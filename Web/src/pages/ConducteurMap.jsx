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
    const [markers, setMarkers] = useState({});
    const [conducteurMarker, setConducteurMarker] = useState(null);
    const [destinationMarker, setDestinationMarker] = useState(null);
    const [layerGroup, setLayerGroup] = useState(null);



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
            fetch(`http://localhost:5000/user/${userId}`)
            .then(response => response.json())
            .then(data => {
                setUserData(data);

            })
                .catch(error => console.error("Erreur lors de la récupération des données utilisateur:", error));
        }
        const newLayerGroup = L.layerGroup().addTo(newMap);
        setLayerGroup(newLayerGroup);
        setMap(newMap);

        return () => newMap.remove();
    }, [userId]);
    useEffect(() => {
        if (map && conducteurMarker && destinationMarker) {
            afficherTrajet(map);
        }
    }, [map, conducteurMarker, destinationMarker, markers]);


    useEffect(() => {
        Object.values(markers).forEach(marker => {
            if (!marker._map) {
                map.removeLayer(marker);
            }
        });
    }, [markers]);

    const afficherTrajet = (map, routesData) => {
        if (!map) {
            console.error("Carte non disponible.");
            return;
        }

        const waypoints = [];

        // Ajouter le point de départ du conducteur
        if (conducteurMarker) {
            waypoints.push(conducteurMarker.getLatLng());
        }

        // Ajouter les passagers cochés comme waypoints intermédiaires
        const passagersCoches = Object.values(markers).map(marker => marker.getLatLng());
        waypoints.push(...passagersCoches);

        // Ajouter la destination finale
        if (destinationMarker) {
            waypoints.push(destinationMarker.getLatLng());
        }

        // Vérifier s'il y a au moins un trajet conducteur → destination
        if (waypoints.length < 2) {
            console.error("Impossible d'afficher un itinéraire.");
            return;
        }

        // Supprimer l'ancien itinéraire s'il existe
        if (map.routeLayer) {
            map.removeControl(map.routeLayer);
            map.routeLayer = null;
        }

        // Ajouter l'itinéraire sur la carte
        map.routeLayer = L.Routing.control({
            waypoints,
            lineOptions: { styles: [{ color: 'blue', weight: 5 }] },
            createMarker: function(i, waypoint, n) {
                if (i === 0) return L.marker(waypoint.latLng).bindPopup("Départ Conducteur");
                if (i === n - 1) return L.marker(waypoint.latLng).bindPopup("Destination Finale");
                return L.marker(waypoint.latLng).bindPopup(`Passager ${i}`);
            },
            routeWhileDragging: true,
            autoRoute: true,

        }).addTo(map);
        document.querySelector(".leaflet-routing-container")?.remove();
    };




    const fetchPassagers = async () => {
        if (!userId) return;
        if (!userId || !map) return;
        try {
            const response = await fetch(`http://localhost:5000/find_passengers`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: userId, timeslot: mornEve, day: date }),
            });

            const data = await response.json();
            console.log("Passagers récupérés :", data);

            if (!data.possible_passengers || data.possible_passengers.length === 0) {
                console.log("Aucun passager trouvé.");
                return;
            }

            setPassagers(data.possible_passengers);
            if (!map || !layerGroup) return;

            const firstPassenger = data.possible_passengers[0];
            if (!firstPassenger || !firstPassenger.routes || !firstPassenger.routes.driver_to_passenger) {
                console.error("firstPassenger ou driver_to_passenger est undefined !");
                return;
            } // Utiliser le premier passager comme référence
            if (firstPassenger) {
                const driverCoords = firstPassenger.routes.driver_to_passenger.geometry[0]; // Premier point = conducteur
                const destinationCoords = firstPassenger.routes.passenger_to_destination.geometry[1]; // Dernier point = destination

                if (!driverCoords || !destinationCoords) {
                    console.error("driverCoords ou destinationCoords est undefined !");
                    return;
                }


                // Afficher le marqueur du conducteur
                if (!conducteurMarker) {
                    const driverMarker = L.marker([driverCoords[0], driverCoords[1]])
                        .addTo(map)
                        .bindPopup("Conducteur");
                    setConducteurMarker(driverMarker);
                }

                // Afficher le marqueur de la destination
                if (!destinationMarker) {
                    const destMarker = L.marker([destinationCoords[0], destinationCoords[1]])
                        .addTo(map)
                        .bindPopup("Destination Finale");
                    setDestinationMarker(destMarker);
                }
            }
        } catch (error) {
            console.error("Erreur lors de la récupération des passagers:", error);
        }
    };



    const toggleMarker = (passager) => {
        if (!layerGroup || !map) return;

        const passengerId = passager.passenger_id;
        const passengerCoords = passager.routes.driver_to_passenger.geometry[1];

        setMarkers(prevMarkers => {
            const newMarkers = { ...prevMarkers };

            if (newMarkers[passengerId]) {
                console.log(`🗑 Suppression du marqueur du passager ${passengerId}`);
                layerGroup.removeLayer(newMarkers[passengerId]); // Suppression du marqueur
                delete newMarkers[passengerId];
            } else {
                console.log(`➕ Ajout du marqueur du passager ${passengerId}`);

                const marker = L.marker([passengerCoords[0], passengerCoords[1]])
                    .bindPopup(`${passager.first_name} ${passager.last_name} - ${passager.address}`);

                layerGroup.addLayer(marker); // Ajout dans le LayerGroup
                newMarkers[passengerId] = marker;
                // Ajuster la vue pour englober tous les marqueurs et le trajet
                const allMarkers = Object.values(newMarkers).map(marker => marker.getLatLng());

                // Ajouter le conducteur et la destination s'ils existent
                if (conducteurMarker) allMarkers.push(conducteurMarker.getLatLng());
                if (destinationMarker) allMarkers.push(destinationMarker.getLatLng());

                if (allMarkers.length > 1) {
                    const bounds = L.latLngBounds(allMarkers);
                    map.fitBounds(bounds, { padding: [50, 50] }); // Ajuster le zoom
                }
            }

            return newMarkers; // Met à jour l'état des marqueurs
        });
    };

    const handleSendOffers = async () => {
        if (!userId) {
            console.error("Utilisateur non identifié.");
            return;
        }

        const selectedPassengers = Object.keys(markers);
        if (selectedPassengers.length === 0) {
            alert("Aucun passager sélectionné !");
            return;
        }

        try {
            for (const passengerId of selectedPassengers) {
                const passenger = passagers.find(p => p.passenger_id === passengerId);
                if (!passenger) continue;

                const response = await fetch("http://localhost:5000/offerPassenger", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        driver_id: userId,
                        ride_request_id: passenger.ride_request_id
                    }),
                });

                const data = await response.json();
                if (!response.ok) {
                    console.error(`Erreur pour le passager ${passengerId}:`, data.error);
                }
                else {
                    console.log(`Offre envoyée au passager ${passengerId}.`);
                }
            }
            alert("Offres envoyées avec succès !");
        } catch (error) {
            console.error("Erreur lors de l'envoi des offres :", error);
        }
    };



    return (
        <div className="conducteur-map-container" style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
            {/* Date centrée au-dessus */}
            <h2 style={{ textAlign: "center", marginBottom: "20px" }}>
                Trajet du {new Date(date).toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                })}
            </h2>

            {/* Conteneur avec carte à gauche et passagers à droite */}
            <div style={{ display: "flex", justifyContent: "center", width: "100%", gap: "20px" }}>
                {/* Carte à gauche */}
                <div id="map" style={{ width: "70%", height: "750px" }}></div>

                {/* Liste des passagers à droite */}
                <div id="options-passagers" style={{ width: "30%", display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <h2>Passagers Disponibles</h2>
                    <button onClick={fetchPassagers}>Charger les passagers</button>
                    <div id="passagers-list" style={{ marginTop: "10px", width: "100%", textAlign: "center" }}>
                    {passagers.length > 0 ? (
                        passagers.map((passager) => (
                            <div key={passager.passenger_id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "80%" }}>
                                <p>{passager.first_name} {passager.last_name}</p>
                                <input
                                    type="checkbox"
                                    onChange={() => toggleMarker(passager)}
                                />
                            </div>
                        ))
                    ) : (
                        <p>Aucun passager trouvé.</p>
                    )}

                    </div>
                </div>
            </div>
            <button
                onClick={handleSendOffers}
                style={{ marginTop: "20px", padding: "10px", backgroundColor: "blue", color: "white", border: "none", cursor: "pointer" }}
            >
                Envoyer les offres aux passagers sélectionnés
            </button>

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
