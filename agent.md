# Agent Rules & Execution Policy

**1. Git Commit & Push Policy (STRICT):**
- The agent does **NOT** have permission to execute `git commit`, `git push`, or modifying git remote commands.
- The agent must **ONLY** explain the proposed changes and request the user to commit and push by providing the exact commit message and git commands.
- The user retains sole execution authority for committing and pushing to git repositories.

**2. Workflow Modification Policy (STRICT):**
- The agent does **NOT** have permission to make changes directly to any GitHub Actions workflow files (`.github/workflows/*`) in the workspace.
- The agent can **ONLY** suggest workflow changes, explain the rationale, and provide the exact YAML snippet for the user to review and apply manually.
- Workflow files must remain frozen and stable once deployed to prevent pipeline disruptions.
