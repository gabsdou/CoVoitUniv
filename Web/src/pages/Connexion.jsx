import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom"; // Pour rediriger après connexion
import { AuthContext } from "../context/AuthContext";
import "./Inscription.css";

function Connexion() {
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);
  const [formData, setFormData] = useState({
    numero_etudiant: "",
    password: "",
  });

  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        //localStorage.setItem("token", data.token);
        login(data.token);
        navigate("/calendrier");
      } else {
        setErrorMessage(data.error || "Erreur de connexion.");
      }
    } catch (error) {
      console.error("An error occurred:", error);
      setErrorMessage("Impossible de contacter le serveur.");
    }
  };

  return (
    <div className="page">
      <h1>Connexion</h1>
      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label htmlFor="numero_etudiant">Numéro Étudiant :</label>
          <input
            type="integer"
            id="numero_etudiant"
            name="numero_etudiant"
            value={formData.numero_etudiant}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Mot de Passe :</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <div className="hasAccount">
            Vous n'avez pas de compte?
            <br />
            <a href="/inscription">Inscrivez-vous</a>
          </div>
        {errorMessage && <p className="error-message">{errorMessage}</p>}
        <button type="submit" className="submit-btn">Connexion</button>
      </form>
    </div>
  );
}

export default Connexion;
