# FEATURES.md — Feature Inventory & Verification Matrix

**Project:** เมนูชุมชน (Community Menu Planner)  
**Status Key:**
- `Working`: Fully implemented, verified with automated tests and manual UI smoke tests.
- `Partially Working`: Functional with documented constraints.
- `Broken`: Non-functional / blocked.
- `Missing`: Planned but not implemented.
- `Needs Verification`: Awaiting specific platform/environment testing.

---

## Feature Matrix

| Subsystem | Feature Description | Status | Verification Method | Notes |
|---|---|---|---|---|
| **Core Architecture** | Universal Database Adapter | **Working** | `test_logic.py` & `db.py` | Auto SQLite fallback with optional MySQL |
| **Core Architecture** | Context-Managed Database Sessions | **Working** | `test_logic.py` | Auto commit on success, rollback on error |
| **Inventory** | Master Ingredient Catalog (CRUD) | **Working** | `InventoryScreen` | Supports standard units (g, eggs, pcs) |
| **Inventory** | FIFO Lot Management & Allocation | **Working** | `TestDatabaseAndLogic.test_suggest_lots_fifo` | Orders by earliest `use_by` date |
| **Inventory** | Negative Stock Prevention | **Working** | `TestDatabaseAndLogic.test_prevent_negative_stock` | Aborts with `AppError` before deducting |
| **Inventory** | Lot Expiration Warnings (< 2 days) | **Working** | `HomeScreen` & `InventoryScreen` | Color-coded tags (warning/danger) |
| **Inventory** | Stock Adjustments with Reason Logging | **Working** | `TestDatabaseAndLogic.test_adjust_lot_requires_reason` | Mandatory non-empty reason in audit trail |
| **Recipe Management** | Recipe Formula per-dish Definition | **Working** | `RecipeScreen` | Links menus to ingredients with dish scaling |
| **Community Registry**| Farmer Contact & Area Directory | **Working** | `CommunityScreen` | Local farmer profiles |
| **Community Registry**| Produce Availability & Pricing | **Working** | `CommunityScreen` & `best_offer` | Time-sensitive availability and std pricing |
| **Menu Planning** | Multi-Recipe Scaling Calculation | **Working** | `TestDatabaseAndLogic.test_calc_plan_pumpkin_dish` | Aggregates duplicate ingredients across dishes |
| **Menu Planning** | Community Procurement Optimizer | **Working** | `test_logic.py` (`calc_plan`) | Selects cheapest supplier ready today |
| **Menu Planning** | Plan Confirmation & Double-Issue Guard | **Working** | `TestEndToEndWorkflow.test_full_demo_lifecycle` | Plan cannot be issued twice (`USED`) |
| **Procurement** | Auto-PO Generation Grouped by Farmer | **Working** | `TestEndToEndWorkflow` | Partitions deficits by vendor |
| **Procurement** | Goods Receipt into Lots | **Working** | `TestDatabaseAndLogic.test_purchase_order_lifecycle` | Injects lots with calculated shelf life |
| **Procurement** | Prevention of Duplicate Receiving | **Working** | `TestDatabaseAndLogic.test_purchase_order_lifecycle` | Only `PENDING` orders can be received |
| **Reporting** | Period Financial Summary | **Working** | `TestEndToEndWorkflow` (`report()`) | Summarizes PO totals by farmer |
| **Reporting** | Usage and Waste Historical Breakdown | **Working** | `ReportScreen` & `report()` | Categorizes stock movements |
| **AI Advisor** | Prompt Data Compilation | **Working** | `TestAIHelper.test_build_prompt_data` | Excludes user-filtered dishes |
| **AI Advisor** | Strict JSON Schema Validation | **Working** | `TestAIHelper.test_check_answer_valid_and_filters_invalid` | Discards invalid / duplicate menu codes |
| **AI Advisor** | Offline & Missing Key Fallback | **Working** | `TestAIHelper.test_ask_ai_without_key_raises_apperror` | User notified to select menus manually |
