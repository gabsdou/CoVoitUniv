// src/components/SemaineView.jsx
import React, { useState } from "react";
import "./SemaineView.css"; // le CSS associé

function SemaineView({ week, onBack }) {
  const [daysHours, setDaysHours] = useState(
    week.days.map((date) => ({
      date,
      startHour: 9,
      endHour: 17,
    }))
  );

  const updateHour = (index, field, newValue) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      const dayObj = { ...newDaysHours[index] };

      if (field === "startHour") {
        if (newValue < dayObj.endHour) {
          dayObj.startHour = newValue;
        }
      } else if (field === "endHour") {
        if (newValue > dayObj.startHour) {
          dayObj.endHour = newValue;
        }
      }

      newDaysHours[index] = dayObj;
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
        {daysHours.map((dayObj, idx) => {
          const { date, startHour, endHour } = dayObj;
          // Format d'affichage : "Lun 06/01"
          const dayLabel = date.format("ddd DD/MM");

          return (
            <div key={date.toString()} className="day-column">
              <h3>{dayLabel}</h3>

              <div className="day-hours">
                {Array.from({ length: 24 }, (_, hour) => {
                  const isHighlighted = hour >= startHour && hour < endHour;
                  return (
                    <div
                      key={hour}
                      className={`hour-block ${isHighlighted ? "highlight" : ""}`}
                    >
                      {hour}h
                    </div>
                  );
                })}
              </div>

              <div className="sliders">
                <label>Début : {startHour}h</label>
                <input
                  type="range"
                  min={0}
                  max={23}
                  value={startHour}
                  onChange={(e) => updateHour(idx, "startHour", +e.target.value)}
                />
                <label>Fin : {endHour}h</label>
                <input
                  type="range"
                  min={1}
                  max={24}
                  value={endHour}
                  onChange={(e) => updateHour(idx, "endHour", +e.target.value)}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default SemaineView;
