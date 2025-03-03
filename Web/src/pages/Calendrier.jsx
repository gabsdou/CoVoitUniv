// src/components/Calendrier2025.jsx
import React, { useState, useContext } from "react";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import isSameOrAfter from "dayjs/plugin/isSameOrAfter";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore";
import { AuthContext } from "../context/AuthContext"; // Import du contexte
import MoisView from "./MoisView";
import 'dayjs/locale/fr';
import "./Calendrier.css";
dayjs.locale('fr');

dayjs.extend(isoWeek);
dayjs.extend(isSameOrAfter);
dayjs.extend(isSameOrBefore);

const YEAR = 2025;

// Génère la liste des mois de l'année (0 = janvier, 1 = février, etc.)
const MONTH_NAMES = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
];

// Fonction pour obtenir les semaines d'un mois
function getWeeksInMonth(year, monthIndex) {
  const startOfMonth = dayjs(`${year}-${monthIndex+1}-01`).startOf("month");
  const endOfMonth = startOfMonth.endOf("month");
  const { userId } = useContext(AuthContext);

  let current = startOfMonth.startOf("isoWeek"); // Lundi
  const weeks = [];

  while (current.isSameOrBefore(endOfMonth, "day") || current.isBefore(endOfMonth.startOf("isoWeek"))) {
    const weekNumber = current.isoWeek();
    const days = Array.from({ length: 7 }, (_, i) => current.add(i, "day"));
    weeks.push({ weekNumber, days });
    current = current.add(7, "day");
  }

  return weeks;
}

function Calendrier2025({  }) {
  const { userId } = useContext(AuthContext); // Récupérer userId

  const [selectedMonth, setSelectedMonth] = useState(null);

  if (!userId) {
    return <p>Veuillez vous connecter.</p>;
  }

  // Si on a cliqué sur un mois, on affiche la vue MoisView
  if (selectedMonth !== null) {
    const monthName = MONTH_NAMES[selectedMonth];
    const weeks = getWeeksInMonth(YEAR, selectedMonth);
    const monthData = { monthIndex: selectedMonth, monthName, weeks };
    return (
      <MoisView
        year={YEAR}
        monthData={monthData}
        userId={userId}
        onBack={() => setSelectedMonth(null)}
      />
    );
  }

  // Sinon on affiche la liste des 12 mois
  return (
    <div>
      <h1>Calendrier Année {YEAR}</h1>
      <div className="months-container">
        {MONTH_NAMES.map((m, i) => (
          <div
            key={i}
            onClick={() => setSelectedMonth(i)}
            id={`month-${i}`}
            className="month-box"
          >
            {m}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Calendrier2025;
