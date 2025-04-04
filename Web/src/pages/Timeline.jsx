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

  // Récupère la semaine courante + X semaines suivantes
  const fetchMultipleWeeks = async () => {
    if (!userId) return;

    try {
      const weeksToFetch = 4;              // ici, la semaine courante + 3 suivantes
      const currentWeek = dayjs().isoWeek();
      let allDays = [];

      for (let i = 0; i < weeksToFetch; i++) {
        const indexWeek = currentWeek + i;

        try {
          const response = await fetch(
            `http://localhost:5000/getCal/${userId}?indexWeek=${indexWeek}`
          );

          // Si la requête est OK, on concatène les jours
          if (response.ok) {
            const data = await response.json();
            if (data?.calendar?.days) {
              allDays = allDays.concat(data.calendar.days);
            }
          } else {
            // On ignore l'erreur pour cette semaine
            console.warn(`Impossible de récupérer la semaine ${indexWeek}.`);
          }
        } catch (err) {
          // Si la requête plante, on l'ignore également
          console.warn(
            `Erreur lors de la récupération de la semaine ${indexWeek}:`,
            err
          );
        }
      }

      // On met à jour le state avec l'ensemble de tous les jours valides
      setWeekData({ days: allDays });
    } catch (err) {
      console.error("Erreur générale:", err);
      setError("Impossible de contacter le serveur.");
    }
  };

  // Charge les données une première fois au montage / quand userId change
  useEffect(() => {
    fetchMultipleWeeks();
  }, [userId]);

  // Quand on clique pour demander un trajet ou gérer ses passagers
  const handleDayClick = async (passCond, date, mornEve) => {
    if (passCond === "conducteur") {
      return navigate("/InterfaceConducteur", { state: { passCond, mornEve, date } });
    } else {
      try {
        const response = await fetch(`http://localhost:5000/request_ride`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: userId,
            timeSlot: mornEve,
            day: date,
          }),
        });
        const data = await response.json();

        if (response.ok) {
          alert("Demande de trajet envoyée !");
          // On refait un fetch pour mettre à jour l'interface
          fetchMultipleWeeks();
        } else {
          alert(`Erreur : ${data.error}`);
        }
      } catch (error) {
        console.error("Erreur lors de l'envoi des données :", error);
        alert("Impossible de sauvegarder les modifications.");
      }
    }
  };

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
      <h1>Vos trajets (semaines à venir incluses)</h1>
      <ul className="timeline-list">
        {weekData.days
          .filter((day) => !day.disabled)
          .map((day, index) => (
            <li key={index}>
              <strong>
                {new Date(day.date).toLocaleDateString("fr-FR", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                })}
              </strong>
              <p>
                Aller : {day.departAller} → {day.destinationAller} à {day.startHour}h 
                &nbsp;|&nbsp; Rôle : {day.roleAller}
              </p>
              <p>
                Retour : {day.departRetour} → {day.destinationRetour} à {day.endHour}h
                &nbsp;|&nbsp; Rôle : {day.roleRetour}
              </p>

              <button
                onClick={() => handleDayClick(day.roleAller, day.date, "morning")}
                className="btn-nav"
                style={{
                  backgroundColor: day.validatedAller ? "green" : undefined,
                  pointerEvents: day.validatedAller ? "none" : "auto",
                  opacity: day.validatedAller ? 0.7 : 1,
                }}
              >
                {day.roleAller === "conducteur"
                  ? "Choisir mes passagers (Aller)"
                  : "Demander un trajet (Aller)"}
              </button>

              <button
                onClick={() => handleDayClick(day.roleRetour, day.date, "evening")}
                className="btn-nav"
                style={{
                  backgroundColor: day.validatedRetour ? "green" : undefined,
                  pointerEvents: day.validatedRetour ? "none" : "auto",
                  opacity: day.validatedRetour ? 0.7 : 1,
                }}
              >
                {day.roleRetour === "conducteur"
                  ? "Choisir mes passagers (Retour)"
                  : "Demander un trajet (Retour)"}
              </button>
            </li>
          ))}
      </ul>
    </div>
  );
}

export default Timeline;
