import React, { useState, useContext } from "react";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import isSameOrAfter from "dayjs/plugin/isSameOrAfter";
import isSameOrBefore from "dayjs/plugin/isSameOrBefore";
import { AuthContext } from "../context/AuthContext";
import MoisView from "./MoisView";
import SemaineView from "./SemaineView";
import 'dayjs/locale/fr';
import "./Calendrier.css";

dayjs.locale('fr');
dayjs.extend(isoWeek);
dayjs.extend(isSameOrAfter);
dayjs.extend(isSameOrBefore);

const YEAR = 2025;

const MONTH_NAMES = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
];

function getWeeksInMonth(year, monthIndex) {
  const startOfMonth = dayjs(`${year}-${monthIndex+1}-01`).startOf("month");
  const endOfMonth = startOfMonth.endOf("month");

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

function Calendrier2025({ }) {
  const { userId } = useContext(AuthContext);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedWeek, setSelectedWeek] = useState(null);

  if (!userId) {
    return <p>Veuillez vous connecter.</p>;
  }

  const today = dayjs();
  const currentMonthIndex = today.month();
  const weeksInMonth = getWeeksInMonth(YEAR, currentMonthIndex);
  const currentWeekData = weeksInMonth.find(week =>
    week.days.some(day => day.isSame(today, "day"))
  );

  // ** Si une semaine est sélectionnée, affiche la SemaineView **
  if (selectedWeek) {
    return (
      <SemaineView
        week={selectedWeek}
        userId={userId}
        onBack={() => setSelectedWeek(null)}
      />
    );
  }

  // ** Si un mois est sélectionné, affiche la MoisView **
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

  return (
    <div>
      <h1>Calendrier Année {YEAR}</h1>
      <button
        className="today-button"
        onClick={() => setSelectedWeek(currentWeekData)}
      >
        📅 Aller à aujourd’hui
      </button>

      <div className="months-container">
        {MONTH_NAMES.map((m, i) => (
          <div
            key={i}
            onClick={() => setSelectedMonth(i)}
            id={`month-${i}`}
            className={`month-box ${today.month() === i ? "current-month" : ""}`}
          >
            {m}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Calendrier2025;
