import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import { Link } from "react-router-dom";
import "./ConducteurMap.css"; // Ajouter le fichier CSS pour styliser la page ConducteurMap
import "../leaflet-routing-machine/leaflet-routing-machine.css"; // Ajouter le fichier CSS pour styliser le routage
import "../leaflet/leaflet.css"; // Ajouter le fichier CSS pour styliser la carte

const InterfaceConducteur = () => {
    useEffect(() => {
      // Initialisation de la carte
      const map = L.map("map").setView([48.8566, 2.3522], 10);

      // Ajouter le calque OpenStreetMap
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      // Simuler userData (devrait venir du backend)
      let userData = { coords: [48.8566, 2.3522] };

      // Configuration du routage
      const routingControl = L.Routing.control({
        waypoints: [
          L.latLng(userData.coords),
          L.latLng(48.956432, 2.338543), // Destination exemple
        ],
        routeWhileDragging: false,
        draggableWaypoints: true,
        addWaypoints: false,
        show: false,
      }).addTo(map);

      return () => {
        map.remove();
      };
    }, []);

    return (
      <div className="container">
        <header>

        </header>

        {/* Conteneur de la carte */}
        <div id="map" style={{ width: "1000px", height: "750px" }}></div>

        {/* Conteneur des options passagers */}
        <div id="options-passagers">
          <h2>Destinations</h2>
          <div id="destinations-list"></div>
          <button id="btn">Valider</button>
        </div>
      </div>
    );
  };


  function ConducteurMap() {
    return (
      <div>
        <InterfaceConducteur />
      </div>
    );
  }
export default ConducteurMap;
