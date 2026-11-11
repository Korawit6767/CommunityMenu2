# BRANCH_STRATEGY.md — Git Workflow & Branching Policy

**Project:** เมนูชุมชน (Community Menu Planner)  
**Standard:** Team-Based Branching, Pull Requests & Protected Release  
**Status:** Active  

---

## 1. Branch Hierarchy

```text
[main] (Production / Stable Releases — PROTECTED)
  ▲
  │ (Explicit User Approval Required to Merge)
  │
[develop] (Integration & Pre-Release Testing)
  ▲
  ├───────────────────┼───────────────────┼───────────────────┼───────────────────┐
  │                   │                   │                   │                   │
[team/69030450-     [team/69030377-     [team/69030343-     [team/69030304-     [team/69030208-
 qa-docs]            ux-ui]              backend-db]         python-automation]  gui-db]
  ▲                   ▲                   ▲                   ▲                   ▲
  │                   │                   │                   │                   │
(Task Branches)     (Task Branches)     (Task Branches)     (Task Branches)     (Task Branches)
docs/*              ui/*                feat/*              feat/*              feat/*
test/*                                  fix/*               refactor/*          fix/*
```

---

## 2. Branch Definitions & Permissions

### 2.1 Permanent Protected Branches

#### `main`
- **Purpose:** Release-ready, thoroughly verified, stable versions.
- **Rules:**
  - **ABSOLUTE RULE:** Direct commits are forbidden.
  - No merges permitted without explicit user approval.
  - History must remain clean and linear.

#### `develop`
- **Purpose:** Continuous integration branch where verified team contributions converge.
- **Rules:**
  - Changes must arrive exclusively via verified Pull Requests from team member branches.
  - All automated unit and integration tests must pass before merging.
  - Never merge unverified or broken code into `develop`.

### 2.2 Designated Team Branches
Each team member maintains an active branch reflecting their subsystem domain:
1. `team/69030450-qa-docs` (QA / Documentation)
2. `team/69030377-ux-ui` (UX/UI Design)
3. `team/69030343-backend-db` (Backend & Database)
4. `team/69030304-python-automation` (Application & Core Logic)
5. `team/69030208-gui-db` (GUI & Database Integration)

### 2.3 Task Branches
For isolated features, bug fixes, or documentation tasks, team members create short-lived task branches:
- `feature/<id>-<task-name>`: New feature implementations.
- `fix/<id>-<bug-name>`: Bug fixes and issue patches.
- `refactor/<id>-<scope>`: Architectural and non-breaking code refactoring.
- `docs/<id>-<scope>`: Documentation updates.
- `test/<id>-<suite>`: Test suite implementations.

---

## 3. Commit Standards

All commits must adhere to Conventional Commits:

```text
<type>(<scope>): <concise description in present tense>

[optional body providing technical rationale]
[optional footer referencing issue or task ID]
```

### Approved Commit Types
- `feat`: New feature or user capability.
- `fix`: Bug fix or patch.
- `docs`: Documentation addition or revision.
- `test`: Adding or refactoring tests (no production code change).
- `refactor`: Code reorganization with no functional or behavioral change.
- `perf`: Performance improvement.
- `chore`: Repository configuration, dependency changes, or setup.

---

## 4. Operating Rules for Agents & Developers

1. **Pre-flight Checks:** Always verify working tree status before starting:
   ```bash
   git status
   git branch --show-current
   ```
2. **Never Work on `main`:** Ensure the active branch is either a team branch or task branch.
3. **Diff Review:** Inspect the exact staged diff before committing:
   ```bash
   git diff --staged
   ```
4. **No Destructive Operations:** Never run `git reset --hard`, `git push --force`, or branch deletions without authorization.
5. **Merge Gate to `main`:** Only the user can authorize a merge into `main`.
