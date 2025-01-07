import React, { useState } from "react";
import "./MonEDT.css";

function EmploiDuTemps() {
  const [startHour, setStartHour] = useState(9); // Heure de début par défaut
  const [endHour, setEndHour] = useState(17); // Heure de fin par défaut

  const handleArrowMove = (arrow, direction) => {
    if (arrow === "start") {
      const newStartHour = Math.max(0, Math.min(23, startHour + direction));
      if (newStartHour < endHour) {
        setStartHour(newStartHour);
        console.log(`début: ${newStartHour}h, fin: ${endHour}h`);
      }
    } else if (arrow === "end") {
      const newEndHour = Math.max(0, Math.min(23, endHour + direction));
      if (newEndHour > startHour) {
        setEndHour(newEndHour);
        console.log(`début: ${startHour}h, fin: ${newEndHour}h`);
      }
    }
  };

  return (
    <div className="schedule">
      <h1>Emploi du Temps</h1>
      <div className="timeline">
        {Array.from({ length: 24 }, (_, hour) => (
          <div
            key={hour}
            className={`hour ${
              hour >= startHour && hour <= endHour ? "selected" : ""
            }`}
          >
            {hour}h
          </div>
        ))}
      </div>
      <div className="controls">
        <div className="control">
          <button
            onClick={() => handleArrowMove("start", -1)}
            className="arrow"
          >
            ◀
          </button>
          <span>Début : {startHour}h</span>
          <button onClick={() => handleArrowMove("start", 1)} className="arrow">
            ▶
          </button>
        </div>
        <div className="control">
          <button onClick={() => handleArrowMove("end", -1)} className="arrow">
            ◀
          </button>
          <span>Fin : {endHour}h</span>
          <button onClick={() => handleArrowMove("end", 1)} className="arrow">
            ▶
          </button>
        </div>
      </div>
    </div>
  );
}

export default EmploiDuTemps;
