import React, { useEffect } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import { Link } from "react-router-dom";
import "./ConducteurMap.css";
import "../leaflet-routing-machine/leaflet-routing-machine.css";
import "../leaflet/leaflet.css";
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';


const InterfaceConducteur = () => {
    useEffect(() => {
      // Initialisation de la carte
      const map = L.map("map").setView([48.8566, 2.3522], 10);

      // Ajouter le calque OpenStreetMap
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);


      // MOYEN SUR, FAUT TESTER TOUT CA

      // Récupération de UserData (Coordonnées de l'utilisateur)
      let userData = fetch("http://localhost:3000/user/")  // TODO: récupérer le numéro de l'utilisateur connecté

      // Récupération des passagers disponibles
      let passagers = fetch("http://localhost:3000/passengers/"); // TODO: récupérer le numéro de l'utilisateur connecté

      // Traduire le json en objet
      userData = JSON.parse(userData);
      passagers = JSON.parse(passagers);

      // Ajouter un marqueur pour l'utilisateur
      L.marker(userData.coords).addTo(map).bindPopup("Vous êtes ici");

      // Ajouter tous les passagers disponibles à la liste
      const passagersList = document.getElementById("passagers-list");
      passagers.forEach((passager) => {
        const passagerElement = document.createElement("div");
        passagerElement.innerHTML = `<p>${passager.nom} ${passager.prenom}</p>`;
        passagersList.appendChild(passagerElement);
      });
      
      // MOYEN SUR, FAUT TESTER TOUT CA

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
        //IMPORTANT
        // (Optionnel) Préciser un service de routage personnalisé (OSRM, ORS, etc.)
        /*router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1/driving'
        })*/
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
          <h2>Passagers Disponibles</h2>
          <div id="passagers-list"></div>
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
