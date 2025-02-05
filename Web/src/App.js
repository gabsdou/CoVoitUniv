import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Accueil from "./pages/Accueil";
import Inscription from "./pages/Inscription";
import Connexion from "./pages/Connexion";
import MonEDT from "./pages/MonEDT";
import ConducteurMap from "./pages/ConducteurMap";
import PassagerMap from "./pages/PassagerMap";
import Calendrier from "./pages/Calendrier";
import "./App.css";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthenticated(!!token); // Convertit en booléen (true si token existe)
  }, []);
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Accueil />} />
            <Route path="/inscription" element={<Inscription />} />
            <Route path ="/connexion" element={<Connexion />} />
            <Route path="/mon-edt" element={isAuthenticated ? <MonEDT /> : <Navigate to = "/connexion"/>} />
            <Route path="/InterfaceConducteur" element={<ConducteurMap />} />
            <Route path="/InterfacePassager" element={<PassagerMap />} />
            <Route path="/Calendrier" element={<Calendrier />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
