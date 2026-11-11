# test_logic.py
# ชุดทดสอบ Unit & Integration Test สำหรับ logic.py และ db.py
# รัน: python -m unittest test_logic.py

import os
import unittest
from datetime import date, timedelta

# กำหนดให้ใช้ in-memory หรือ test database เพื่อไม่กระทบข้อมูลหลัก
os.environ["DB_FILE"] = "test_community_menu.db"
os.environ["DB_ENGINE"] = "sqlite"

import db
import logic
import ai_helper


class TestUnitConversions(unittest.TestCase):
    """ทดสอบการแปลงหน่วยและการจัดรูปแบบข้อความ"""

    def test_same_unit(self):
        self.assertEqual(logic.to_std(500, "กรัม", "กรัม"), 500)
        self.assertEqual(logic.to_std(10, "ฟอง", "ฟอง"), 10)

    def test_kg_to_gram(self):
        self.assertEqual(logic.to_std(2.5, "กก.", "กรัม"), 2500)
        self.assertEqual(logic.to_std(1, "กก.", "กรัม"), 1000)

    def test_gram_to_kg(self):
        self.assertEqual(logic.to_std(3500, "กรัม", "กก."), 3.5)

    def test_invalid_conversion_raises(self):
        with self.assertRaises(logic.AppError):
            logic.to_std(5, "กก.", "ฟอง")
        with self.assertRaises(logic.AppError):
            logic.to_std(10, "ชิ้น", "กรัม")

    def test_fmt_qty(self):
        self.assertEqual(logic.fmt_qty(1000, "กรัม"), "1 กก.")
        self.assertEqual(logic.fmt_qty(2500, "กรัม"), "2.5 กก.")
        self.assertEqual(logic.fmt_qty(500, "กรัม"), "500 กรัม")
        self.assertEqual(logic.fmt_qty(12, "ฟอง"), "12 ฟอง")


class TestDatabaseAndLogic(unittest.TestCase):
    """ทดสอบการทำงานของฐานข้อมูลและกฎธุรกิจ (FIFO, การคำนวณ, การตัดสต็อก)"""

    @classmethod
    def setUpClass(cls):
        # ลบ test database เก่าถ้ามี แล้วสร้างใหม่
        if os.path.exists("test_community_menu.db"):
            try:
                os.remove("test_community_menu.db")
            except Exception:
                pass
        db.create_tables()
        db.seed_demo_data()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists("test_community_menu.db"):
            try:
                os.remove("test_community_menu.db")
            except Exception:
                pass

    def test_seed_counts(self):
        """ตรวจสอบความครบถ้วนของข้อมูลจำลองเริ่มต้น"""
        ings = logic.list_ingredients()
        self.assertEqual(len(ings), 20)

        menus = logic.list_menus()
        self.assertEqual(len(menus), 10)

        farmers = logic.list_farmers()
        self.assertEqual(len(farmers), 5)

    def test_usable_stock(self):
        """ตรวจสอบการนับยอดคงเหลือที่ยังไม่หมดอายุ"""
        conn = db.get_conn()
        try:
            # ฟักทอง (id=1) มีล็อตคงเหลือ 2000 กรัม
            stock = logic.usable_stock(conn, 1)
            self.assertEqual(stock, 2000)
        finally:
            conn.close()

    def test_calc_plan_pumpkin_dish(self):
        """ตรวจสอบตัวอย่างสาธิตใน PROJECT.md: ฟักทองผัดไข่ 30 จาน -> ยอดซื้อเพิ่ม 80 บาท"""
        # Menu 1 = ฟักทองผัดไข่
        lines, summary = logic.calc_plan([(1, 30)])
        self.assertEqual(summary["buy_cost"], 80.0)

        line_map = {l["name"]: l for l in lines}
        self.assertIn("ฟักทอง", line_map)
        self.assertIn("ไข่ไก่", line_map)

        # ฟักทอง: ต้องใช้ 3000g, มี 2000g, ซื้อเพิ่ม 1000g
        self.assertEqual(line_map["ฟักทอง"]["need"], 3000)
        self.assertEqual(line_map["ฟักทอง"]["have"], 2000)
        self.assertEqual(line_map["ฟักทอง"]["buy"], 1000)

        # ไข่ไก่: ต้องใช้ 30, มี 20, ซื้อเพิ่ม 10
        self.assertEqual(line_map["ไข่ไก่"]["need"], 30)
        self.assertEqual(line_map["ไข่ไก่"]["have"], 20)
        self.assertEqual(line_map["ไข่ไก่"]["buy"], 10)

    def test_suggest_lots_fifo(self):
        """ตรวจสอบว่าระบบเสนอล็อตที่หมดอายุก่อนเสมอ (FIFO)"""
        conn = db.get_conn()
        try:
            # ฟักทองมี 2000g ในล็อตแรก ขอเบิก 500g
            plan = logic.suggest_lots(conn, 1, 500)
            self.assertEqual(len(plan), 1)
            lot, take = plan[0]
            self.assertEqual(take, 500)
        finally:
            conn.close()

    def test_prevent_negative_stock(self):
        """ตรวจสอบการป้องกันยอดติดลบ (ถ้าขอเบิกเกินสต็อกที่มี ต้อง raise AppError)"""
        conn = db.get_conn()
        try:
            # ขอเบิกฟักทอง 99999 กรัม (มีแค่ 2000)
            with self.assertRaises(logic.AppError):
                logic.suggest_lots(conn, 1, 99999)
        finally:
            conn.close()

    def test_adjust_lot_requires_reason(self):
        """การปรับยอดสต็อกต้องระบุเหตุผลเสมอ"""
        with self.assertRaises(logic.AppError):
            logic.adjust_lot(1, 1500, "")

    def test_purchase_order_lifecycle(self):
        """ทดสอบวงจรชีวิตคำสั่งซื้อ: สร้าง PO -> รับสินค้า -> สร้างล็อตใหม่เข้าคลัง"""
        # สร้าง PO ซื้อไข่ไก่ 50 ฟอง ราคา 5 บาท/ฟอง จากเกษตรกร 2
        po_id = logic.create_po(2, [(2, 50, 5.0)])
        self.assertIsNotNone(po_id)

        # ตรวจสอบสถานะก่อนรับ
        pos = logic.list_pos("PENDING")
        matching = [p for p in pos if p["id"] == po_id]
        self.assertEqual(len(matching), 1)

        # รับสินค้า
        logic.receive_po(po_id)

        # ตรวจสอบว่ารับซ้ำไม่ได้
        with self.assertRaises(logic.AppError):
            logic.receive_po(po_id)


class TestAIHelper(unittest.TestCase):
    """ทดสอบการทำงานของ ai_helper: การเตรียมข้อมูล prompt และการตรวจสอบคำตอบ"""

    @classmethod
    def setUpClass(cls):
        db.create_tables()
        if db.is_empty():
            db.seed_demo_data()

    def test_build_prompt_data(self):
        """ตรวจสอบการรวบรวมข้อมูลเพื่อส่งให้ AI (ตัดเมนูที่ exclude ออก)"""
        data = ai_helper.build_prompt_data(100, 30, ["M01"])
        self.assertNotIn("M01", [m["code"] for m in data["menus"]])
        self.assertEqual(data["extra_budget_baht"], 100)
        self.assertEqual(data["dishes_per_menu"], 30)
        self.assertTrue(len(data["stock"]) > 0)
        self.assertTrue(len(data["community_produce"]) > 0)

    def test_check_answer_valid_and_filters_invalid(self):
        """ตรวจสอบการ parse คำตอบ AI และกรองรหัสเมนูที่ไม่มีจริงทิ้ง"""
        raw_json = (
            '{"recommendations": ['
            '{"menu_code": "M01", "reason": "ใช้ฟักทองใกล้หมดอายุ"},'
            '{"menu_code": "M02", "reason": "ผัดผักบุ้งไฟแดงวัตถุดิบครบ"},'
            '{"menu_code": "NON_EXISTENT", "reason": "เมนูที่ไม่มีจริง"},'
            '{"menu_code": "M01", "reason": "รหัสซ้ำ"}'
            ']}'
        )
        recs = ai_helper.check_answer(raw_json)
        self.assertEqual(len(recs), 2)
        codes = [m["code"] for m, _ in recs]
        self.assertEqual(codes, ["M01", "M02"])

    def test_check_answer_malformed_json_raises(self):
        """ถ้า AI ตอบกลับเป็นข้อความที่ไม่ใช่ JSON หรือ schema ผิด ต้อง raise AppError"""
        with self.assertRaises(logic.AppError):
            ai_helper.check_answer("Not a json string")
        with self.assertRaises(logic.AppError):
            ai_helper.check_answer('{"other_key": 123}')

    def test_ask_ai_without_key_raises_apperror(self):
        """ถ้าไม่มี API key ต้องแจ้งเตือน AppError อย่างสุภาพให้เลือกเมนูเองได้ตามปกติ"""
        orig_key = os.environ.get("GEMINI_API_KEY", "")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        try:
            with self.assertRaises(logic.AppError) as ctx:
                ai_helper.ask_ai(100, 30, [])
            self.assertIn("เลือกเมนูเองได้ตามปกติ", str(ctx.exception))
        finally:
            if orig_key:
                os.environ["GEMINI_API_KEY"] = orig_key


class TestEndToEndWorkflow(unittest.TestCase):
    """ทดสอบวงจรการทำงานแบบครบวงจร (End-to-End User Journey ตาม PROJECT.md หัวข้อ 4.9)
    1. ตรวจสอบคลังและล็อตเริ่มต้น
    2. คำนวณแผนเมนูฟักทองผัดไข่ 30 จาน
    3. ยืนยันแผนและสร้างใบสั่งซื้อ (PO) อัตโนมัติแยกตามเกษตรกร
    4. บันทึกรับสินค้าเข้าคลังเป็นล็อตใหม่
    5. ยืนยันเบิกวัตถุดิบตามแผน (ตัดตามล็อต FIFO)
    6. ตรวจสอบรายงานสรุปยอดจัดซื้อและประวัติการเคลื่อนไหว
    7. ป้องกันการเบิกซ้ำ"""

    @classmethod
    def setUpClass(cls):
        # สร้างฐานข้อมูลแยกเฉพาะสำหรับ E2E test
        cls.db_name = "test_e2e_community_menu.db"
        if os.path.exists(cls.db_name):
            try:
                os.remove(cls.db_name)
            except Exception:
                pass
        os.environ["DB_FILE"] = cls.db_name
        db.create_tables()
        db.seed_demo_data()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_name):
            try:
                os.remove(cls.db_name)
            except Exception:
                pass

    def test_full_demo_lifecycle(self):
        conn = db.get_conn()
        try:
            # 1. ตรวจสอบสต็อกเริ่มต้น: ฟักทอง 2000g, ไข่ไก่ 20 ฟอง
            pumpkin_init = logic.usable_stock(conn, 1)
            egg_init = logic.usable_stock(conn, 2)
            self.assertEqual(pumpkin_init, 2000)
            self.assertEqual(egg_init, 20)

            # 2. คำนวณแผนเมนูฟักทองผัดไข่ 30 จาน (Menu id=1)
            lines, summary = logic.calc_plan([(1, 30)])
            self.assertEqual(summary["buy_cost"], 80.0)

            # 3. ยืนยันแผนและสร้าง PO
            plan_id = logic.create_plan([(1, 30)], budget=100)
            self.assertIsNotNone(plan_id)
            po_ids = logic.create_po_from_plan(lines, plan_id)
            self.assertTrue(len(po_ids) > 0)

            # 4. ตรวจสอบสถานะ PO และรับสินค้าเข้าคลัง
            for poid in po_ids:
                logic.receive_po(poid)

            # ตรวจสอบว่าสต็อกเพิ่มขึ้นหลังรับสินค้า (ฟักทอง 3000g, ไข่ไก่ 30 ฟอง)
            self.assertEqual(logic.usable_stock(conn, 1), 3000)
            self.assertEqual(logic.usable_stock(conn, 2), 30)

            # 5. ยืนยันเบิกวัตถุดิบตามแผน
            logic.use_plan(plan_id)

            # ตรวจสอบว่าสต็อกถูกตัดหมดพอดี (ฟักทองเหลือ 0g, ไข่ไก่เหลือ 0 ฟอง)
            self.assertEqual(logic.usable_stock(conn, 1), 0)
            self.assertEqual(logic.usable_stock(conn, 2), 0)

            # 6. ป้องกันเบิกซ้ำ
            with self.assertRaises(logic.AppError):
                logic.use_plan(plan_id)

            # 7. ตรวจสอบรายงาน
            t_str = db.today_str()
            buy_rep, move_rep = logic.report(t_str, t_str)
            self.assertTrue(len(buy_rep) > 0)
            self.assertTrue(len(move_rep) > 0)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
