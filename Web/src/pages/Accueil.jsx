import React from "react";
import { Link } from "react-router-dom";

function Accueil() {
  return (
    <div className="page">
      <h1>Bienvenue sur notre site</h1>
      <Link to="/inscription" className="nav-link nav-main">
        S'inscrire
      </Link>
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
