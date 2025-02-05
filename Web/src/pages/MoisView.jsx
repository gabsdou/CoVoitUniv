// src/components/MoisView.jsx
import React, { useState } from "react";
import SemaineView from "./SemaineView";
import "./MoisView.css";


function MoisView({ year, monthData, onBack }) {
  const { monthName, weeks } = monthData;
  const [selectedWeek, setSelectedWeek] = useState(null);

  // Si une semaine est sélectionnée, on affiche SemaineView
  if (selectedWeek) {
    return (
      <SemaineView
        week={selectedWeek}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }

  // Sinon, on affiche la liste des semaines
  return (
    <div>
      <button onClick={onBack}>← Retour à l'année</button>
      <h2>{monthName} {year}</h2>
      <div className="weeks-grid">
          {weeks.map((week) => (
            <button
              key={week.weekNumber}
              className="week-button"
              onClick={() => setSelectedWeek(week)}
            >
              Semaine {week.weekNumber}
            </button>
          ))}
        </div>

    </div>
  );
}

export default MoisView;
