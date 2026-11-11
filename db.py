# db.py
# จัดการฐานข้อมูล: รองรับทั้ง SQLite (Local Default) และ MySQL (Networked)
# มอบ Universal Connection Wrapper ให้ logic.py และหน้าจอใช้งานได้อย่างราบรื่น

import os
import sys
import sqlite3
from datetime import date, datetime, timedelta

# ---------- Engine Selection & Config ----------
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()
DB_FILE = os.getenv("DB_FILE", "community_menu.db")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "menu_user"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "database": os.getenv("DB_NAME", "community_menu"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": False,
    "use_pure": True,
}

# ตรวจสอบว่า mysql.connector ใช้งานได้หรือไม่
HAS_MYSQL = False
try:
    import mysql.connector
    from mysql.connector import errorcode
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False


# ---------- Helpers ----------
def today_str():
    return date.today().isoformat()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------- Schemas ----------
SQLITE_DDL = [
    """CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        unit TEXT NOT NULL,
        min_stock REAL DEFAULT 0,
        shelf_days INTEGER DEFAULT 7
    )""",
    """CREATE TABLE IF NOT EXISTS lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
        received_date TEXT NOT NULL,
        use_by TEXT NOT NULL,
        qty_left REAL NOT NULL,
        unit_cost REAL NOT NULL,
        note TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
        lot_id INTEGER REFERENCES lots(id),
        type TEXT NOT NULL,
        qty REAL NOT NULL,
        unit_cost REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        ref TEXT,
        reason TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS recipe_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
        qty_per_dish REAL NOT NULL,
        UNIQUE (menu_id, ingredient_id)
    )""",
    """CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        area TEXT,
        contact TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS produce (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
        price REAL NOT NULL,
        sell_unit TEXT NOT NULL,
        qty_available REAL NOT NULL,
        ready_date TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS menu_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_date TEXT NOT NULL,
        budget REAL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'DRAFT',
        created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS plan_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER NOT NULL REFERENCES menu_plans(id) ON DELETE CASCADE,
        menu_id INTEGER NOT NULL REFERENCES menus(id),
        dishes INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL REFERENCES farmers(id),
        plan_id INTEGER REFERENCES menu_plans(id),
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        received_at TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS po_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
        ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
        qty REAL NOT NULL,
        unit_price REAL NOT NULL
    )"""
]

MYSQL_DDL = [
    """CREATE TABLE IF NOT EXISTS ingredients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        unit VARCHAR(20) NOT NULL,
        min_stock DECIMAL(10,2) DEFAULT 0,
        shelf_days INT DEFAULT 7
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS lots (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ingredient_id INT NOT NULL,
        received_date DATE NOT NULL,
        use_by DATE NOT NULL,
        qty_left DECIMAL(10,2) NOT NULL,
        unit_cost DECIMAL(10,4) NOT NULL,
        note TEXT,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS movements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ingredient_id INT NOT NULL,
        lot_id INT,
        type ENUM('IN','USE','WASTE','ADJUST') NOT NULL,
        qty DECIMAL(10,2) NOT NULL,
        unit_cost DECIMAL(10,4) DEFAULT 0,
        created_at DATETIME NOT NULL,
        ref VARCHAR(50),
        reason TEXT,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT,
        FOREIGN KEY (lot_id) REFERENCES lots(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS menus (
        id INT AUTO_INCREMENT PRIMARY KEY,
        code VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS recipe_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        menu_id INT NOT NULL,
        ingredient_id INT NOT NULL,
        qty_per_dish DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT,
        UNIQUE KEY uniq_menu_ingredient (menu_id, ingredient_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS farmers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        area VARCHAR(100),
        contact VARCHAR(50)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS produce (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT NOT NULL,
        ingredient_id INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        sell_unit VARCHAR(20) NOT NULL,
        qty_available DECIMAL(10,2) NOT NULL,
        ready_date DATE NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS menu_plans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        plan_date DATE NOT NULL,
        budget DECIMAL(10,2) DEFAULT 0,
        status ENUM('DRAFT','CONFIRMED','USED') NOT NULL DEFAULT 'DRAFT',
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS plan_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        plan_id INT NOT NULL,
        menu_id INT NOT NULL,
        dishes INT NOT NULL,
        FOREIGN KEY (plan_id) REFERENCES menu_plans(id) ON DELETE CASCADE,
        FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS purchase_orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        farmer_id INT NOT NULL,
        plan_id INT,
        created_at DATETIME NOT NULL,
        status ENUM('PENDING','RECEIVED','CANCELLED') NOT NULL DEFAULT 'PENDING',
        received_at DATETIME,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id) ON DELETE RESTRICT,
        FOREIGN KEY (plan_id) REFERENCES menu_plans(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci""",
    """CREATE TABLE IF NOT EXISTS po_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        po_id INT NOT NULL,
        ingredient_id INT NOT NULL,
        qty DECIMAL(10,2) NOT NULL,
        unit_price DECIMAL(10,4) NOT NULL,
        FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
]


# ---------- Connection & Cursor Wrappers ----------
class ManagedCursor:
    """Cursor wrapper ที่รองรับการแปลง placeholder (%s <-> ?) และคืน dict/index access"""
    def __init__(self, raw_cur, is_sqlite=True):
        self._cur = raw_cur
        self.is_sqlite = is_sqlite

    def __getattr__(self, name):
        return getattr(self._cur, name)

    def __iter__(self):
        return iter(self._cur)

    def _normalize_sql(self, sql):
        if self.is_sqlite:
            # แปลง %s เป็น ? สำหรับ SQLite
            return sql.replace("%s", "?")
        else:
            # แปลง ? เป็น %s สำหรับ MySQL
            return sql.replace("?", "%s")

    def execute(self, sql, params=None):
        sql = self._normalize_sql(sql)
        if params is None:
            self._cur.execute(sql)
        else:
            self._cur.execute(sql, params)
        return self

    def executemany(self, sql, seq_of_params):
        sql = self._normalize_sql(sql)
        self._cur.executemany(sql, seq_of_params)
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()


class ManagedConnection:
    """Connection wrapper ที่ใช้ได้ทั้ง direct (conn = get_conn()) และ context manager (with get_conn() as conn:)"""
    def __init__(self, raw_conn, is_sqlite=True):
        self._conn = raw_conn
        self.is_sqlite = is_sqlite
        self._in_context = False

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def cursor(self, *args, **kwargs):
        if self.is_sqlite:
            return ManagedCursor(self._conn.cursor(*args, **kwargs), is_sqlite=True)
        else:
            return ManagedCursor(self._conn.cursor(dictionary=True, *args, **kwargs), is_sqlite=False)

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def executemany(self, sql, seq_of_params):
        cur = self.cursor()
        cur.executemany(sql, seq_of_params)
        return cur

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __enter__(self):
        self._in_context = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
        finally:
            if self._in_context:
                self.close()


def get_conn():
    """เปิด connection ตาม engine ที่พร้อมใช้งาน (SQLite เป็นค่าเริ่มต้น)"""
    # ถ้าตั้งใจใช้ MySQL และมี library + connect ได้
    if DB_ENGINE == "mysql" and HAS_MYSQL:
        try:
            raw_conn = mysql.connector.connect(**DB_CONFIG)
            return ManagedConnection(raw_conn, is_sqlite=False)
        except Exception as e:
            print(f"[db.py] Warning: Could not connect to MySQL ({e}). Falling back to SQLite.")

    # SQLite Local Fallback
    raw_conn = sqlite3.connect(DB_FILE)
    raw_conn.row_factory = sqlite3.Row
    raw_conn.execute("PRAGMA foreign_keys = ON;")
    return ManagedConnection(raw_conn, is_sqlite=True)


def get_cursor(conn):
    """คืน cursor ที่เข้าถึง column ผ่าน dict/index ได้"""
    return conn.cursor()


# ---------- Database Initialization ----------
def create_tables():
    with get_conn() as conn:
        ddls = MYSQL_DDL if not conn.is_sqlite else SQLITE_DDL
        for ddl in ddls:
            conn.execute(ddl)


def is_empty():
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM ingredients")
        row = cur.fetchone()
        return row["cnt"] == 0 if row else True


def seed_demo_data():
    """ใส่ข้อมูลจำลองเริ่มต้น: วัตถุดิบ 20 / สูตร 10 / เกษตรกร 5"""
    with get_conn() as conn:
        t = date.today()

        def d(days):
            return (t + timedelta(days=days)).isoformat()

        # วัตถุดิบ
        ingredients = [
            ("I01", "ฟักทอง", "กรัม", 1000, 10),
            ("I02", "ไข่ไก่", "ฟอง", 30, 14),
            ("I03", "กระเทียม", "กรัม", 200, 30),
            ("I04", "น้ำมันพืช", "กรัม", 500, 180),
            ("I05", "ซอสหอยนางรม", "กรัม", 300, 180),
            ("I06", "ผักบุ้ง", "กรัม", 500, 3),
            ("I07", "หมูสับ", "กรัม", 500, 3),
            ("I08", "อกไก่", "กรัม", 500, 3),
            ("I09", "ข้าวสาร", "กรัม", 5000, 180),
            ("I10", "ใบกะเพรา", "กรัม", 100, 3),
            ("I11", "พริกขี้หนู", "กรัม", 100, 7),
            ("I12", "คะน้า", "กรัม", 500, 4),
            ("I13", "มะเขือเทศ", "กรัม", 300, 7),
            ("I14", "หอมหัวใหญ่", "กรัม", 300, 20),
            ("I15", "เต้าหู้ไข่", "ชิ้น", 10, 7),
            ("I16", "ถั่วฝักยาว", "กรัม", 300, 5),
            ("I17", "ตำลึง", "กรัม", 200, 3),
            ("I18", "น้ำปลา", "กรัม", 300, 365),
            ("I19", "น้ำตาลทราย", "กรัม", 300, 365),
            ("I20", "แตงกวา", "กรัม", 300, 5),
        ]
        conn.executemany(
            "INSERT INTO ingredients(code,name,unit,min_stock,shelf_days) VALUES (?,?,?,?,?)",
            ingredients,
        )

        cur = conn.execute("SELECT id, name FROM ingredients")
        ing = {row["name"]: row["id"] for row in cur.fetchall()}

        # ล็อตเริ่มต้น
        lots = [
            ("ฟักทอง", -6, 2, 2000, 0.03),
            ("ไข่ไก่", -3, 10, 20, 5),
            ("กระเทียม", -10, 20, 1000, 0.08),
            ("น้ำมันพืช", -20, 150, 3000, 0.05),
            ("ซอสหอยนางรม", -20, 150, 2000, 0.09),
            ("ผักบุ้ง", -1, 1, 600, 0.03),
            ("หมูสับ", -1, 2, 1500, 0.14),
            ("อกไก่", -1, 2, 400, 0.11),
            ("ข้าวสาร", -15, 150, 10000, 0.03),
            ("ใบกะเพรา", -1, 2, 150, 0.06),
            ("พริกขี้หนู", -2, 5, 200, 0.1),
            ("คะน้า", -2, 2, 300, 0.04),
            ("มะเขือเทศ", -2, 5, 800, 0.04),
            ("หอมหัวใหญ่", -5, 15, 1000, 0.04),
            ("เต้าหู้ไข่", -2, 5, 8, 10),
            ("ถั่วฝักยาว", -1, 4, 500, 0.04),
            ("น้ำปลา", -30, 300, 1500, 0.05),
            ("น้ำตาลทราย", -30, 300, 2000, 0.03),
            ("แตงกวา", -1, 4, 200, 0.03),
        ]
        for name, recv, useby, qty, cost in lots:
            c = conn.execute(
                "INSERT INTO lots(ingredient_id,received_date,use_by,qty_left,unit_cost,note) "
                "VALUES (?,?,?,?,?,?)",
                (ing[name], d(recv), d(useby), qty, cost, "ข้อมูลจำลอง"),
            )
            lot_id = c.lastrowid
            conn.execute(
                "INSERT INTO movements(ingredient_id,lot_id,type,qty,unit_cost,created_at,ref,reason) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (ing[name], lot_id, "IN", qty, cost, d(recv) + " 08:00:00", "ยอดยกมา", "ข้อมูลจำลอง"),
            )

        # เมนู + สูตร
        menus = {
            ("M01", "ฟักทองผัดไข่"): [("ฟักทอง", 100), ("ไข่ไก่", 1), ("กระเทียม", 5), ("น้ำมันพืช", 10), ("ซอสหอยนางรม", 10)],
            ("M02", "ผัดผักบุ้งไฟแดง"): [("ผักบุ้ง", 150), ("กระเทียม", 5), ("พริกขี้หนู", 3), ("น้ำมันพืช", 10), ("ซอสหอยนางรม", 15)],
            ("M03", "ข้าวกะเพราหมูสับ"): [("หมูสับ", 100), ("ใบกะเพรา", 10), ("พริกขี้หนู", 5), ("กระเทียม", 5), ("ข้าวสาร", 120), ("น้ำมันพืช", 10), ("น้ำปลา", 10)],
            ("M04", "ไข่เจียวหมูสับ"): [("ไข่ไก่", 2), ("หมูสับ", 40), ("น้ำมันพืช", 30), ("น้ำปลา", 5)],
            ("M05", "ผัดคะน้าหมูสับ"): [("คะน้า", 150), ("หมูสับ", 60), ("กระเทียม", 5), ("ซอสหอยนางรม", 15), ("น้ำมันพืช", 10)],
            ("M06", "ไก่ผัดมะเขือเทศ"): [("อกไก่", 100), ("มะเขือเทศ", 80), ("หอมหัวใหญ่", 40), ("น้ำมันพืช", 10), ("น้ำตาลทราย", 5)],
            ("M07", "แกงจืดเต้าหู้หมูสับ"): [("เต้าหู้ไข่", 1), ("หมูสับ", 50), ("ตำลึง", 30), ("น้ำปลา", 10)],
            ("M08", "ผัดถั่วฝักยาวหมูสับ"): [("ถั่วฝักยาว", 120), ("หมูสับ", 50), ("กระเทียม", 5), ("น้ำปลา", 10), ("น้ำมันพืช", 10)],
            ("M09", "ไข่ผัดมะเขือเทศ"): [("ไข่ไก่", 2), ("มะเขือเทศ", 100), ("หอมหัวใหญ่", 30), ("น้ำมันพืช", 10), ("น้ำตาลทราย", 5)],
            ("M10", "แกงจืดฟักทองหมูสับ"): [("ฟักทอง", 120), ("หมูสับ", 50), ("น้ำปลา", 10)],
        }
        for (code, name), items in menus.items():
            c = conn.execute("INSERT INTO menus(code,name) VALUES (?,?)", (code, name))
            mid = c.lastrowid
            for ing_name, qty in items:
                conn.execute(
                    "INSERT INTO recipe_items(menu_id,ingredient_id,qty_per_dish) VALUES (?,?,?)",
                    (mid, ing[ing_name], qty),
                )

        # เกษตรกร
        farmers = [
            ("กลุ่มเกษตรกรบ้านหนองบัว (จำลอง)", "ต.หนองบัว", "081-000-0001"),
            ("ฟาร์มไข่ลุงชัย (จำลอง)", "ต.ท่าช้าง", "081-000-0002"),
            ("สวนผักป้าแดง (จำลอง)", "ต.บ้านใหม่", "081-000-0003"),
            ("วิสาหกิจชุมชนผักปลอดภัย (จำลอง)", "ต.โนนสูง", "081-000-0004"),
            ("ฟาร์มหมูพี่เอก (จำลอง)", "ต.หนองบัว", "081-000-0005"),
        ]
        conn.executemany("INSERT INTO farmers(name,area,contact) VALUES (?,?,?)", farmers)
        cur = conn.execute("SELECT id FROM farmers ORDER BY id")
        fid = [row["id"] for row in cur.fetchall()]

        # ผลผลิตพร้อมขาย
        produce = [
            (0, "ฟักทอง", 30, "กก.", 50, 0),
            (2, "ฟักทอง", 35, "กก.", 20, 1),
            (1, "ไข่ไก่", 5, "ฟอง", 300, 0),
            (3, "ไข่ไก่", 5.5, "ฟอง", 200, 0),
            (2, "ผักบุ้ง", 30, "กก.", 15, 0),
            (2, "คะน้า", 40, "กก.", 10, 0),
            (3, "ถั่วฝักยาว", 40, "กก.", 10, 1),
            (3, "ตำลึง", 50, "กก.", 5, 0),
            (3, "มะเขือเทศ", 40, "กก.", 15, 0),
            (0, "แตงกวา", 25, "กก.", 20, 0),
            (4, "หมูสับ", 140, "กก.", 30, 0),
            (0, "ใบกะเพรา", 60, "กก.", 3, 0),
        ]
        for f, name, price, unit, qty, ready in produce:
            conn.execute(
                "INSERT INTO produce(farmer_id,ingredient_id,price,sell_unit,qty_available,ready_date,updated_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (fid[f], ing[name], price, unit, qty, d(ready), now_str()),
            )

        # ประวัติซื้อย้อนหลัง
        history = [(1, -7, "ไข่ไก่", 60, 5), (2, -5, "ผักบุ้ง", 2000, 0.03), (4, -3, "หมูสับ", 3000, 0.14)]
        for f, day, name, qty, price in history:
            c = conn.execute(
                "INSERT INTO purchase_orders(farmer_id,created_at,status,received_at) VALUES (?,?,?,?)",
                (fid[f], d(day) + " 09:00:00", "RECEIVED", d(day) + " 15:00:00"),
            )
            conn.execute(
                "INSERT INTO po_items(po_id,ingredient_id,qty,unit_price) VALUES (?,?,?,?)",
                (c.lastrowid, ing[name], qty, price),
            )


def init_db():
    create_tables()
    if is_empty():
        seed_demo_data()


if __name__ == "__main__":
    try:
        init_db()
        print("สร้างฐานข้อมูล + ข้อมูลจำลอง (Demo Data) เรียบร้อยแล้ว")
    except Exception as err:
        print(f"Database Error: {err}")
        sys.exit(1)
