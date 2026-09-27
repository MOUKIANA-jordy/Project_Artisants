import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
  const [status, setStatus] = useState("Connexion au backend...");

  useEffect(() => {
    api
      .get("/api/categories/")
      .then((response) => {
        console.log("Catégories :", response.data);
        setStatus("Frontend connecté au backend Django ✅");
      })
      .catch((error) => {
        console.error("Erreur API :", error);
        setStatus("Erreur de connexion au backend ❌");
      });
  }, []);

  return (
    <main style={{ padding: "40px" }}>
      <h1>Annuaire des Artisans</h1>
      <p>{status}</p>
    </main>
  );
}

export default App;
