import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import VerticalDetail from './pages/VerticalDetail';

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
          path="/vertical/:id"
          element={
            <Layout>
              <VerticalDetail />
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
