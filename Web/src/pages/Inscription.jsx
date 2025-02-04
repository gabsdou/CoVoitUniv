import React, { useState } from "react";
import "./Inscription.css";

function Inscription() {
  const [formData, setFormData] = useState({
    numero_etudiant: "",
    last_name: "",
    first_name: "",
    address: "",
    is_driver: "",
  });

  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formData);
    setIsSubmitted(true);
  };

  return (
    <div className="page">
      <h1>Inscription</h1>
      {!isSubmitted ? (
        <form onSubmit={handleSubmit} className="form-container">
          <div className="form-group">
            <label htmlFor="numero_etudiant">Numéro Etudiant :</label>
            <input
              type="integer"
              id="numero_etudiant"
              name="numero_etudiant"
              value={formData.numero_etudiant}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="last_name">Nom :</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="first_name">Prénom :</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="address">Adresse :</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="is_driver">Conducteur? :</label>
            <input
              type="checkbox"
              id="is_driver"
              name="is_driver"
              checked={formData.is_driver}
              onChange={handleChange}
            />
          </div>
          <button type="submit" className="submit-btn">
            Envoyer
          </button>
        </form>
      ) : (
        <div className="success-message">
          <h2>Message envoyé !</h2>
        </div>
      )}
    </div>
  );
}

export default Inscription;
