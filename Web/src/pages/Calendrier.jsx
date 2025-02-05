import React, { useState } from "react";
import "./Calendrier.css";

/* ----------------------
   Sous-Composant Jour :
   Gère un emploi du temps journalier avec flèches pour ajuster l'heure de début/fin
-----------------------*/
function Jour({ dayName, onBack }) {
  const [startHour, setStartHour] = useState(9);
  const [endHour, setEndHour] = useState(17);

  const handleArrowMove = (arrow, direction) => {
    if (arrow === "start") {
      const newStartHour = Math.max(0, Math.min(23, startHour + direction));
      if (newStartHour < endHour) {
        setStartHour(newStartHour);
      }
    } else if (arrow === "end") {
      const newEndHour = Math.max(0, Math.min(23, endHour + direction));
      if (newEndHour > startHour) {
        setEndHour(newEndHour);
      }
    }
  };

  return (
    <div className="jour-container">
      <button onClick={onBack} className="btn-back">← Retour à la semaine</button>
      <h2>Planning du {dayName}</h2>

      <div className="timeline">
        {Array.from({ length: 24 }, (_, hour) => (
          <div
            key={hour}
            className={`hour ${hour >= startHour && hour <= endHour ? "selected" : ""}`}
          >
            {hour}h
          </div>
        ))}
      </div>

      <div className="controls">
        <div className="control">
          <button onClick={() => handleArrowMove("start", -1)} className="arrow">◀</button>
          <span>Début : {startHour}h</span>
          <button onClick={() => handleArrowMove("start", 1)} className="arrow">▶</button>
        </div>
        <div className="control">
          <button onClick={() => handleArrowMove("end", -1)} className="arrow">◀</button>
          <span>Fin : {endHour}h</span>
          <button onClick={() => handleArrowMove("end", 1)} className="arrow">▶</button>
        </div>
      </div>
    </div>
  );
}

/* ----------------------
   Sous-Composant Semaine :
   Affiche 7 jours (ex. Lundi à Dimanche).
   Au clic sur un jour, on "zoom" vers le planning du jour.
-----------------------*/
function Semaine({ monthName, weekIndex, onBack }) {
  const [selectedDay, setSelectedDay] = useState(null);

  // Simule des noms de jours
  const days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];

  // Si un jour est sélectionné, on affiche le planning (Jour) au lieu de la liste des jours
  if (selectedDay !== null) {
    return (
      <Jour
        dayName={days[selectedDay]}
        onBack={() => setSelectedDay(null)}
      />
    );
  }

  return (
    <div className="semaine-container">
      <button onClick={onBack} className="btn-back">← Retour au mois</button>
      <h2>Semaine {weekIndex + 1} de {monthName}</h2>
      <ul className="days-list">
        {days.map((dayName, idx) => (
          <li key={idx} onClick={() => setSelectedDay(idx)}>
            {dayName}
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ----------------------
   Sous-Composant Mois :
   Affiche 4 ou 5 semaines (simplifié ici).
   Au clic sur une semaine, on "zoom" vers la semaine sélectionnée.
-----------------------*/
function Mois({ monthIndex, onBack }) {
  const [selectedWeek, setSelectedWeek] = useState(null);

  // Liste de semaines - simplifiée à 4 ou 5 semaines
  const weeks = [0, 1, 2, 3, 4]; // (0 = Semaine 1, etc.)
  // Pour l'affichage, on simule un tableau de noms de mois
  const monthNames = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
  ];
  const monthName = monthNames[monthIndex];

  // Si une semaine est sélectionnée, on affiche directement le composant <Semaine>
  if (selectedWeek !== null) {
    return (
      <Semaine
        monthName={monthName}
        weekIndex={selectedWeek}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }

  return (
    <div className="mois-container">
      <button onClick={onBack} className="btn-back">← Retour à l'année</button>
      <h2>{monthName}</h2>
      <ul className="weeks-list">
        {weeks.map((week, idx) => (
          <li key={idx} onClick={() => setSelectedWeek(week)}>
            Semaine {week + 1}
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ----------------------
   Composant principal Calendrier :
   Vue Année (12 mois). Au clic sur un mois, on "zoom" sur le <Mois />.
-----------------------*/
function Calendrier() {
  const [selectedMonth, setSelectedMonth] = useState(null);

  // Si un mois est sélectionné, on affiche <Mois />
  if (selectedMonth !== null) {
    return (
      <Mois
        monthIndex={selectedMonth}
        onBack={() => setSelectedMonth(null)}
      />
    );
  }

  // Sinon, vue globale de l'année (les 12 mois)
  return (
    <div className="calendrier-container">
      <h1>Calendrier Annuel</h1>
      <div className="months-grid">
        {Array.from({ length: 12 }, (_, month) => (
          <div
            key={month}
            className="month-cell"
            onClick={() => setSelectedMonth(month)}
          >
            Mois {month + 1}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Calendrier;
