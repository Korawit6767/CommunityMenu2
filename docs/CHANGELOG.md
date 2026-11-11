# CHANGELOG.md — Project Version History

All notable changes to the "Community Menu Planner" application are documented in this file.

---

## [1.0.0] — 2026-11-11

### Added
- **Universal Database Engine (`db.py`):** Added `ManagedConnection` and `ManagedCursor` classes providing zero-configuration SQLite support (`community_menu.db`) as the local desktop default, with transparent fallback from MySQL.
- **Automated Regression Test Suite (`test_logic.py`):** Implemented 17 unit, integration, and end-to-end workflow tests verifying conversions, FIFO lot ordering, zero-deficit guarantees, AI prompt compilation, and complete user journeys.
- **Service Decoupling (`logic.preview_lots`):** Introduced service-level lot previewing to fully decouple presentation screens from direct database driver dependencies.
- **Comprehensive Documentation Suite (`docs/`):**
  - `docs/PROJECT_AUDIT.md`: Phase 0 repository audit report.
  - `docs/ARCHITECTURE.md`: Layered system design, sequence diagrams, and state transitions.
  - `docs/TEAM_ROLES.md`: 5 designated members, subsystem ownership, and collaboration matrix.
  - `docs/BRANCH_STRATEGY.md`: Git branching workflow, commit standards, and protection gates.
  - `docs/FEATURES.md`: Full feature verification matrix.
  - `docs/ROADMAP.md`: Multi-phase milestone tracker.
  - `docs/TESTING.md`: Test execution guide, test breakdown, and performance benchmarks.
  - `docs/USER_GUIDE.md`: User manual in Thai.
  - `HANDOFF.md` & `PHASE-LOG.md`: Engineering handoff and phase execution logs.

### Fixed
- Fixed application crash on startup caused by missing `mysql.connector` dependency in desktop environments.
- Fixed SQL query syntax discrepancies where `logic.py` executed SQLite syntax against generator-based connection objects.
- Fixed direct database connection leaks in `screens/inventory.py`.
- Fixed empty `test_logic.py` placeholder by introducing an automated test suite.

### Security & Integrity
- Strictly protected `main` branch with zero direct commits.
- Verified that AI services cannot modify database tables, compute balances, or leak supplier contact details.
