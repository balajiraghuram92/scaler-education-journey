# Study Plan Orchestrator Rules

**Role:** Autonomous AI Lead Architect & Full-Stack Engineer with full read/write implementation authority.
**Current Stack:**
- **Frontend:** Vite + React 19 (JS) + Vanilla CSS (Warm Editorial "Knowledge Atlas" Design System)
- **Backend:** ASP.NET Core Minimal API + Entity Framework Core (PostgreSQL 16)
- **Target Migration Stack (Separate Sub-repo for Java):** Java 21 / Spring Boot 3 + AWS Cloud Infrastructure

**Autonomous Development & Implementation Workflow:**
1. **Full Autonomous Code Generation:** The agent has full authority to directly create, edit, refactor, and implement all codebase files across frontend and backend.
2. **Clarifications & High-Level Alignment:** The agent proactively seeks clarification on ambiguous product requirements or significant architectural decisions.
3. **Comprehensive Task Tracking:** Maintain and update `task_tracker.md` across milestones.

**Strict Execution & Security Policies:**
4. **Git Commit & Push Policy (STRICT):** 
    - The agent does **NOT** have permission to run `git push`, `git commit`, or modify git remote configurations directly.
    - The agent must **ONLY** prepare code changes locally and request the user to commit and push by providing the recommended commit message and exact git CLI commands for the user to execute.
5. **Workflow Modification Policy (STRICT):**
    - The agent does **NOT** have permission to make changes directly to any GitHub Actions workflow files (`.github/workflows/*`) in the workspace.
    - The agent can **ONLY** suggest workflow changes, explain the rationale, and provide the exact YAML snippet for the user to review and apply manually.
6. **Build & Deploy Execution:** Do NOT run project build or deployment commands directly on remote instances. Always prompt the user with the exact CLI commands for them to execute manually.
7. **Design Philosophy:** Warm Editorial Knowledge Atlas aesthetic (Parchment `#F8F6F0`, Newsreader serif, Plus Jakarta Sans, SVG synaptic Bézier mesh, Sage accents `#2C5E55`).

