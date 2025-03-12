import React, { useState, useEffect, useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

function Accueil() {
  const { isAuthenticated, logout } = useContext(AuthContext);
  return (
    <div className="page">
      <h1>CoVoitUniv</h1>
      {!isAuthenticated ? (
          <>
            <Link to="/inscription" className="nav-link nav-main">
              S'inscrire
            </Link>
            <Link to="/connexion" className="nav-link nav-main">
              Connexion
            </Link>
          </>
        ) : (
          <>
            <Link to="/calendrier" className="nav-link nav-main">
            Mon EDT
            </Link>
            <Link to="/timeline" className="nav-link nav-main">
            Mes trajets
            </Link>
          </>
        )}
      <p>
        Le covoiturage présente de nombreux avantages, notamment la réduction
        des coûts de transport, la diminution de l'empreinte carbone et la
        promotion de la convivialité entre les passagers. En partageant un
        véhicule, les utilisateurs peuvent économiser de l'argent sur le
        carburant et les frais de stationnement, tout en contribuant à la
        protection de l'environnement en réduisant le nombre de voitures sur la
        route.
      </p>
    </div>
  );
}

export default Accueil;

