import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import { Link } from "react-router-dom";
import "./PassagerMap.css";
import "../leaflet-routing-machine/leaflet-routing-machine.css";
import "../leaflet/leaflet.css";
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';


const InterfacePassager = () => {
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

      const defaultIcon = L.icon({
        iconUrl: markerIcon,
        iconRetinaUrl: markerIconRetina,
        shadowUrl: markerShadow,
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });

    L.Marker.prototype.options.icon = defaultIcon;



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
        <div id="options-conducteur">
          <h2>Conducteurs Possibles</h2>
          <div id="conducteur-list"></div>
          <button id="btn">Valider</button>
        </div>
      </div>
    );
  };


  function PassagerMap() {
    return (
      <div>
        <InterfacePassager />
      </div>
    );
  }
export default PassagerMap;
