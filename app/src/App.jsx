import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import Profile from './pages/Profile';
import VerticalDetail from './pages/VerticalDetail';
import LabProjects from './pages/LabProjects';
import ReadingMap from './pages/ReadingMap';
import ChapterReader from './pages/ChapterReader';
import CurriculumImporter from './pages/CurriculumImporter';
import ChaptersIndex from './pages/ChaptersIndex';
import LearningPathDetail from './pages/LearningPath/LearningPathDetail';
import AuthPage from './pages/AuthPage';
import AdminDashboard from './pages/AdminDashboard';
import ProtectedRoute from './components/common/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';

// Localization Lab Pages
import LocalizationStrings from './pages/Localization/LocalizationStrings';
import LocalizationWorkflow from './pages/Localization/LocalizationWorkflow';
import LocalizationSnapshots from './pages/Localization/LocalizationSnapshots';
import LocalizationJobs from './pages/Localization/LocalizationJobs';
import LocalizationOps from './pages/Localization/LocalizationOps';
import VendorJobs from './pages/Localization/Vendor/VendorJobs';
import VendorMyJob from './pages/Localization/Vendor/VendorMyJob';

function MarketplaceRedirect() {
  const location = useLocation();
  return <Navigate to={`/lab-projects/localization/jobs${location.search}`} replace />;
}

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary title="Application Route Error">
        <AuthProvider>
          <Routes>
            {/* Root — redirects to Chapters */}
            <Route
              path="/"
              element={<Navigate to="/chapters" replace />}
            />

            {/* Authentication Routes */}
            <Route
              path="/login"
              element={
                <Layout>
                  <AuthPage />
                </Layout>
              }
            />
            <Route
              path="/signup"
              element={<Navigate to="/login" replace />}
            />

            {/* Administrative User Approval Dashboard */}
            <Route
              path="/admin"
              element={<Navigate to="/admin/users" replace />}
            />
            <Route
              path="/admin/users"
              element={
                <Layout>
                  <ProtectedRoute requireAdmin>
                    <AdminDashboard />
                  </ProtectedRoute>
                </Layout>
              }
            />

          {/* Chapters / curriculum entry point */}
          <Route
            path="/chapters"
            element={
              <Layout>
                <ChaptersIndex />
              </Layout>
            }
          />
          <Route
            path="/chapters/:slug"
            element={
              <Layout>
                <LearningPathDetail />
              </Layout>
            }
          />

          {/* Backward-compatible canonical learning-path URLs */}
          <Route
            path="/learning-paths/:slug"
            element={
              <Layout>
                <LearningPathDetail />
              </Layout>
            }
          />
          <Route
            path="/learning-paths/:courseSlug/:moduleSlug/:lessonSlug"
            element={
              <Layout>
                <ChapterReader />
              </Layout>
            }
          />

          {/* Profile & Certifications */}
          <Route
            path="/profile"
            element={
              <Layout>
                <Profile />
              </Layout>
            }
          />
          <Route
            path="/certifications"
            element={<Navigate to="/profile" replace />}
          />

          {/* Legacy Compatibility Vertical Routes */}
          <Route
            path="/vertical/:id"
            element={
              <Layout>
                <VerticalDetail />
              </Layout>
            }
          />

          {/* Dedicated Lab Projects Sandbox */}
          <Route
            path="/lab-projects"
            element={
              <Layout>
                <LabProjects />
              </Layout>
            }
          />

          {/* Localization Lab — Owner Routes */}
          <Route
            path="/lab-projects/localization"
            element={
              <Layout>
                <LocalizationStrings />
              </Layout>
            }
          />
          <Route
            path="/lab-projects/localization/workflow"
            element={
              <Layout>
                <LocalizationWorkflow />
              </Layout>
            }
          />
          <Route
            path="/lab-projects/localization/snapshots"
            element={
              <Layout>
                <LocalizationSnapshots />
              </Layout>
            }
          />
          <Route
            path="/lab-projects/localization/jobs"
            element={
              <Layout>
                <LocalizationJobs />
              </Layout>
            }
          />
          {/* Old marketplace links keep working (query string, e.g. ?project=, is preserved) */}
          <Route
            path="/lab-projects/localization/marketplace"
            element={<MarketplaceRedirect />}
          />

          {/* Localization Lab — Operations (Admin Only) */}
          <Route
            path="/lab-projects/localization/ops"
            element={
              <Layout>
                <ProtectedRoute requireAdmin>
                  <LocalizationOps />
                </ProtectedRoute>
              </Layout>
            }
          />

          {/* Localization Lab — Vendor Portal Routes (Unwrapped, No Main Layout) */}
          <Route
            path="/lab-projects/localization/vendor"
            element={<VendorJobs />}
          />
          <Route
            path="/lab-projects/localization/vendor/jobs/:jobId"
            element={<VendorMyJob />}
          />

          {/* Dedicated Reading Map */}
          <Route
            path="/reading-map"
            element={
              <Layout>
                <ReadingMap />
              </Layout>
            }
          />
          <Route
            path="/progress"
            element={<Navigate to="/reading-map" replace />}
          />

          {/* Curriculum Importer */}
          <Route
            path="/curriculum-import"
            element={
              <Layout>
                <CurriculumImporter />
              </Layout>
            }
          />
          <Route
            path="/map-chapter"
            element={<Navigate to="/curriculum-import" replace />}
          />
          <Route
            path="/add-vertical"
            element={<Navigate to="/curriculum-import" replace />}
          />
          <Route
            path="/ingest"
            element={<Navigate to="/curriculum-import" replace />}
          />

          {/* Hierarchical Chapter Reader */}
          <Route
            path="/chapter/:slug"
            element={
              <Layout>
                <ChapterReader />
              </Layout>
            }
          />
          <Route
            path="/chapter/:verticalOrCourseSlug/:moduleSlug/:lessonSlug"
            element={
              <Layout>
                <ChapterReader />
              </Layout>
            }
          />
          <Route
            path="/learning"
            element={
              <Layout>
                <ChapterReader />
              </Layout>
            }
          />
          <Route
            path="/concept-chapter"
            element={<Navigate to="/chapters" replace />}
          />
        </Routes>
        </AuthProvider>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
