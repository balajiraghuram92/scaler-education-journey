import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Profile from './pages/Profile';
import VerticalDetail from './pages/VerticalDetail';
import LabProjects from './pages/LabProjects';
import ReadingMap from './pages/ReadingMap';
import ChapterReader from './pages/ChapterReader';
import CurriculumImporter from './pages/CurriculumImporter';
import ChaptersIndex from './pages/ChaptersIndex';
import LearningPathDetail from './pages/LearningPath/LearningPathDetail';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary title="Application Route Error">
        <Routes>
          {/* Root — redirects to Chapters */}
          <Route
            path="/"
            element={<Navigate to="/chapters" replace />}
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
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
