import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Profile from './pages/Profile';
import VerticalDetail from './pages/VerticalDetail';
import LabProjects from './pages/LabProjects';
import ChapterReader from './pages/ChapterReader';
import CurriculumImporter from './pages/CurriculumImporter';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout>
              <Home />
            </Layout>
          }
        />
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
        <Route
          path="/vertical/:id"
          element={
            <Layout>
              <VerticalDetail />
            </Layout>
          }
        />
        <Route
          path="/lab-projects"
          element={
            <Layout>
              <LabProjects />
            </Layout>
          }
        />
        <Route
          path="/reading-map"
          element={
            <Layout>
              <LabProjects />
            </Layout>
          }
        />
        <Route
          path="/progress"
          element={<Navigate to="/reading-map" replace />}
        />
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
          element={
            <Layout>
              <CurriculumImporter />
            </Layout>
          }
        />
        <Route
          path="/add-vertical"
          element={
            <Layout>
              <CurriculumImporter />
            </Layout>
          }
        />
        <Route
          path="/ingest"
          element={<Navigate to="/curriculum-import" replace />}
        />
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
          element={<Navigate to="/chapter/structured-concurrency" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

