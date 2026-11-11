// ============================================================
// Neo4j Cypher Export for Community Menu Database (เมนูชุมชน)
// Compatible with Neo4j 5.x / AuraDB / Neo4j Desktop
// ============================================================

// 1. Constraints
CREATE CONSTRAINT IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.code IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Menu) REQUIRE m.code IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (f:Farmer) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (l:Lot) REQUIRE l.id IS UNIQUE;

// 2. Ingredients (วัตถุดิบ 20 รายการ)
MERGE (:Ingredient {code: 'I01', name: 'ฟักทอง', unit: 'กรัม', min_stock: 1000.0, shelf_days: 10});
MERGE (:Ingredient {code: 'I02', name: 'ไข่ไก่', unit: 'ฟอง', min_stock: 30.0, shelf_days: 14});
MERGE (:Ingredient {code: 'I03', name: 'กระเทียม', unit: 'กรัม', min_stock: 200.0, shelf_days: 30});
MERGE (:Ingredient {code: 'I04', name: 'น้ำมันพืช', unit: 'กรัม', min_stock: 500.0, shelf_days: 180});
MERGE (:Ingredient {code: 'I05', name: 'ซอสหอยนางรม', unit: 'กรัม', min_stock: 300.0, shelf_days: 180});
MERGE (:Ingredient {code: 'I06', name: 'ผักบุ้ง', unit: 'กรัม', min_stock: 500.0, shelf_days: 3});
MERGE (:Ingredient {code: 'I07', name: 'หมูสับ', unit: 'กรัม', min_stock: 500.0, shelf_days: 3});
MERGE (:Ingredient {code: 'I08', name: 'อกไก่', unit: 'กรัม', min_stock: 500.0, shelf_days: 3});
MERGE (:Ingredient {code: 'I09', name: 'ข้าวสาร', unit: 'กรัม', min_stock: 5000.0, shelf_days: 180});
MERGE (:Ingredient {code: 'I10', name: 'ใบกะเพรา', unit: 'กรัม', min_stock: 100.0, shelf_days: 3});
MERGE (:Ingredient {code: 'I11', name: 'พริกขี้หนู', unit: 'กรัม', min_stock: 100.0, shelf_days: 7});
MERGE (:Ingredient {code: 'I12', name: 'คะน้า', unit: 'กรัม', min_stock: 500.0, shelf_days: 4});
MERGE (:Ingredient {code: 'I13', name: 'มะเขือเทศ', unit: 'กรัม', min_stock: 300.0, shelf_days: 7});
MERGE (:Ingredient {code: 'I14', name: 'หอมหัวใหญ่', unit: 'กรัม', min_stock: 300.0, shelf_days: 20});
MERGE (:Ingredient {code: 'I15', name: 'เต้าหู้ไข่', unit: 'ชิ้น', min_stock: 10.0, shelf_days: 7});
MERGE (:Ingredient {code: 'I16', name: 'ถั่วฝักยาว', unit: 'กรัม', min_stock: 300.0, shelf_days: 5});
MERGE (:Ingredient {code: 'I17', name: 'ตำลึง', unit: 'กรัม', min_stock: 200.0, shelf_days: 3});
MERGE (:Ingredient {code: 'I18', name: 'น้ำปลา', unit: 'กรัม', min_stock: 300.0, shelf_days: 365});
MERGE (:Ingredient {code: 'I19', name: 'น้ำตาลทราย', unit: 'กรัม', min_stock: 300.0, shelf_days: 365});
MERGE (:Ingredient {code: 'I20', name: 'แตงกวา', unit: 'กรัม', min_stock: 300.0, shelf_days: 5});

// 3. Menus (เมนู 10 รายการ)
MERGE (:Menu {code: 'M01', name: 'ฟักทองผัดไข่'});
MERGE (:Menu {code: 'M02', name: 'ผัดผักบุ้งไฟแดง'});
MERGE (:Menu {code: 'M03', name: 'ข้าวกะเพราหมูสับ'});
MERGE (:Menu {code: 'M04', name: 'ไข่เจียวหมูสับ'});
MERGE (:Menu {code: 'M05', name: 'ผัดคะน้าหมูสับ'});
MERGE (:Menu {code: 'M06', name: 'ไก่ผัดมะเขือเทศ'});
MERGE (:Menu {code: 'M07', name: 'แกงจืดเต้าหู้หมูสับ'});
MERGE (:Menu {code: 'M08', name: 'ผัดถั่วฝักยาวหมูสับ'});
MERGE (:Menu {code: 'M09', name: 'ไข่ผัดมะเขือเทศ'});
MERGE (:Menu {code: 'M10', name: 'แกงจืดฟักทองหมูสับ'});

// 4. Recipes Relationships (:Menu)-[:REQUIRES {qty_per_dish}]->(:Ingredient)
MATCH (m:Menu {code: 'M01'}), (i:Ingredient {code: 'I01'}) MERGE (m)-[:REQUIRES {qty_per_dish: 100.0}]->(i);
MATCH (m:Menu {code: 'M01'}), (i:Ingredient {code: 'I02'}) MERGE (m)-[:REQUIRES {qty_per_dish: 1.0}]->(i);
MATCH (m:Menu {code: 'M01'}), (i:Ingredient {code: 'I03'}) MERGE (m)-[:REQUIRES {qty_per_dish: 5.0}]->(i);
MATCH (m:Menu {code: 'M01'}), (i:Ingredient {code: 'I04'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);
MATCH (m:Menu {code: 'M01'}), (i:Ingredient {code: 'I05'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);

MATCH (m:Menu {code: 'M02'}), (i:Ingredient {code: 'I06'}) MERGE (m)-[:REQUIRES {qty_per_dish: 150.0}]->(i);
MATCH (m:Menu {code: 'M02'}), (i:Ingredient {code: 'I03'}) MERGE (m)-[:REQUIRES {qty_per_dish: 5.0}]->(i);
MATCH (m:Menu {code: 'M02'}), (i:Ingredient {code: 'I11'}) MERGE (m)-[:REQUIRES {qty_per_dish: 3.0}]->(i);
MATCH (m:Menu {code: 'M02'}), (i:Ingredient {code: 'I04'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);
MATCH (m:Menu {code: 'M02'}), (i:Ingredient {code: 'I05'}) MERGE (m)-[:REQUIRES {qty_per_dish: 15.0}]->(i);

MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I07'}) MERGE (m)-[:REQUIRES {qty_per_dish: 100.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I10'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I11'}) MERGE (m)-[:REQUIRES {qty_per_dish: 5.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I03'}) MERGE (m)-[:REQUIRES {qty_per_dish: 5.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I09'}) MERGE (m)-[:REQUIRES {qty_per_dish: 120.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I04'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);
MATCH (m:Menu {code: 'M03'}), (i:Ingredient {code: 'I18'}) MERGE (m)-[:REQUIRES {qty_per_dish: 10.0}]->(i);

// 5. Farmers (เกษตรกร 5 ราย)
MERGE (:Farmer {id: 1, name: 'กลุ่มเกษตรกรบ้านหนองบัว (จำลอง)', area: 'ต.หนองบัว', contact: '081-000-0001'});
MERGE (:Farmer {id: 2, name: 'ฟาร์มไข่ลุงชัย (จำลอง)', area: 'ต.ท่าช้าง', contact: '081-000-0002'});
MERGE (:Farmer {id: 3, name: 'สวนผักป้าแดง (จำลอง)', area: 'ต.บ้านใหม่', contact: '081-000-0003'});
MERGE (:Farmer {id: 4, name: 'วิสาหกิจชุมชนผักปลอดภัย (จำลอง)', area: 'ต.โนนสูง', contact: '081-000-0004'});
MERGE (:Farmer {id: 5, name: 'ฟาร์มหมูพี่เอก (จำลอง)', area: 'ต.หนองบัว', contact: '081-000-0005'});

// 6. Community Produce (:Farmer)-[:SELLS {price, sell_unit, qty_available}]->(:Ingredient)
MATCH (f:Farmer {id: 1}), (i:Ingredient {code: 'I01'}) MERGE (f)-[:SELLS {price: 30.0, sell_unit: 'กก.', qty_available: 50.0}]->(i);
MATCH (f:Farmer {id: 3}), (i:Ingredient {code: 'I01'}) MERGE (f)-[:SELLS {price: 35.0, sell_unit: 'กก.', qty_available: 20.0}]->(i);
MATCH (f:Farmer {id: 2}), (i:Ingredient {code: 'I02'}) MERGE (f)-[:SELLS {price: 5.0, sell_unit: 'ฟอง', qty_available: 300.0}]->(i);
MATCH (f:Farmer {id: 4}), (i:Ingredient {code: 'I02'}) MERGE (f)-[:SELLS {price: 5.5, sell_unit: 'ฟอง', qty_available: 200.0}]->(i);
MATCH (f:Farmer {id: 3}), (i:Ingredient {code: 'I06'}) MERGE (f)-[:SELLS {price: 30.0, sell_unit: 'กก.', qty_available: 15.0}]->(i);
MATCH (f:Farmer {id: 3}), (i:Ingredient {code: 'I12'}) MERGE (f)-[:SELLS {price: 40.0, sell_unit: 'กก.', qty_available: 10.0}]->(i);
MATCH (f:Farmer {id: 4}), (i:Ingredient {code: 'I16'}) MERGE (f)-[:SELLS {price: 40.0, sell_unit: 'กก.', qty_available: 10.0}]->(i);
MATCH (f:Farmer {id: 5}), (i:Ingredient {code: 'I07'}) MERGE (f)-[:SELLS {price: 140.0, sell_unit: 'กก.', qty_available: 30.0}]->(i);

// 7. Initial Inventory Batches (:Lot)-[:BATCH_OF]->(:Ingredient)
MATCH (i:Ingredient {code: 'I01'}) MERGE (:Lot {id: 1, received_date: '2026-10-18', use_by: '2026-11-20', qty_left: 2000.0, unit_cost: 0.03})-[:BATCH_OF]->(i);
MATCH (i:Ingredient {code: 'I02'}) MERGE (:Lot {id: 2, received_date: '2026-10-21', use_by: '2026-11-25', qty_left: 20.0, unit_cost: 5.0})-[:BATCH_OF]->(i);
MATCH (i:Ingredient {code: 'I03'}) MERGE (:Lot {id: 3, received_date: '2026-10-14', use_by: '2026-12-01', qty_left: 1000.0, unit_cost: 0.08})-[:BATCH_OF]->(i);
MATCH (i:Ingredient {code: 'I04'}) MERGE (:Lot {id: 4, received_date: '2026-10-04', use_by: '2027-03-23', qty_left: 3000.0, unit_cost: 0.05})-[:BATCH_OF]->(i);
MATCH (i:Ingredient {code: 'I05'}) MERGE (:Lot {id: 5, received_date: '2026-10-04', use_by: '2027-03-23', qty_left: 2000.0, unit_cost: 0.09})-[:BATCH_OF]->(i);
