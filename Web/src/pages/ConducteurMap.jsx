import React, { useEffect, useState, useContext } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { useLocation } from "react-router-dom";
import "./ConducteurMap.css";
import "../leaflet-routing-machine/leaflet-routing-machine.css";
import "../leaflet/leaflet.css";
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const InterfaceConducteur = () => {
    const { userId } = useContext(AuthContext);
    const [passagers, setPassagers] = useState([]);
    const [map, setMap] = useState(null);
    const location = useLocation();
    const {passCond, date , mornEve} = location.state || {}; // Récupérer les données passées
    //fix bug des icones
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: markerIconRetina,
        iconUrl: markerIcon,
        shadowUrl: markerShadow
    });

    const [userData, setUserData] = useState(null);

    useEffect(() => {
        const newMap = L.map("map").setView([48.8566, 2.3522], 10);
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(newMap);
        setMap(newMap);

        // Récupération des données utilisateur
        if (userId) {
            fetch(`http://localhost:3000/user/${userId}`)
                .then(response => response.json())
                .then(data => {
                    setUserData(data);
                    L.marker(data.coords).addTo(newMap).bindPopup("Vous êtes ici");
                })
                .catch(error => console.error("Erreur lors de la récupération des données utilisateur:", error));
        }

        return () => newMap.remove();
    }, [userId]);
    const afficherTrajet = (map, routesData) => {
      if (!map || !routesData) return;

      // Supprimer les anciens itinéraires s'ils existent
      if (map.routeLayer) {
          map.removeControl(map.routeLayer);
      }

      // Récupérer les trajets
      const driverToPassengerCoords = routesData.routes.driver_to_passenger.geometry;
      const passengerToDestinationCoords = routesData.routes.passenger_to_destination.geometry;

      // Fonction pour convertir les coordonnées GeoJSON en format Leaflet
      const convertirCoordonnees = (geoJsonCoords) => {
          return geoJsonCoords.map(coord => [coord[1], coord[0]]); // Inverser lat/lon
      };

      const route1 = convertirCoordonnees(driverToPassengerCoords);
      const route2 = convertirCoordonnees(passengerToDestinationCoords);

      // Ajouter les trajets à la carte avec Leaflet Routing Machine
      map.routeLayer = L.Routing.control({
          waypoints: [
              L.latLng(route1[0]), // Départ du conducteur
              L.latLng(route1[route1.length - 1]), // Arrivée chez le passager
              L.latLng(route2[route2.length - 1])  // Destination finale du passager
          ],
          createMarker: function() { return null; }, // Pas de marqueurs par défaut
          routeWhileDragging: true
      }).addTo(map);
  };


    const fetchPassagers = async () => {
        if (!userId) return;
        try {

            const response = await fetch(`http://localhost:5000/find_passengers/`


              , {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ user_id: userId, timeslot: mornEve, day: date }),}
            );
            const data = await response.json();
            console.log(data);
            if (data.possible_passengers.length === 0) {
              console.log("Aucun passager trouvé.");
              return;
            }
            setPassagers(data.possible_passengers);

            // Ajouter des marqueurs sur la carte pour les passagers
            data.possible_passengers.forEach(passager => {
              if (passager.geometry) {
                  L.marker([passager.geometry[1], passager.geometry[0]])
                   .addTo(map)
                   .bindPopup(`${passager.first_name} ${passager.last_name}`);
              }
          });

          // Afficher les trajets sur la carte
          afficherTrajet(map, data);
        } catch (error) {
            console.error("Erreur lors de la récupération des passagers:", error);
        }
    };

    return (
        <div className="container">
            <header></header>
            <div id="map" style={{ width: "1000px", height: "750px" }}></div>
            <div id="options-passagers">
                <h2>Passagers Disponibles</h2>
                <button onClick={fetchPassagers}>Charger les passagers</button>
                <div id="passagers-list">
                    {passagers.map((passager, index) => (
                        <p key={index}>{passager.first_name} {passager.last_name}</p>
                    ))}
                </div>
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
