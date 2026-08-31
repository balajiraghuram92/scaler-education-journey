# Prompt: Simplify nav to Chapters-only, make Chapters the default page

Paste everything below into the Local LLM verbatim.

---

You are editing a React app. Make exactly two changes, described below with exact
before/after content. Do not touch any other file, do not delete any page component
files, do not remove any `<Route>` definitions other than the one explicitly changed
below. The routes for `/reading-map`, `/lab-projects`, `/curriculum-import` and their
page components must remain in the codebase untouched — they are only being unlinked
from the nav bar and from the root path, not deleted, so they stay reachable by typing
their URL directly and can be restored to the nav easily later.

## File 1: `app/src/components/Navbar.jsx`

Find this block (lines 21–56):

```jsx
          <div className="navbar-section navbar-center">
            <Link
              to="/"
              className={`navbar-nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              Knowledge Atlas
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/reading-map"
              className={`navbar-nav-link ${location.pathname === '/reading-map' ? 'active' : ''}`}
            >
              Reading Map
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/lab-projects"
              className={`navbar-nav-link ${location.pathname === '/lab-projects' ? 'active' : ''}`}
            >
              Lab Projects
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/curriculum-import"
              className={`navbar-nav-link ${location.pathname === '/curriculum-import' ? 'active' : ''}`}
            >
              Importer
            </Link>
            <span className="navbar-nav-divider">·</span>
            <Link
              to="/chapters"
              className={`navbar-nav-link ${location.pathname.startsWith('/chapters') || location.pathname.startsWith('/chapter') || location.pathname.startsWith('/learning-paths') ? 'active' : ''}`}
            >
              Chapters
            </Link>
          </div>
```

Replace it with (remove the Knowledge Atlas / Reading Map / Lab Projects / Importer
links and their `·` dividers; keep the Chapters link exactly as it is, including its
`className` logic, and keep the same 2-space indentation and multi-line `<Link>`
formatting style used throughout this file):

```jsx
          <div className="navbar-section navbar-center">
            <Link
              to="/chapters"
              className={`navbar-nav-link ${location.pathname.startsWith('/chapters') || location.pathname.startsWith('/chapter') || location.pathname.startsWith('/learning-paths') ? 'active' : ''}`}
            >
              Chapters
            </Link>
          </div>
```

Nothing else in this file changes (the brand logo section, the profile section, and the
`useLocation` import/usage all stay exactly as they are — `location` is still used by
the Chapters link's `className`).

## File 2: `app/src/App.jsx`

### 2a. Remove the now-unused `Home` import

Find (line 3):
```jsx
import Home from './pages/Home';
```
Delete this line entirely. (The `Home.jsx` page file itself must NOT be deleted — only
this import line goes, since nothing will reference `Home` anymore after step 2b.)

### 2b. Make `/chapters` the destination of the root path

Find this block (lines 19–27):
```jsx
          {/* Home / Knowledge Atlas */}
          <Route
            path="/"
            element={
              <Layout>
                <Home />
              </Layout>
            }
          />
```

Replace it with (a plain redirect, matching the exact style already used elsewhere in
this same file for other redirects, e.g. the `/certifications` → `/profile` route a few
lines down — self-closing `<Navigate>` on its own line, no `<Layout>` wrapper, `replace`
so it doesn't add a history entry):

```jsx
          {/* Root — redirects to Chapters */}
          <Route
            path="/"
            element={<Navigate to="/chapters" replace />}
          />
```

`Navigate` is already imported at the top of this file (`import { BrowserRouter, Routes,
Route, Navigate } from 'react-router-dom';`), so no import changes are needed for this
part.

Nothing else in `App.jsx` changes — every other `<Route>` (including `/reading-map`,
`/lab-projects`, `/curriculum-import`, `/chapters`, `/chapters/:slug`,
`/learning-paths/:slug`, etc.) stays exactly as it is.

## Output expected

The full, updated contents of both files:
- `app/src/components/Navbar.jsx`
- `app/src/App.jsx`

## Verification (do this yourself after applying, don't just trust the diff)

- `Navbar.jsx` should now render exactly one link in `navbar-center`: Chapters.
- `App.jsx` should have no remaining reference to `Home` anywhere (grep for `Home` in
  the file — it should not appear).
- Visiting `/` in the running app should immediately redirect to `/chapters`.
- Visiting `/reading-map`, `/lab-projects`, or `/curriculum-import` directly by URL
  should still work exactly as before (these routes and their pages are untouched).
