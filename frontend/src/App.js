import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import ProtectedRoute from "./routes/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import ClientDashboard from "./pages/client/ClientDashboard";


function ArtisanDashboard() {
  const { user, logout } = useAuth();

  return (
    <main>
      <h1>Espace Artisan</h1>

      <p>
        Bienvenue {user?.first_name}.
      </p>

      <button onClick={logout}>
        Se déconnecter
      </button>
    </main>
  );
}


function AdminDashboard() {
  const { user, logout } = useAuth();

  return (
    <main>
      <h1>Administration</h1>

      <p>
        Bienvenue {user?.first_name}.
      </p>

      <button onClick={logout}>
        Se déconnecter
      </button>
    </main>
  );
}


function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* PAGE D'ACCUEIL */}
        <Route
          path="/"
          element={<Home />}
        />

        {/* CONNEXION */}
        <Route
          path="/login"
          element={<Login />}
        />

        {/* ESPACE CLIENT */}
        <Route
          element={
            <ProtectedRoute
              allowedRoles={["client"]}
            />
          }
        >
          <Route
            path="/client"
            element={<ClientDashboard />}
          />
        </Route>

        {/* ESPACE ARTISAN */}
        <Route
          element={
            <ProtectedRoute
              allowedRoles={["artisan"]}
            />
          }
        >
          <Route
            path="/artisan"
            element={<ArtisanDashboard />}
          />
        </Route>

        {/* ESPACE ADMIN */}
        <Route
          element={
            <ProtectedRoute
              allowedRoles={["admin"]}
            />
          }
        >
          <Route
            path="/admin"
            element={<AdminDashboard />}
          />
        </Route>

        {/* PAGE INCONNUE */}
        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
