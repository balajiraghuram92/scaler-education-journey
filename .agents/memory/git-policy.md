---
type: project
description: Git commit auto, push ask-before-push policy
---

# Git Workflow Preferences — Raghu

- **Commit policy**: Muse may commit automatically without asking. Stage only the files Muse changed (never `git add -A` on a dirty tree).
- **Push policy**: ALWAYS ask for explicit user confirmation before `git push`. User has SSH chain configured, so push will work when authorized, but never auto-push.
- **Context**: Repo `balajiraghuram92/scaler-education-journey` — contains `.raghu-personal` folder at `info/.raghu-personal/` (tracked dot folder for personal assets, low-profile on GitHub front page, cloneable). User approved `info/.raghu-personal/` creation on 2026-08-07 and authorized commit+push for it in this session.
- **Future**: If push is requested, use `git push origin <branch>` only after user says "push" in that session.

Saved: 2026-08-07
