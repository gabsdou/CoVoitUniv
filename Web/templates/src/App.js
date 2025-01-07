import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Accueil from "./pages/Accueil";
import NousContacter from "./pages/NousContacter";
import MonEDT from "./pages/MonEDT";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Accueil />} />
            <Route path="/nous-contacter" element={<NousContacter />} />
            <Route path="/mon-edt" element={<MonEDT />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
