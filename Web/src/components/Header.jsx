import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Header.css"; // Ajouter le fichier CSS pour styliser le header

function Header() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  // Vérifier si un token est présent au chargement du composant
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token); // Convertit en booléen (true si token existe)
  }, []);

  // Fonction de déconnexion
  const handleLogout = () => {
    localStorage.removeItem("token"); // Supprime le token
    setIsAuthenticated(false);
    navigate("/"); // Redirige vers la page d'accueil
  };
  return (
    
    <header className="header">
      <img src="/Covoit.png" alt="Logo Covoit" className="logo covoit" />
      <nav className="nav">
        <Link to="/" className="nav-link nav-accueil">
          Accueil
        </Link>
        {!isAuthenticated ? (
          <>
            <Link to="/inscription" className="nav-link nav-contact">
              S'inscrire
            </Link>
            <Link to="/connexion" className="nav-link nav-contact">
              Connexion
            </Link>
          </>
        ) : (
          <Link to="/mon-edt" className="nav-link nav-edt">
            Mon EDT
          </Link>
        )}
      </nav>
      <img src="/USPN.png" alt="Logo USPN" className="logo uspn" />
    </header>
  );
}

export default Header;
