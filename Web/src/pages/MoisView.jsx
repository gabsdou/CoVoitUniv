// MoisView.jsx
import React, { useState } from "react";
import SemaineView from "./SemaineView";

function MoisView({ year, monthData, onBack }) {
  const [selectedWeek, setSelectedWeek] = useState(null);
  const { monthName, weeks } = monthData;

  if (selectedWeek) {
    return (
      <SemaineView
        week={selectedWeek}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }

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
