import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Profile from './pages/Profile';
import VerticalDetail from './pages/VerticalDetail';
import LabProjects from './pages/LabProjects';

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
      </Routes>
    </BrowserRouter>
  );
}

export default App;

