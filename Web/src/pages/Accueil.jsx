import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import "./Accueil.css"; // Ajout du fichier CSS

function Accueil() {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <div className="accueil-container">
      {/* Section de bienvenue */}
      <div className="hero">
        <h1>🚗 CoVoitUniv</h1>
        <p className="subtitle">
          Partagez vos trajets et simplifiez vos déplacements universitaires.
        </p>
      </div>

      {/* Boutons de connexion / inscription ou accès aux trajets */}
      <div className="buttons-container">
        {!isAuthenticated ? (
          <>
            <Link to="/inscription" className="btn primary-btn">
              S'inscrire
            </Link>
            <Link to="/connexion" className="btn secondary-btn">
              Connexion
            </Link>
          </>
        ) : (
          <>
            <Link to="/calendrier" className="btn primary-btn">
              Mon emploi du temps
            </Link>
            <Link to="/timeline" className="btn secondary-btn">
              Mes trajets
            </Link>
          </>
        )}
      </div>

      {/* Avantages du covoiturage */}
      <div className="features">
        <h2>Pourquoi choisir CoVoitUniv ?</h2>
        <div className="feature-box">
          <div className="feature">
            <h3>💰 Économie</h3>
            <p>Réduisez vos coûts de transport en partageant les trajets.</p>
          </div>
          <div className="feature">
            <h3>🌍 Écologie</h3>
            <p>Diminuez votre empreinte carbone en limitant le nombre de voitures.</p>
          </div>
          <div className="feature">
            <h3>🤝 Convivialité</h3>
            <p>Voyagez ensemble et créez de nouvelles rencontres.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Accueil;
