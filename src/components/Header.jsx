import React from "react";
import { Link } from "react-router-dom";
import "./Header.css"; // Ajouter le fichier CSS pour styliser le header

function Header() {
  return (
    <header className="header">
      <img src="/Covoit.png" alt="Logo Covoit" className="logo covoit" />
      <nav className="nav">
        <Link to="/" className="nav-link nav-accueil">
          Accueil
        </Link>
        <Link to="/nous-contacter" className="nav-link nav-contact">
          Nous Contacter
        </Link>
        <Link to="/mon-edt" className="nav-link nav-edt">
          Mon EDT
        </Link>
      </nav>
      <img src="/USPN.png" alt="Logo USPN" className="logo uspn" />
    </header>
  );
}

export default Header;
