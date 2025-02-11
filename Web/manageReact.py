from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
import requests

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Base de données SQLite
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)

@app.route('/signup', methods=['POST'])
def signup():
    # Fetch the data from the json sent by react
    data = request.get_json()
    numero = data['numero_etudiant']
    password = data['password']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    is_driver = data['is_driver']

    # Store the data in the database
    new_user = User(id=numero, first_name=first_name, last_name=last_name, address=address, is_driver=is_driver)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Inscription réussie !', 'status': 'success'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    print("Received data for login:", data)  # Debug print

    numero = data['numero_etudiant']
    password = data['password']

    # Vérifier si l'utilisateur existe dans la base de données
    user = User.query.filter_by(id=numero).first()
    if user:
        # Generate a token (for simplicity, we'll just use a placeholder here)
        token = 'your_generated_token'
        return jsonify({'token': token, 'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# MOYEN SÛR FAUT TESTER TOUT CA AVEC LE FRONT

@app.route('/user/<int:id>', methods=['GET'])
def user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify({'first_name': user.first_name, 'last_name': user.last_name, 'address': user.address, 'is_driver': user.is_driver})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/passengers/<int:id>', methods=['GET'])
def passengers(id):
    users = User.query.filter_by(id!=id).all()
    passengers = []
    for user in users:
        if not user.is_driver:
            passengers.append({'first_name': user.first_name, 'last_name': user.last_name, 'address': user.address})
    return jsonify(passengers)

# MOYEN SÛR FAUT TESTER TOUT CA AVEC LE FRONT

if __name__ == '__main__':
    with app.app_context():  # Crée un contexte de l'application
        db.create_all()  # Crée la base de données si elle n'existe pas encore    app.run(debug=True)
    app.run(debug=True)
    