import React, { useState, useEffect } from "react";
import "./SemaineView.css";


function SemaineView({ week, onBack }) {
  /**
   * daysHours = tableau d’objets { date, startHour, endHour } pour chaque jour
   * - startHour : heure de début (ex: 9)
   * - endHour : heure de fin (exclusif, ex: 17 => plage colorée = 9h à 16h inclus)
   */
  const weekdays = week.days.filter(date => {
    const dayOfWeek = new Date(date).getDay();
    return dayOfWeek !== 0 && dayOfWeek !== 6; // Exclure dimanche (0) et samedi (6)
  });
  const [daysHours, setDaysHours] = useState(
    weekdays.map(date => ({
      date,
      startHour: 9,
      endHour: 17,
    }))
  );
  const saveCalendarData = () => {
    if (!week) {
      console.error("La variable week est undefined !");
      return;
    }

    const calendarData = {
      weekNumber: week.weekNumber,
      days: daysHours
    };

    const jsonData = JSON.stringify(calendarData, null, 2);

    const blob = new Blob([jsonData], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `calendrier_semaine_${week.weekNumber}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  const sendDataToBackend = async () => {
    const calendarData = {
      weekNumber: week.weekNumber,
      days: daysHours
    };

    try {
      const response = await fetch("http://localhost:5000/save_calendar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(calendarData),
      });

      const data = await response.json();
      alert(data.message);
    } catch (error) {
      console.error("Erreur lors de l'envoi des données:", error);
    }
  };
  /**
   * État pour savoir si on est en train de « drag » le haut ou le bas
   * - dayIndex : index du jour dans daysHours
   * - handleType : "top" ou "bottom"
   * - null = on ne fait pas de drag en ce moment
   */
  const [dragging, setDragging] = useState(null);

  useEffect(() => {
    // Au mouseup global, on arrête le drag
    const handleGlobalMouseUp = () => {
      setDragging(null);
    };
    document.addEventListener("mouseup", handleGlobalMouseUp);
    return () => {
      document.removeEventListener("mouseup", handleGlobalMouseUp);
    };
  }, []);

  /**
   * Quand on fait un mouseDown sur un bloc "handle" (haut ou bas).
   * @param {number} dayIndex index du jour
   * @param {"top"|"bottom"} handleType
   */
  const handleMouseDownOnHandle = (dayIndex, handleType) => {
    setDragging({ dayIndex, handleType });
  };

  /**
   * Quand la souris entre sur un bloc horaire (onMouseEnter),
   * si on est en drag sur le même jour, on met à jour startHour ou endHour.
   * @param {number} dayIndex
   * @param {number} hour (0..23)
   */
  const handleMouseEnterHour = (dayIndex, hour) => {
    // On ne fait rien si on n’est pas en dragging,
    // ou si ce n’est pas le jour correspondant.
    if (!dragging || dragging.dayIndex !== dayIndex) return;

    setDaysHours(prev => {
      const newDaysHours = [...prev];
      let dayObj = { ...newDaysHours[dayIndex] };

      if (dragging.handleType === "top") {
        // On veut déplacer le startHour
        // On ne peut pas dépasser endHour - 1
        // (afin de toujours avoir startHour < endHour)
        const newStart = Math.min(hour, dayObj.endHour - 1);
        dayObj.startHour = Math.max(newStart, 0); // borné à >= 0
      } else {
        // On veut déplacer le bas (endHour)
        // endHour est exclusif → on positionne sur hour+1
        // On ne peut pas être en dessous de startHour + 1
        const newEnd = hour + 1;
        dayObj.endHour = Math.min(Math.max(newEnd, dayObj.startHour + 1), 24);
      }

      newDaysHours[dayIndex] = dayObj;
      return newDaysHours;
    });
  };

  return (
    <div className="semaine-container">
      <button onClick={onBack} className="btn-back">
        ← Retour au mois
      </button>

      <h2>Semaine {week.weekNumber}</h2>

      <div className="days-columns">
        {daysHours.map((dayObj, dayIndex) => {
          const { date, startHour, endHour } = dayObj;
          const dayLabel = date.format("ddd DD/MM"); // Ex: "Lun 06/01"

          // Le bloc "top-handle" est celui correspondant à startHour
          // Le bloc "bottom-handle" est celui correspondant à endHour - 1
          const topHandleHour = startHour;
          const bottomHandleHour = endHour - 1;

          return (
            <div key={date.toString()} className="day-column">
              <h3>{dayLabel}</h3>

              <div className="day-hours">
                {Array.from({ length: 24 }, (_, hour) => {
                  const isHighlighted = hour >= startHour && hour < endHour;
                  // Est-ce le bloc du haut ?
                  const isTopHandle = hour === topHandleHour;
                  // Est-ce le bloc du bas ?
                  const isBottomHandle = hour === bottomHandleHour;

                  // On colorie en highlight si dans la plage
                  // On ajoute une classe "handle" si c’est le top ou le bottom
                  let blockClass = "hour-block";
                  if (isHighlighted) {
                    blockClass += " highlight";
                  }
                  if (isTopHandle || isBottomHandle) {
                    blockClass += " handle";
                  }

                  return (
                    <div
                      key={hour}
                      className={blockClass}
                      onMouseDown={() => {
                        // On ne déclenche que si c’est un handle
                        if (isTopHandle) {
                          handleMouseDownOnHandle(dayIndex, "top");
                        } else if (isBottomHandle) {
                          handleMouseDownOnHandle(dayIndex, "bottom");
                        }
                      }}
                      onMouseEnter={() => handleMouseEnterHour(dayIndex, hour)}
                    >
                      {hour}h
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
      <button onClick={saveCalendarData} className="btn-save">
  Enregistrer les horaires
</button>
<button onClick={sendDataToBackend} className="btn-send">
  Envoyer au serveur
</button>

    </div>
  );
}

export default SemaineView;
