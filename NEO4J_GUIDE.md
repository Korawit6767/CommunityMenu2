# คู่มือการใช้งานและเชื่อมต่อ Neo4j Graph Database
สำหรับระบบ **เมนูชุมชน (Community Menu Planner)**

---

## 1. บทนำ (Overview)

ระบบเมนูชุมชนรองรับการจัดเก็บและวิเคราะห์ข้อมูลแบบ **Graph Database (Neo4j)** นอกเหนือจาก Relational Database (SQLite / MySQL) เพื่อเพิ่มประสิทธิภาพในการ:
- คำนวณห่วงโซ่อุปทาน (Supply Chain Traversal) ระหว่าง **เมนู -> วัตถุดิบ -> เกษตรกร**
- ค้นหาเกษตรกรที่ให้ราคาและระยะเวลาพร้อมส่งดีที่สุด (Shortest Path / Lowest Cost Traversal)
- ตรวจสอบล็อตสินค้าที่หมดอายุและความเชื่อมโยงกับเมนูที่วางแผนไว้

---

## 2. โครงสร้าง Graph Model (Nodes & Relationships)

### Nodes (โหนด)
- `(:Ingredient)`: วัตถุดิบ (Properties: `code`, `name`, `unit`, `min_stock`, `shelf_days`)
- `(:Menu)`: รายการอาหาร (Properties: `code`, `name`)
- `(:Farmer)`: เกษตรกรในชุมชน (Properties: `id`, `name`, `area`, `contact`)
- `(:Lot)`: ล็อตวัตถุดิบในคลัง (Properties: `id`, `received_date`, `use_by`, `qty_left`, `unit_cost`)
- `(:MenuPlan)`: แผนเมนูอาหาร (Properties: `id`, `plan_date`, `budget`, `status`)
- `(:PurchaseOrder)`: ใบสั่งซื้อผลผลิต (Properties: `id`, `created_at`, `status`)

### Relationships (ความสัมพันธ์)
- `(:Menu)-[:REQUIRES {qty_per_dish}]->(:Ingredient)`: เมนูต้องการวัตถุดิบ
- `(:Farmer)-[:SELLS {price, sell_unit, qty_available, ready_date}]->(:Ingredient)`: เกษตรกรจำหน่ายวัตถุดิบ
- `(:Lot)-[:BATCH_OF]->(:Ingredient)`: ล็อตสินค้าของวัตถุดิบชนิดนี้
- `(:MenuPlan)-[:INCLUDES {dishes}]->(:Menu)`: แผนการประกอบอาหารบรรจุเมนู
- `(:PurchaseOrder)-[:ORDERED_FROM]->(:Farmer)`: ใบสั่งซื้อส่งตรงถึงเกษตรกร

---

## 3. ตัวเลือกการติดตั้งและเชื่อมต่อ

### ตัวเลือกที่ 1: ใช้งานผ่าน Neo4j AuraDB (Cloud Free Tier) - แนะนำ
1. สมัครใช้งานฟรีที่ [https://neo4j.com/cloud/platform/aura-graph-database/](https://neo4j.com/cloud/platform/aura-graph-database/)
2. สร้าง Instance ฟรี (Free Tier) จะได้รับ `Connection URI`, `Username`, `Password`
3. ตั้งค่า Environment Variables ก่อนรันโปรแกรม:
   ```cmd
   set NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
   set NEO4J_USER=neo4j
   set NEO4J_PASSWORD=your_aura_password
   set DB_ENGINE=neo4j
   ```
4. รันคำสั่ง seed ข้อมูลเข้า Cloud:
   ```cmd
   python neo4j_adapter.py
   ```

### ตัวเลือกที่ 2: ติดตั้ง Neo4j Desktop หรือ Docker ในเครื่อง
- **Neo4j Desktop:** ดาวน์โหลดจาก [neo4j.com/download](https://neo4j.com/download/) สร้าง Project และ Database พอร์ตมาตรฐาน `bolt://localhost:7687`
- นำเข้าข้อมูลโดยเปิด **Neo4j Browser** แล้วนำเนื้อหาในไฟล์ `neo4j_export_data.cypher` ไปวางแล้วกด Run

---

## 4. ไฟล์ที่เกี่ยวข้องในโปรเจกต์
- `neo4j_adapter.py`: Adapter จัดการ Driver, Connection, Graph Seed และ Cypher Queries
- `neo4j_export_data.cypher`: สคริปต์ Cypher สำหรับ Import ข้อมูลเข้าฐานข้อมูล Neo4j ทันที
- `logic.py`: ฟังก์ชันวิเคราะห์เชิงกราฟ `get_graph_recipe_and_supplier()` และ `get_graph_expiring_lots()` พร้อม Fallback อัตโนมัติหากเซิร์ฟเวอร์ยังไม่ออนไลน์
