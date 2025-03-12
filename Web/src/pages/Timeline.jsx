import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import { useNavigate } from "react-router-dom";

import "./Timeline.css";

dayjs.extend(isoWeek);

function Timeline() {
    const { userId } = useContext(AuthContext);
    const [weekData, setWeekData] = useState(null);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const handleDayClick  = async (passCond, date, mornEve) => {
        if(passCond === "conducteur") {
            return navigate("/InterfaceConducteur", { state: {passCond, mornEve, date } });
        }
        else {
            try {
              const response = await fetch(`http://localhost:5000/request_ride`
              , {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  user_id: userId,
                  timeSlot: mornEve,
                  day : date }),
              }
              );
              const data = await response.json();
              if (response.ok) {
                alert("Demande de trajet envoyée !");
              } else {
                alert(`Erreur : ${data.error}`);
              }
            }
            catch (error) {
              console.error("Erreur lors de l'envoi des données :", error);
              alert("Impossible de sauvegarder les modifications.");
          }
          }
        return

    };
    useEffect(() => {
        if (!userId) return;

        // 🔹 Calculer la semaine actuelle
        const currentWeek = dayjs().isoWeek();



        const fetchWeekData = async () => {
            try {
                const response = await fetch(`http://localhost:5000/getCal/${userId}?indexWeek=${currentWeek}`);
                const data = await response.json();

                if (response.ok) {
                    setWeekData(data.calendar);
                } else {
                    setError(data.error || "Erreur lors de la récupération des trajets.");
                }
            } catch (err) {
                console.error("Erreur:", err);
                setError("Impossible de contacter le serveur.");
            }
        };

        fetchWeekData();
    }, [userId]);

    if (!userId) {
        return <p>Veuillez vous connecter pour voir vos trajets.</p>;
    }

    if (error) {
        return <p>{error}</p>;
    }

    if (!weekData || !weekData.days) {
        return <p>Chargement des trajets...</p>;
    }

    return (
        <div className="timeline-container">
            <h1>Vos trajets de la semaine</h1>
            <ul className="timeline-list">
                {weekData.days.map((day, index) => (
                    <li key={index}>
                        <strong>
                            {new Date(day.date).toLocaleDateString("fr-FR", {
                                weekday: "long",
                                day: "numeric",
                                month: "long",
                            })}
                        </strong>
                        <p>Aller : {day.departAller} → {day.destinationAller} à {day.startHour}h, Role : {day.roleAller}</p>
                        <p>Retour : {day.departRetour} → {day.destinationRetour} à {day.endHour}h, Role : {day.roleRetour}</p>

                        {/* Ajout des boutons */}
                        <button
                            onClick={() => handleDayClick(day.roleAller, day.date, "morning")}
                            className="btn-nav"
                        >
                            {day.roleAller === "conducteur" ? "Choisir mes passagers (Aller)" : "Demander un trajet (Aller)"}
                        </button>

                        <button
                            onClick={() => handleDayClick(day.roleRetour, day.date, "evening")}
                            className="btn-nav"
                        >
                            {day.roleRetour === "conducteur" ? "Choisir mes passagers (Retour)" : "Demander un trajet (Retour)"}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Timeline;
