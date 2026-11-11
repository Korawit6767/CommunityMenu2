# TEAM_ROLES.md — Team Structure & Ownership Matrix

**Project:** เมนูชุมชน (Community Menu Planner)  
**Effective Date:** 2026-11-11  
**Team Composition:** 5 Designated Members  

---

## 1. Team Members & Roles

### 1.1 Member 69030450 — Quality Assurance & Documentation
- **Name:** นายกิตติศักดิ์ พัฒนนิติศักดิ์
- **Role:** QA Lead / Test Engineer / Technical Documentarian
- **Designated Branch:** `team/69030450-qa-docs`
- **Core Responsibilities:**
  - Lead repository audit, test strategy design, and baseline verification.
  - Implement and maintain unit test suites in `test_logic.py` and integration tests.
  - Formulate regression test suites for calculation logic, unit conversion, and lot allocation.
  - Author and maintain project documentation (`PROJECT_AUDIT.md`, `ARCHITECTURE.md`, `TEAM_ROLES.md`, `BRANCH_STRATEGY.md`, `ROADMAP.md`, `HANDOFF.md`, `PHASE-LOG.md`).
  - Verify release readiness, identify defects, and audit CI results.

### 1.2 Member 69030377 — UX/UI Design
- **Name:** นางสาวพิชชาภา ภูววิไลเมธา
- **Role:** UX/UI Lead Designer
- **Designated Branch:** `team/69030377-ux-ui`
- **Core Responsibilities:**
  - Define application user flow, navigation hierarchy, and layout specifications.
  - Maintain and enhance design system specifications (colors, spacing, typography, ttk element styling in `screens/widgets.py`).
  - Standardize error dialogs, alert banners, and visual accessibility (contrast, responsive sizing).
  - Review screen consistency between mockups and desktop rendering across Windows display scalings.

### 1.3 Member 69030343 — Backend & Database
- **Name:** นายธีระนิตย์ บุญทวี
- **Role:** Backend Lead / Database Architect
- **Designated Branch:** `team/69030343-backend-db`
- **Core Responsibilities:**
  - Primary ownership of database schema, migrations, and DDL integrity (`db.py`, `community_menu_mysql.sql`).
  - Architect and maintain dual database engine support (zero-config local SQLite + networked MySQL server).
  - Design data models, foreign key relationships, cascade behaviors, and seed data (`seed_demo_data`).
  - Optimize query performance, indexes, and transactional boundaries.

### 1.4 Member 69030304 — Python Application & Core Logic
- **Name:** นายชยภัทร พุทธศรีเมือง
- **Role:** Python Core Developer / Algorithm Specialist
- **Designated Branch:** `team/69030304-python-automation`
- **Core Responsibilities:**
  - Maintain core application architecture and execution lifecycle (`main.py`, `logic.py`).
  - Implement business rules, unit conversions (`to_std`, `fmt_qty`), and FIFO lot deduction algorithms.
  - Develop multi-recipe meal calculation engine (`calc_plan`) and supplier optimization (`best_offer`).
  - Integrate AI advisory service (`ai_helper.py`) with defensive timeouts, fallback mechanisms, and validation.

### 1.5 Member 69030208 — GUI Implementation & Database Integration
- **Name:** นายฤทธิพร วงค์ป้อม
- **Role:** GUI Developer / Data Integration Specialist
- **Designated Branch:** `team/69030208-gui-db`
- **Core Responsibilities:**
  - Implement desktop views (`screens/home.py`, `inventory.py`, `recipes.py`, `community.py`, `planner.py`, `purchase.py`, `report.py`).
  - Connect presentation widgets to backend service layers without leaking DB connections into UI modules.
  - Implement threading controllers for background tasks to prevent UI thread lockup.
  - Perform GUI usability testing and input validation before data reaches business logic.

---

## 2. Subsystem Ownership & Collaboration Matrix

| Subsystem / File | Primary Owner | Secondary Collaborator | Review Gatekeeper |
|---|---|---|---|
| **Quality Assurance & Testing** (`test_logic.py`, `tests/`) | 69030450 | 69030304 | 69030450 |
| **Documentation & Phase Logs** (`docs/*`, `HANDOFF.md`, `PHASE-LOG.md`) | 69030450 | All Members | 69030450 |
| **UI Design System & Theming** (`screens/widgets.py`) | 69030377 | 69030208 | 69030377 |
| **GUI Screen Views** (`screens/*.py`, `main.py`) | 69030208 | 69030377 | 69030208 |
| **Database Schema & Driver** (`db.py`, `*.sql`) | 69030343 | 69030208 | 69030343 |
| **Core Business Logic & Algorithms** (`logic.py`) | 69030304 | 69030450 | 69030304 |
| **AI Integration & External Services** (`ai_helper.py`) | 69030304 | 69030208 | 69030304 |

---

## 3. Collaboration Rules & Communication Contracts

1. **Subsystem Isolation:** A member may not modify files owned by another subsystem without prior coordination and explicit code review.
2. **Interface Preservation:** Public signatures in `logic.py` and `db.py` must maintain backward compatibility. Changes to parameters or return structures must be documented in `ARCHITECTURE.md` before merging.
3. **UI/DB Separation Principle:** Screen classes in `screens/` must never construct raw SQL queries or invoke database drivers directly. All database access must pass through `logic.py` service functions.
4. **Data Contract Compliance:** Any alteration to database tables or column types owned by 69030343 must be reflected in migration scripts and coordinated with 69030208 (GUI) and 69030304 (Logic).
