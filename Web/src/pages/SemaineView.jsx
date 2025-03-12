import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import ToggleSwitch from "./ToggleSwitch";
import "./SemaineView.css";

function SemaineView({ week, userId, onBack }) {
  const [showAllerInfo, setShowAllerInfo] = useState({});
  const [showRetourInfo, setShowRetourInfo] = useState({});
  const [roles, setRoles] = useState(
    week.days.reduce((acc, day) => {
      const dayOfWeek = new Date(day).getDay();
      if (dayOfWeek !== 0 && dayOfWeek !== 6) {
        acc[day] = { aller: "passager", retour: "passager" };
      }
      return acc;
    }, {})
  );
  const [daysHours, setDaysHours] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWeekSchedule = async () => {
      try {
        const response = await fetch(
          `http://localhost:5000/getCal/${userId}?indexWeek=${week.weekNumber}`
        );
        const data = await response.json();
        if (data.calendar && data.calendar.days.length > 0) {
          setDaysHours(
            data.calendar.days.map((day) => ({
              date: day.date,
              startHour: day.startHour,
              endHour: day.endHour,
              departAller: normaliserAdresse(day.departAller),
              destinationAller: normaliserAdresse(day.destinationAller),
              departRetour: normaliserAdresse(day.departRetour),
              destinationRetour: normaliserAdresse(day.destinationRetour),
            }))
          );
          setRoles(
            data.calendar.days.reduce((acc, day) => {
              acc[day.date] = {
                aller: day.roleAller || "passager",
                retour: day.roleRetour || "passager",
              };
              return acc;
            }, {})
          );
        } else {
          setDaysHours(getDefaultWeekSchedule());
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des données de la semaine :", error);
        setDaysHours(getDefaultWeekSchedule());
      }
    };
    fetchWeekSchedule();
  }, [week.weekNumber, userId]);

  const normaliserAdresse = (adresse) => {
    if (!adresse) return "Maison";
    if (adresse.includes("74 Rue Marcel Cachin, 93000 Bobigny")) return "Bobigny";
    if (adresse.includes("99 Av. Jean Baptiste Clément, 93430 Villetaneuse")) return "Villetaneuse";
    if (adresse.includes("Place du 8 Mai 1945, 93200, Saint-Denis")) return "Saint-Denis";
    return "Maison";
  };

  const getDefaultWeekSchedule = () => {
    return week.days
      .filter((date) => {
        const dayOfWeek = new Date(date).getDay();
        return dayOfWeek !== 0 && dayOfWeek !== 6;
      })
      .map((date) => ({
        date,
        startHour: 9,
        endHour: 17,
        departAller: "Maison",
        destinationAller: "Villetaneuse",
        departRetour: "Villetaneuse",
        destinationRetour: "Maison",
        roleAller: "passager",
        roleRetour: "passager",
      }));
  };

  const handleSaveWeek = async () => {
    try {
      const response = await fetch("http://localhost:5000/saveCal", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          calendar_changes: {
            weekNumber: week.weekNumber,
            days: daysHours.map((day) => ({
              date: day.date,
              startHour: day.startHour,
              endHour: day.endHour,
              departAller: day.departAller,
              destinationAller: day.destinationAller,
              roleAller: roles[day.date]?.aller || "passager",
              departRetour: day.departRetour,
              destinationRetour: day.destinationRetour,
              roleRetour: roles[day.date]?.retour || "passager",
            })),
          },
        }),
      });

      const result = await response.json();
      if (response.ok) {
        alert("Modifications enregistrées avec succès !");
      } else {
        alert(`Erreur : ${result.error}`);
      }
    } catch (error) {
      console.error("Erreur lors de l'envoi des données :", error);
      alert("Impossible de sauvegarder les modifications.");
    }
  };

  const handleDepartAllerChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].departAller = value;
      return newDaysHours;
    });
  };

  const handleDestinationAllerChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].destinationAller = value;
      return newDaysHours;
    });
  };

  const handleDepartRetourChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].departRetour = value;
      return newDaysHours;
    });
  };

  const handleDestinationRetourChange = (dayIndex, value) => {
    setDaysHours((prev) => {
      const newDaysHours = [...prev];
      newDaysHours[dayIndex].destinationRetour = value;
      return newDaysHours;
    });
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

    setDaysHours((prev) => {
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

  const handleNavigate = async (passCond, date, mornEve) => {
    if (passCond === "conducteur") {
      navigate("/InterfaceConducteur", {
        state: { userId, passCond, mornEve, date },
      });
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
        } else {
          alert(`Erreur : ${data.error}`);
        }
      } catch (error) {
        console.error("Erreur lors de l'envoi des données :", error);
        alert("Impossible de sauvegarder les modifications.");
      }
    }
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
          const dayLabel = new Date(date).toLocaleDateString("fr-FR", {
            weekday: "long",
            day: "numeric",
            month: "long",
          });

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
              <div className="day-buttons">
                <button
                  className="toggle-button"
                  onClick={() =>
                    setShowAllerInfo((prev) => ({
                      ...prev,
                      [date]: !prev[date],
                    }))
                  }
                >
                  {showAllerInfo[date] ? "Masquer Aller" : "Sélectionner infos Aller"}
                </button>

                {showAllerInfo[date] && (
                  <div className="aller-info">
                    <label htmlFor="depart-select">Départ Aller</label>
                    <br />
                    <select
                      id="depart-select"
                      value={dayObj.departAller}
                      onChange={(e) => handleDepartAllerChange(dayIndex, e.target.value)}
                    >
                      <option value="Maison">Maison</option>
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <label htmlFor="retour-select">Destination Aller</label>
                    <br />
                    <select
                      id="retour-select"
                      value={dayObj.destinationAller}
                      onChange={(e) => handleDestinationAllerChange(dayIndex, e.target.value)}
                    >
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Maison">Maison</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <div className="switch-container">
                      <label>Rôle à l'aller :</label>
                      <ToggleSwitch
                        checked={roles[dayObj.date]?.aller === "conducteur"}
                        onChange={() =>
                          setRoles((prevRoles) => ({
                            ...prevRoles,
                            [dayObj.date]: {
                              ...prevRoles[dayObj.date],
                              aller:
                                prevRoles[dayObj.date]?.aller === "conducteur"
                                  ? "passager"
                                  : "conducteur",
                            },
                          }))
                        }
                      />
                      <span className="switch-text">
                        {roles[dayObj.date]?.aller === "conducteur"
                          ? "🚗 Conducteur"
                          : "🧍 Passager"}
                      </span>
                    </div>
                  </div>
                )}

                <button
                  className="toggle-button"
                  onClick={() =>
                    setShowRetourInfo((prev) => ({
                      ...prev,
                      [date]: !prev[date],
                    }))
                  }
                >
                  {showRetourInfo[date] ? "Masquer Retour" : "Sélectionner infos Retour"}
                </button>

                {showRetourInfo[date] && (
                  <div className="retour-info">
                    <label htmlFor="depart-select-retour">Départ Retour</label>
                    <br />
                    <select
                      id="depart-select-retour"
                      value={dayObj.departRetour}
                      onChange={(e) => handleDepartRetourChange(dayIndex, e.target.value)}
                    >
                      <option value="Maison">Maison</option>
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <label htmlFor="retour-select-retour">Destination Retour</label>
                    <br />
                    <select
                      id="retour-select-retour"
                      value={dayObj.destinationRetour}
                      onChange={(e) => handleDestinationRetourChange(dayIndex, e.target.value)}
                    >
                      <option value="Villetaneuse">Villetaneuse</option>
                      <option value="Maison">Maison</option>
                      <option value="Saint-Denis">Saint-Denis</option>
                      <option value="Bobigny">Bobigny</option>
                    </select>
                    <br />

                    <div className="switch-container">
                      <label>Rôle au retour :</label>
                      <ToggleSwitch
                        checked={roles[dayObj.date]?.retour === "conducteur"}
                        onChange={() =>
                          setRoles((prevRoles) => ({
                            ...prevRoles,
                            [dayObj.date]: {
                              ...prevRoles[dayObj.date],
                              retour:
                                prevRoles[dayObj.date]?.retour === "conducteur"
                                  ? "passager"
                                  : "conducteur",
                            },
                          }))
                        }
                      />
                      <span className="switch-text">
                        {roles[dayObj.date]?.retour === "conducteur"
                          ? "🚗 Conducteur"
                          : "🧍 Passager"}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
      <button onClick={handleSaveWeek} className="btn-save">
        💾 Sauvegarder
      </button>
    </div>
  );
}

export default SemaineView;
