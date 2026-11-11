# PROJECT_AUDIT.md — Phase 0 Repository Audit

**Application:** เมนูชุมชน (Community Menu Planner) — ระบบวางแผนเมนูและจัดซื้อผลผลิตชุมชนโดยใช้ AI  
**Audit Date:** 2026-11-11  
**Lead Auditor:** 69030450 (นายกิตติศักดิ์ พัฒนนิติศักดิ์ — QA & Documentation)  
**Current Branch:** `team/69030450-qa-docs`  
**Baseline Git Status:** Initialized from zip distribution, initial baseline commit `67d832c` preserved on `main`  

---

## 1. Executive Summary

This repository audit constitutes **Phase 0** of the master development plan outlined in `AGENT.md`. The audited codebase is **"เมนูชุมชน (Community Menu Planner)"**, a Python desktop application utilizing Tkinter and Google Gemini AI designed for local restaurant menu planning, FIFO lot inventory tracking, community agricultural produce procurement, and cost analysis.

### High-Level Findings
1. **Framework & Language:** Python 3.14 (desktop environment), Tkinter/ttk for GUI presentation.
2. **Persistence State (Critical Blockers):** The codebase is currently in a broken, half-migrated state between an embedded SQLite storage engine (`community_menu.db`) and a client-server MySQL database (`community_menu`). `db.py` was converted to `mysql.connector`, but `logic.py`, `ai_helper.py`, and `screens/inventory.py` still invoke SQLite-style execution APIs (`conn.execute()`, `?` placeholder parameters, `:i` named placeholders, SQLite `||` string concatenation).
3. **External Environment:** MySQL server is not running on `localhost:3306`, and `mysql-connector-python` is not installed in the active Python runtime (`C:\Program Files\Thonny\python.exe`). Attempting to import `db` or `logic` raises an immediate `ModuleNotFoundError: No module named 'mysql'`.
4. **Baseline Test Suite:** `test_logic.py` is present in the repository but completely blank (0 tests, 1 byte).
5. **Core Business Logic:** The business logic in `logic.py` and screen implementations in `screens/` are well-structured, modular, and cleanly written with defensive validation and Thai localization, but cannot run until the database abstraction layer is stabilized.

---

## 2. Codebase Inventory & Structural Map

```text
CommunityMenu2-main/
├── .gitignore                    # Configured for Python, pycache, *.db, default_key.py, *.exe
├── AGENT.md / Agents.md          # Master development instructions & team specification
├── CODE_GUIDE.md                 # Layman architectural narrative in Thai
├── PROJECT.md                    # Academic project definition & software specification
├── README.md                     # Application overview and user guide
├── requirements.txt              # Listed dependencies: google-genai, mysql-connector-python
├── main.py                       # Application bootstrap, root Tkinter window & tab controller
├── db.py                         # Current DB schema definitions & MySQL seed data
├── logic.py                      # Pure business logic, conversions, calculations, plan generator
├── ai_helper.py                  # Google Gemini API connector (JSON schema extraction)
├── test_logic.py                 # Baseline test file (currently empty)
├── community_menu_mysql.sql      # DDL export generated from former SQLite database
├── mysql_export_data.txt         # SQL INSERT dump of seed data
├── screens/
│   ├── __init__.py               # Python package marker
│   ├── home.py                   # HomeScreen (dashboard metrics, low-stock, expiring lots, PO status)
│   ├── inventory.py              # InventoryScreen (ingredient CRUD, lot management, adjustments)
│   ├── recipes.py                # RecipeScreen (menu & recipe per-dish ingredient editor)
│   ├── community.py              # CommunityScreen (farmers & community produce management)
│   ├── planner.py                # PlannerScreen (daily planner, AI recommendation, budget solver)
│   ├── purchase.py               # PurchaseScreen (purchase order creation, status, lot receiving)
│   ├── report.py                 # ReportScreen (spending reports, waste logs, community contribution)
│   └── widgets.py                # UI style definitions, custom widgets, Table (Treeview)
└── docs/                         # Formal project documentation suite
    ├── PROJECT_AUDIT.md          # Phase 0 repository audit report (this document)
    ├── ARCHITECTURE.md           # Logical and physical architectural specification
    ├── TEAM_ROLES.md             # Subsystem ownership & team member responsibility matrix
    ├── BRANCH_STRATEGY.md        # Branching policy, PR workflow, and gate controls
    └── ROADMAP.md                # Development roadmap, milestones, and deliverables
```

---

## 3. Current Feature Audit & Operational Status

| Module / Screen | File | Intended Feature | Current Operational Status | Root Cause / Blocker |
|---|---|---|---|---|
| **Application Core** | `main.py` | Tkinter root application, tabs, global exception handler | **BROKEN** | Fails on launch: `init_db()` crashes on `import mysql.connector` |
| **Dashboard** | `screens/home.py` | Summary cards, low stock alerts, lot expiration warnings, pending POs | **PARTIALLY WORKING** (Code complete, blocked by DB) | Blocked by `logic.dashboard()` DB access |
| **Inventory & Lots** | `screens/inventory.py` | Ingredient CRUD, FIFO lot tracking, manual receipt, usage, waste, adjustments | **PARTIALLY WORKING** (Code complete, blocked by DB) | Direct call to `get_conn()` on line 175 incompatible with generator |
| **Recipe Management** | `screens/recipes.py` | Menu definitions, per-dish ingredient configuration, units | **PARTIALLY WORKING** (Code complete, blocked by DB) | Blocked by `logic.list_menus()` |
| **Community Produce**| `screens/community.py` | Farmer directory, available produce listings, pricing, ready dates | **PARTIALLY WORKING** (Code complete, blocked by DB) | Blocked by `logic.list_farmers()` |
| **Menu Planning & AI**| `screens/planner.py` | Multi-menu plan builder, dish scaling, budget validation, AI prompt execution | **PARTIALLY WORKING** (Code complete, blocked by DB/API) | Blocked by DB; AI requires Gemini API key or fallback manual selection |
| **Purchasing** | `screens/purchase.py` | Purchase order generation grouped by cheapest farmer, goods receipt into lots | **PARTIALLY WORKING** (Code complete, blocked by DB) | Blocked by `logic.list_pos()` |
| **Reports** | `screens/report.py` | Date-filtered financial reports, community spend analysis, waste aggregation | **PARTIALLY WORKING** (Code complete, blocked by DB) | Blocked by `logic.report()` |
| **AI Integration** | `ai_helper.py` | Structured JSON prompt to `gemini-flash-lite-latest` | **BLOCKED** | Missing API key (expected fallback mechanism operates cleanly if DB works) |
| **Automated Tests** | `test_logic.py` | Unit and integration test suite | **MISSING** | File is empty (0 test cases executed) |

---

## 4. Technical Debt & Critical Discrepancies

### 4.1 The SQLite vs MySQL Fracture
1. **`db.py` Implementation:**
   - Defines `DB_CONFIG` expecting a running MySQL service on port 3306.
   - Decorates `get_conn()` with `@contextmanager`, yielding a `mysql.connector` connection.
2. **`logic.py` & `screens/inventory.py` Implementation:**
   - Calls `conn = get_conn()`, expecting a connection object that can directly invoke `conn.execute(sql, params)`. Because `get_conn()` is a generator function, calling it without `with` yields a `<generator object>`, which immediately raises `AttributeError: 'generator' object has no attribute 'execute'`.
   - All queries use SQLite syntax:
     - Placeholder format `?` instead of MySQL `%s`.
     - Named placeholder format `:i` in `logic.py` line 73.
     - SQLite string concatenation `||` in `logic.py` line 395 (`m.name || ' x' || pi.dishes`).
     - Relies on dict-like row access (`row["name"]`) provided natively by SQLite with `conn.row_factory = sqlite3.Row`.
3. **Environment Reality:**
   - The user operating environment is a local Windows desktop without an active MySQL daemon.
   - As documented in `CODE_GUIDE.md` and `PROJECT.md`, the desktop application was originally targeted as a self-contained local installation with `community_menu.db`.

### 4.2 Missing Dependencies & Environment Constraints
- `mysql-connector-python`: Not installed in the active environment.
- `google-genai`: Not installed in the active environment.
- Active system Python is located at `C:\Program Files\Thonny\python.exe` (Python 3.14.4), containing standard library modules (`sqlite3`, `tkinter`, `unittest`).

### 4.3 Missing Test Coverage
- `test_logic.py` exists as an empty placeholder. There are zero regression, integration, or unit tests.

---

## 5. Baseline Test Execution Results

```text
======================================================================
TEST EXECUTION LOG: Baseline Phase 0 Audit
Command: & "C:\Program Files\Thonny\python.exe" -m unittest test_logic.py
Target: test_logic.py
Result: NO TESTS RAN (Ran 0 tests in 0.000s)
Status: NOT TESTED / EMPTY TEST SUITE
======================================================================
Module Import Smoke Test:
- python -c "import sqlite3, tkinter" -> OK (Standard Library available)
- python -c "import db" -> FAILED (ModuleNotFoundError: No module named 'mysql')
- python -c "import logic" -> FAILED (Cascade import error from db)
```

---

## 6. Identified Risks

1. **System Inoperability (High Risk):** The application cannot be launched by the end user or evaluated by testers in its current state.
2. **Data Integrity Violation (High Risk):** Modifying database drivers without an abstraction layer risks subtle calculation bugs in FIFO lot ordering (`ORDER BY use_by, id`) and stock deduction.
3. **Uncoordinated Multi-Developer Collision (Medium Risk):** Five team members modifying `db.py`, `logic.py`, and `screens/` simultaneously without strict interface contracts will produce merge conflicts.
4. **AI Dependency Coupling (Low/Medium Risk):** If network or API quota is unavailable, menu planning must seamlessly degrade to manual mode without crashing.

---

## 7. Recommended Implementation Plan

1. **Phase 1 (Team Setup & Architecture Alignment):**
   - Establish formal team roles and communication contracts.
   - Lock branch structure (`develop`, member branches, task branches).
   - Document formal architecture in `docs/ARCHITECTURE.md`.
2. **Phase 2 (Database Layer Stabilization):**
   - Provide an adaptable database adapter in `db.py` that supports seamless embedded SQLite operation (`community_menu.db`) out-of-the-box while maintaining MySQL DDL compatibility for server installations.
   - Harmonize query execution in `logic.py` so standard CRUD, FIFO lot management, and aggregation succeed cleanly.
3. **Phase 3 (Core Logic & Unit Testing):**
   - Populate `test_logic.py` with comprehensive unit tests for unit conversion (`to_std`, `fmt_qty`), FIFO lot suggestion (`suggest_lots`), negative stock prevention, and multi-recipe calculation (`calc_plan`).
4. **Phase 4 (UI Integration & Manual Windows Testing):**
   - Verify all 7 screens under Tkinter.
   - Ensure `inventory.py` relies on `logic.py` rather than opening raw database connections.
   - Verify graceful AI fallback when offline or lacking credentials.
