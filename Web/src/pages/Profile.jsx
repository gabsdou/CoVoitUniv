import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import "./Profile.css";

function Profile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [addresses, setAddresses] = useState([]);

  useEffect(() => {
    // Récupérer les informations du profil
    fetch(`http://localhost:5000/user/${id}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Erreur lors de la récupération des données du profil");
        }
        return res.json();
      })
      .then((data) => setProfile(data))
      .catch((err) => console.error("Erreur :", err));

    // Récupérer les adresses sauvegardées
    fetch(`http://localhost:5000/user/${id}/addresses`)
      .then((res) => {
        if (!res.ok) {
          throw new Error("Erreur lors de la récupération des adresses");
        }
        return res.json();
      })
      .then((data) => setAddresses(data))
      .catch((err) => console.error("Erreur :", err));
  }, [id]);

  if (!profile) {
    return <p>Chargement du profil...</p>;
  }

  return (
    <div className="profile-container">
      <h1>Profil de {profile.first_name} {profile.last_name}</h1>
      <p>Email : {profile.email}</p>
      <p>Adresse principale : {profile.address}</p>
      <p>Conducteur : {profile.is_driver ? "Oui" : "Non"}</p>
      
      <h2>Adresses sauvegardées</h2>
      {addresses.length === 0 ? (
        <p>Aucune adresse sauvegardée.</p>
      ) : (
        <ul>
          {addresses.map((addr) => (
            <li key={addr.id}>
              <strong>{addr.name}</strong> : {addr.address}
            </li>
          ))}
        </ul>
      )}
      
      <Link to={`/profile/${id}/add-address`} className="btn-add-address">
        Ajouter une adresse
      </Link>
    </div>
  );
}

export default Profile;