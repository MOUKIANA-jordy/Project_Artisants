import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const navigate = useNavigate();
  const {
    user,
    isAuthenticated,
    login,
  } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] =
    useState(false);

  if (isAuthenticated) {
    if (user?.role === "artisan") {
      return <Navigate to="/artisan" replace />;
    }

    if (user?.role === "client") {
      return <Navigate to="/client" replace />;
    }

    if (user?.role === "admin") {
      return <Navigate to="/admin" replace />;
    }

    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      const loggedUser = await login(
        email,
        password
      );

      if (loggedUser.role === "artisan") {
        navigate("/artisan", {
          replace: true,
        });
      } else if (loggedUser.role === "client") {
        navigate("/client", {
          replace: true,
        });
      } else if (loggedUser.role === "admin") {
        navigate("/admin", {
          replace: true,
        });
      } else {
        navigate("/", {
          replace: true,
        });
      }
    } catch (err) {
      console.error(err);

      setError(
        "Email ou mot de passe incorrect."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main>
      <h1>Connexion</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">
            Adresse email
          </label>

          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            required
          />
        </div>

        <div>
          <label htmlFor="password">
            Mot de passe
          </label>

          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            required
          />
        </div>

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
        >
          {submitting
            ? "Connexion..."
            : "Se connecter"}
        </button>
      </form>
    </main>
  );
}

export default Login;
