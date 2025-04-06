import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./AddAddress.css";

function AddAddress() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: "", address: "" });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:5000/user/${id}/addresses`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (res.ok) {
         setMessage("Adresse ajoutée avec succès !");
         setFormData({ name: "", address: "" });
      } else {
         setMessage(data.error || "Erreur lors de l'ajout");
      }
    } catch(error) {
         setMessage("Erreur de connexion au serveur");
    }
  };

  return (
    <div className="add-address-container">
      <h2>Ajouter une adresse</h2>
      {message && <p className="message">{message}</p>}
      <form onSubmit={handleSubmit}>
         <div className="form-group">
           <label>Nom de l'adresse :</label>
           <input 
             type="text" 
             name="name" 
             value={formData.name} 
             onChange={handleChange} 
             required 
           />
         </div>
         <div className="form-group">
           <label>Adresse :</label>
           <input 
             type="text" 
             name="address" 
             value={formData.address} 
             onChange={handleChange} 
             required 
           />
         </div>
         <button type="submit">Ajouter</button>
      </form>
      <button className="back-btn" onClick={() => navigate(-1)}>
        Retour
      </button>
    </div>
  );
}

export default AddAddress;