import React, { useState, useEffect } from "react";
import "./SemaineView.css";

function SemaineView({ week, userId, onBack }) {
  const weekdays = week.days.filter(date => {
    const dayOfWeek = new Date(date).getDay();
    return dayOfWeek !== 0 && dayOfWeek !== 6; // Exclure dimanche (0) et samedi (6)
  });

  const [daysHours, setDaysHours] = useState([]);

  useEffect(() => {
    const fetchWeekSchedule = async () => {
      try {
        const response = await fetch(`http://localhost:5000/getCal/${userId}?indexWeek=${week.weekNumber}`);
        const data = await response.json();

        if (data.calendar && data.calendar.days.length > 0) {
          setDaysHours(data.calendar.days);
        } else {
          console.warn("Aucune donnée trouvée pour cette semaine. Utilisation des horaires par défaut.");
          setDaysHours(getDefaultWeekSchedule(weekdays));
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des données de la semaine :", error);
        setDaysHours(getDefaultWeekSchedule(weekdays));
      }
    };

    fetchWeekSchedule();
  }, [week.weekNumber, userId]);

  /**
   * Génère une semaine par défaut avec des horaires de 9h à 17h.
   */
  const getDefaultWeekSchedule = (weekDays) => {
    return weekDays.map(date => ({
      date,
      startHour: 9,
      endHour: 17,
    }));
  };

  const [dragging, setDragging] = useState(null);

  useEffect(() => {
    const handleGlobalMouseUp = () => setDragging(null);
    document.addEventListener("mouseup", handleGlobalMouseUp);
    return () => document.removeEventListener("mouseup", handleGlobalMouseUp);
  }, []);

  const handleMouseDownOnHandle = (dayIndex, handleType) => {
    setDragging({ dayIndex, handleType });
  };

  const handleMouseEnterHour = (dayIndex, hour) => {
    if (!dragging || dragging.dayIndex !== dayIndex) return;

    setDaysHours(prev => {
      const newDaysHours = [...prev];
      let dayObj = { ...newDaysHours[dayIndex] };

      if (dragging.handleType === "top") {
        const newStart = Math.min(hour, dayObj.endHour - 1);
        dayObj.startHour = Math.max(newStart, 0);
      } else {
        const newEnd = hour + 1;
        dayObj.endHour = Math.min(Math.max(newEnd, dayObj.startHour + 1), 24);
      }

      newDaysHours[dayIndex] = dayObj;
      return newDaysHours;
    });
  };

  return (
    <div className="semaine-container">
      <button onClick={onBack} className="btn-back">← Retour au mois</button>
      <h2>Semaine {week.weekNumber}</h2>

      <div className="days-columns">
        {daysHours.map((dayObj, dayIndex) => {
          const { date, startHour, endHour } = dayObj;
          const dayLabel = new Date(date).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });

          return (
            <div key={date.toString()} className="day-column">
              <h3>{dayLabel}</h3>

              <div className="day-hours">
                {Array.from({ length: 24 }, (_, hour) => {
                  const isHighlighted = hour >= startHour && hour < endHour;
                  const isTopHandle = hour === startHour;
                  const isBottomHandle = hour === endHour - 1;

                  let blockClass = "hour-block";
                  if (isHighlighted) blockClass += " highlight";
                  if (isTopHandle || isBottomHandle) blockClass += " handle";

                  return (
                    <div
                      key={hour}
                      className={blockClass}
                      onMouseDown={() => {
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
    </div>
  );
}

export default SemaineView;
