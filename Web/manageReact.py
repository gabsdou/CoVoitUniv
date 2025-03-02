from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
from testCovoit import geocode_address
import requests
import uuid
import json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Base de données SQLite
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)
    calendar = db.Column(db.Text, nullable=True)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    password = data['password']  # Should be hashed in production
    is_driver = data['is_driver']

    # Optionally geocode to get lat/lon
    lat, lon = geocode_address(address)
    if not lat or not lon:
        return jsonify({'error': 'Adresse invalide', 'status': 'error'}), 400

    # Create user without specifying id => the default UUID will be used
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        address=address,
        password=password,
        is_driver=is_driver
    )
    db.session.add(new_user)
    db.session.commit()

    # If you need to return the new user's ID:
    return jsonify({
        'message': 'Inscription réussie !',
        'status': 'success',
        'user_id': new_user.id
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    print("Received data for login:", data)  # Debug

    numero = data['numero_etudiant']
    password = data['password']

    # Retrieve user by student number
    user = User.query.filter_by(id=numero).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Compare the provided password with the one stored in DB
    # If you are hashing passwords, you’d do something like:
    # if check_password_hash(user.password, password):
    if user.password == password:
        # Generate a token (for simplicity, we'll just use a placeholder)
        token = user.id
        return jsonify({'token': token, 'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# MOYEN SÛR FAUT TESTER TOUT CA AVEC LE FRONT

@app.route('/user/<string:id>', methods=['GET'])
def user(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify({'first_name': user.first_name, 'last_name': user.last_name, 'address': user.address, 'is_driver': user.is_driver})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/passengers/<string:id>', methods=['GET'])
def passengers(id):
    users = User.query.filter_by(id!=id).all()
    passengers = []
    for user in users:
        if not user.is_driver:
            passengers.append({'first_name': user.first_name, 'last_name': user.last_name, 'address': user.address})
    return jsonify(passengers)



#Sauvegarde de calendrier
@app.route('/saveCal', methods=['POST'])
def save_calendar():
    data = request.get_json()

    # Example of JSON sent by the frontend:
    # {
    #   "user_id": 12345,
    #   "calendar_changes": {
    #       "monday": ["8:00-10:00", "14:00-16:00"],
    #       "tuesday": ["9:00-11:00"]
    #   }
    # }

    user_id = data.get('user_id')
    calendar_changes = data.get('calendar_changes')

    if not user_id or not calendar_changes:
        return jsonify({'error': 'Missing user_id or calendar_changes'}), 400

    # Retrieve the user
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Load existing calendar (if any); otherwise, start with an empty dict
    if user.calendar:
        existing_calendar = json.loads(user.calendar)
    else:
        existing_calendar = {}

    # For each day in calendar_changes, overwrite (replace) the existing data 
    # with the new data.
    #
    existing_calendar.update(calendar_changes)
  

    # Store the updated dictionary back in the database
    user.calendar = json.dumps(existing_calendar)
    db.session.commit()

    return jsonify({'message': 'Calendar updated successfully'}), 200

#permet de recuperer le calendrier pour son User
@app.route('/getCal/<string:user_id>', methods=['GET'])
def get_calendar(user_id):
   
    # Retrieve user from DB
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # If the user has a calendar saved, parse it from JSON
    if user.calendar:
        calendar_data = json.loads(user.calendar)
    else:
        # No calendar, so respond with a 200 but no data
        return jsonify({'calendar': None}), 200
    
    # Parse 'indexWeek' from the query parameters
    index_week_str = request.args.get('indexWeek', default=None, type=str)
    if not index_week_str:
        return jsonify({'error': 'Missing "indexWeek" query parameter'}), 400
    
    try:
        index_week = int(index_week_str)
    except ValueError:
        return jsonify({'error': '"indexWeek" must be an integer'}), 400

    # We now assume calendar_data is a list of "week" objects.
    # Each object might look like:
    #   { "weekNumber": 6, "days": [ ... ] }
    
    # Find the requested week by matching "weekNumber"
    requested_week = None
    for week_entry in calendar_data:
        if week_entry.get('weekNumber') == index_week:
            requested_week = week_entry
            break
    
    if not requested_week:
        # If there's no entry matching that weekNumber
        print(f'No data found for week {index_week}')

    return jsonify({'calendar': requested_week}), 200


if __name__ == '__main__':
    
    with app.app_context():# Crée un contexte de l'application
        db.drop_all()  
        db.create_all()  # Crée la base de données si elle n'existe pas encore    app.run(debug=True)
        
    app.run(debug=True)
