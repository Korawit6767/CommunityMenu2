# neo4j_adapter.py
# ระบบเชื่อมต่อและจัดการฐานข้อมูล Graph Database (Neo4j) สำหรับเมนูชุมชน
# แปลงโครงสร้างข้อมูลร้านอาหารเป็น Graph Model (Nodes & Relationships)

import os
from datetime import date, datetime, timedelta

try:
    from neo4j import GraphDatabase, exceptions as neo4j_exceptions
    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False

# ---------- Neo4j Configuration ----------
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def is_neo4j_available():
    """ตรวจสอบว่าติดตั้ง neo4j library และสามารถเชื่อมต่อเซิร์ฟเวอร์ได้หรือไม่"""
    if not HAS_NEO4J_DRIVER:
        return False
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        driver.close()
        return True
    except Exception:
        return False


def get_driver():
    """สร้าง Neo4j driver สำหรับ execute Cypher queries"""
    if not HAS_NEO4J_DRIVER:
        raise RuntimeError("กรุณาติดตั้ง neo4j driver ก่อน: pip install neo4j")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# ---------- Graph Constraints & Indexes ----------
CYPHER_CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.code IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Menu) REQUIRE m.code IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Farmer) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Lot) REQUIRE l.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:MenuPlan) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (po:PurchaseOrder) REQUIRE po.id IS UNIQUE",
]


def init_neo4j_schema(driver):
    """สร้าง Unique Constraints และ Indexes ใน Neo4j"""
    with driver.session() as session:
        for c in CYPHER_CONSTRAINTS:
            try:
                session.run(c)
            except Exception as e:
                print(f"[Neo4j] Constraint warning: {e}")


def seed_neo4j_graph(driver):
    """แปลงข้อมูลจำลองเริ่มต้นเป็น Node และ Relationship บน Neo4j"""
    t = date.today()

    def d(days):
        return (t + timedelta(days=days)).isoformat()

    with driver.session() as session:
        # 1. วัตถุดิบ (Ingredient Nodes)
        ingredients = [
            ("I01", "ฟักทอง", "กรัม", 1000.0, 10),
            ("I02", "ไข่ไก่", "ฟอง", 30.0, 14),
            ("I03", "กระเทียม", "กรัม", 200.0, 30),
            ("I04", "น้ำมันพืช", "กรัม", 500.0, 180),
            ("I05", "ซอสหอยนางรม", "กรัม", 300.0, 180),
            ("I06", "ผักบุ้ง", "กรัม", 500.0, 3),
            ("I07", "หมูสับ", "กรัม", 500.0, 3),
            ("I08", "อกไก่", "กรัม", 500.0, 3),
            ("I09", "ข้าวสาร", "กรัม", 5000.0, 180),
            ("I10", "ใบกะเพรา", "กรัม", 100.0, 3),
            ("I11", "พริกขี้หนู", "กรัม", 100.0, 7),
            ("I12", "คะน้า", "กรัม", 500.0, 4),
            ("I13", "มะเขือเทศ", "กรัม", 300.0, 7),
            ("I14", "หอมหัวใหญ่", "กรัม", 300.0, 20),
            ("I15", "เต้าหู้ไข่", "ชิ้น", 10.0, 7),
            ("I16", "ถั่วฝักยาว", "กรัม", 300.0, 5),
            ("I17", "ตำลึง", "กรัม", 200.0, 3),
            ("I18", "น้ำปลา", "กรัม", 300.0, 365),
            ("I19", "น้ำตาลทราย", "กรัม", 300.0, 365),
            ("I20", "แตงกวา", "กรัม", 300.0, 5),
        ]
        for code, name, unit, min_stock, shelf in ingredients:
            session.run("""
                MERGE (i:Ingredient {code: $code})
                SET i.name = $name, i.unit = $unit, i.min_stock = $min_stock, i.shelf_days = $shelf
            """, code=code, name=name, unit=unit, min_stock=min_stock, shelf=shelf)

        # 2. เมนูและสูตรอาหาร (Menu Nodes & REQUIRES Relationships)
        menus = {
            ("M01", "ฟักทองผัดไข่"): [("I01", 100), ("I02", 1), ("I03", 5), ("I04", 10), ("I05", 10)],
            ("M02", "ผัดผักบุ้งไฟแดง"): [("I06", 150), ("I03", 5), ("I11", 3), ("I04", 10), ("I05", 15)],
            ("M03", "ข้าวกะเพราหมูสับ"): [("I07", 100), ("I10", 10), ("I11", 5), ("I03", 5), ("I09", 120), ("I04", 10), ("I18", 10)],
            ("M04", "ไข่เจียวหมูสับ"): [("I02", 2), ("I07", 40), ("I04", 30), ("I18", 5)],
            ("M05", "ผัดคะน้าหมูสับ"): [("I12", 150), ("I07", 60), ("I03", 5), ("I05", 15), ("I04", 10)],
            ("M06", "ไก่ผัดมะเขือเทศ"): [("I08", 100), ("I13", 80), ("I14", 40), ("I04", 10), ("I19", 5)],
            ("M07", "แกงจืดเต้าหู้หมูสับ"): [("I15", 1), ("I07", 50), ("I17", 30), ("I18", 10)],
            ("M08", "ผัดถั่วฝักยาวหมูสับ"): [("I16", 120), ("I07", 50), ("I03", 5), ("I18", 10), ("I04", 10)],
            ("M09", "ไข่ผัดมะเขือเทศ"): [("I02", 2), ("I13", 100), ("I14", 30), ("I04", 10), ("I19", 5)],
            ("M10", "แกงจืดฟักทองหมูสับ"): [("I01", 120), ("I07", 50), ("I18", 10)],
        }
        for (mcode, mname), items in menus.items():
            session.run("""
                MERGE (m:Menu {code: $mcode})
                SET m.name = $mname
            """, mcode=mcode, mname=mname)
            for icode, qty in items:
                session.run("""
                    MATCH (m:Menu {code: $mcode})
                    MATCH (i:Ingredient {code: $icode})
                    MERGE (m)-[r:REQUIRES]->(i)
                    SET r.qty_per_dish = $qty
                """, mcode=mcode, icode=icode, qty=qty)

        # 3. เกษตรกรและผลผลิต (Farmer Nodes & SELLS Relationships)
        farmers = [
            (1, "กลุ่มเกษตรกรบ้านหนองบัว (จำลอง)", "ต.หนองบัว", "081-000-0001"),
            (2, "ฟาร์มไข่ลุงชัย (จำลอง)", "ต.ท่าช้าง", "081-000-0002"),
            (3, "สวนผักป้าแดง (จำลอง)", "ต.บ้านใหม่", "081-000-0003"),
            (4, "วิสาหกิจชุมชนผักปลอดภัย (จำลอง)", "ต.โนนสูง", "081-000-0004"),
            (5, "ฟาร์มหมูพี่เอก (จำลอง)", "ต.หนองบัว", "081-000-0005"),
        ]
        for fid, name, area, contact in farmers:
            session.run("""
                MERGE (f:Farmer {id: $fid})
                SET f.name = $name, f.area = $area, f.contact = $contact
            """, fid=fid, name=name, area=area, contact=contact)

        produce = [
            (1, "I01", 30, "กก.", 50, 0),
            (3, "I01", 35, "กก.", 20, 1),
            (2, "I02", 5, "ฟอง", 300, 0),
            (4, "I02", 5.5, "ฟอง", 200, 0),
            (3, "I06", 30, "กก.", 15, 0),
            (3, "I12", 40, "กก.", 10, 0),
            (4, "I16", 40, "กก.", 10, 1),
            (4, "I17", 50, "กก.", 5, 0),
            (4, "I13", 40, "กก.", 15, 0),
            (1, "I20", 25, "กก.", 20, 0),
            (5, "I07", 140, "กก.", 30, 0),
            (1, "I10", 60, "กก.", 3, 0),
        ]
        for fid, icode, price, unit, qty, ready in produce:
            session.run("""
                MATCH (f:Farmer {id: $fid})
                MATCH (i:Ingredient {code: $icode})
                MERGE (f)-[s:SELLS]->(i)
                SET s.price = $price, s.sell_unit = $unit, s.qty_available = $qty, s.ready_date = $ready_date
            """, fid=fid, icode=icode, price=price, unit=unit, qty=qty, ready_date=d(ready))

        # 4. ล็อตวัตถุดิบ (Lot Nodes & BATCH_OF Relationships)
        lots = [
            (1, "I01", -6, 2, 2000, 0.03),
            (2, "I02", -3, 10, 20, 5.0),
            (3, "I03", -10, 20, 1000, 0.08),
            (4, "I04", -20, 150, 3000, 0.05),
            (5, "I05", -20, 150, 2000, 0.09),
        ]
        for lid, icode, recv, useby, qty, cost in lots:
            session.run("""
                MATCH (i:Ingredient {code: $icode})
                MERGE (l:Lot {id: $lid})
                SET l.received_date = $recv, l.use_by = $useby, l.qty_left = $qty, l.unit_cost = $cost
                MERGE (l)-[:BATCH_OF]->(i)
            """, lid=lid, icode=icode, recv=d(recv), useby=d(useby), qty=qty, cost=cost)


# ---------- Graph Queries (Cypher API) ----------
def query_menu_ingredients_graph(driver, menu_code):
    """Cypher Query: ดึงวัตถุดิบทั้งหมดที่เมนูต้องใช้ พร้อมฟาร์มที่ขายถูกที่สุด"""
    query = """
        MATCH (m:Menu {code: $code})-[r:REQUIRES]->(i:Ingredient)
        OPTIONAL MATCH (f:Farmer)-[s:SELLS]->(i)
        WITH m, i, r, f, s
        ORDER BY s.price ASC
        RETURN i.code AS ingredient_code,
               i.name AS ingredient_name,
               r.qty_per_dish AS qty_per_dish,
               i.unit AS unit,
               collect({farmer: f.name, price: s.price, ready_date: s.ready_date})[0] AS best_supplier
    """
    with driver.session() as session:
        result = session.run(query, code=menu_code)
        return [dict(record) for record in result]


def query_expiring_lots_graph(driver, days_threshold=2):
    """Cypher Query: หา Lot ที่ใกล้หมดอายุพร้อมชื่อวัตถุดิบ"""
    target_date = (date.today() + timedelta(days=days_threshold)).isoformat()
    query = """
        MATCH (l:Lot)-[:BATCH_OF]->(i:Ingredient)
        WHERE l.qty_left > 0 AND l.use_by <= $target_date
        RETURN l.id AS lot_id, i.name AS ingredient, l.qty_left AS qty_left, i.unit AS unit, l.use_by AS use_by
        ORDER BY l.use_by ASC
    """
    with driver.session() as session:
        result = session.run(query, target_date=target_date)
        return [dict(record) for record in result]


if __name__ == "__main__":
    print(f"Neo4j Driver Installed: {HAS_NEO4J_DRIVER}")
    print(f"Neo4j Server Connected: {is_neo4j_available()}")
    if is_neo4j_available():
        d = get_driver()
        init_neo4j_schema(d)
        seed_neo4j_graph(d)
        print("Neo4j Graph Database initialized and seeded successfully!")
        d.close()
    else:
        print("Neo4j Server is offline or not configured yet.")
