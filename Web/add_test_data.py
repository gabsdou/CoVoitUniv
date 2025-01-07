from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from faker import Faker
import random

# Configuration Flask et SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Fichier de base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Définition du modèle User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)

# Initialisation de la base et ajout de données
with app.app_context():
    # 1. Créer les tables (si elles n'existent pas)
    db.create_all()
    print("Tables créées.")

    # 2. Générer des utilisateurs aléatoires avec des adresses formatées
    fake = Faker("fr_FR")  # Génère des données en français
    users = []
    for _ in range(100):  # Générer 100 utilisateurs
        raw_address = fake.address()  # Adresse brute avec un saut de ligne
        formatted_address = raw_address.replace("\n", " ")  # Remplacer les sauts de ligne par un espace
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            address=formatted_address,
            is_driver=random.choice([True, False])  # Aléatoire pour "is_driver"
        )
        users.append(user)

    # 3. Ajouter à la session et valider
    db.session.add_all(users)
    db.session.commit()
    print("100 utilisateurs aléatoires insérés dans la base avec adresses formatées.")
