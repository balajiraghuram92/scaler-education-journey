# .raghu-personal

Personal drop folder for Raghu — resume, plans, images, PDFs.

- This folder IS tracked (pushed to GitHub) but hidden behind the dot prefix — not rendered on the repo front page. Fork/clone will include it (intentional).
- Not part of `app` build or `api` — nothing here is deployed to Azure Static Web Apps.
- Muse Code can read anything you drop here via `read_file`.

Usage:
- Drop files into `resume/`, `plans/`, `assets/`
- Tell Muse "check .raghu-personal/..." and it can read directly

Add `.gitkeep` files so empty dirs are tracked.
