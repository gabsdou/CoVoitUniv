from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
from testCovoit import geocode_address, get_route
import requests
import uuid
import json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Base de données SQLite
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
###########################################################################################################################################DATABASE############################################################################################################
# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)
    calendar = db.Column(db.Text, nullable=True)


class RideRequest(db.Model):
    __tablename__ = "ride_request"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)        # e.g. "2025-02-03" or "monday"
    address = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    start_hour = db.Column(db.Integer, nullable=False)    # e.g. 9
    end_hour = db.Column(db.Integer, nullable=False)      # e.g. 17

    # If a driver has agreed to pick them up, store the driver’s ID
    matched_driver_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f"<RideRequest {self.id} day={self.day} user={self.user_id}>"
    
class DriverOffer(db.Model):
    __tablename__ = "driver_offer"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    ride_request_id = db.Column(db.String(36), db.ForeignKey('ride_request.id'), nullable=False)
    status = db.Column(db.String(20), default="offered")  
    # e.g. "offered", "accepted", "declined"
    # Up to you how you handle states.

    # Optionally record timestamps, etc.

    def __repr__(self):
        return f"<DriverOffer {self.id} driver={self.driver_id} request={self.ride_request_id} status={self.status}>"

###########################################################################################################################################DATABASE############################################################################################################





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

@app.route('/requestRide', methods=['POST'])
def request_ride():
    """
    Endpoint for a PASSENGER to request a ride on a specific day, time window, and address.
    Example JSON:
    {
        "user_id": "<passenger UUID>",
        "day": "2025-02-03",
        "address": "99 Av. Jean Baptiste Clément, 93430 Villetaneuse",
        "start_hour": 9,
        "end_hour": 17
    }
    """
    data = request.get_json()
    user_id = data.get('user_id')
    day = data.get('day')
    address = data.get('address')
    start_hour = data.get('start_hour')
    end_hour = data.get('end_hour')

    # Basic validation
    if not all([user_id, day, address, start_hour is not None, end_hour is not None]):
        return jsonify({"error": "Missing required fields"}), 400

    # Geocode passenger address
    lat, lon = geocode_address(address)
    if not lat or not lon:
        return jsonify({'error': 'Adresse invalide', 'status': 'error'}), 400

    # Create a new RideRequest
    ride_request = RideRequest(
        user_id=user_id,
        day=day,
        address=address,
        lat=lat,
        lon=lon,
        start_hour=start_hour,
        end_hour=end_hour
    )
    db.session.add(ride_request)
    db.session.commit()

    return jsonify({"message": "Ride request created", "ride_request_id": ride_request.id}), 200

@app.route('/findPassengers', methods=['GET'])
def find_passengers():
    """
    For a DRIVER to find potential passengers matching a given day/time window
    (±30 minutes tolerance) and within 60 min driving distance.
    
    Query parameters:
      - driver_id: the driver's User.id (UUID)
      - day: e.g., "2025-02-03"
    """
    driver_id = request.args.get('driver_id')
    day = request.args.get('day')

    if not driver_id or not day:
        return jsonify({"error": "Missing driver_id or day"}), 400

    # Fetch the driver from the DB
    driver = User.query.filter_by(id=driver_id).first()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    # Parse the driver's calendar (assume JSON with day-based entries)
    driver_calendar = {}
    if driver.calendar:
        try:
            driver_calendar = json.loads(driver.calendar)
        except (json.JSONDecodeError, TypeError):
            pass  # if it fails, treat as empty

    # Attempt to get the driver's availability for the requested 'day'
    driver_day_data = driver_calendar.get(day)
    if not driver_day_data:
        # If the driver has no data for that day, no matches
        return jsonify({"possible_passengers": []}), 200

    # Extract the driver's start/end for the day
    # e.g. driver_day_data = {"startHour": 9, "endHour": 17}
    driver_start_hour = driver_day_data.get("startHour")
    driver_end_hour   = driver_day_data.get("endHour")

    # If driver has incomplete data, return nothing
    if driver_start_hour is None or driver_end_hour is None:
        return jsonify({"possible_passengers": []}), 200

    # Query RideRequest for all unmatched requests for the same 'day'
    ride_requests = RideRequest.query.filter_by(day=day, matched_driver_id=None).all()

    # Prepare driver coords
    driver_coords = geocode_address(driver.address)
    if not driver_coords:
        return jsonify({"error": "Driver address invalid"}), 400

    possible_passengers = []
    time_tolerance = 0.5  # 0.5 hour = 30 minutes

    for request_obj in ride_requests:
        # Compare passenger times with driver times
        p_start = request_obj.start_hour  # passenger start
        p_end   = request_obj.end_hour    # passenger end

        # If either is missing or not numeric, skip
        if p_start is None or p_end is None:
            continue

        # Check if passenger times are within ±30 min of driver's times
        start_diff = abs(driver_start_hour - p_start)
        end_diff   = abs(driver_end_hour   - p_end)
        if (start_diff > time_tolerance) or (end_diff > time_tolerance):
            # Times are too different; skip this passenger
            continue

        # If times are OK, compute route from driver to passenger
        passenger_coords = (request_obj.lat, request_obj.lon)
        if not passenger_coords or passenger_coords == (None, None):
            # No valid coords for passenger
            continue

        route_info = get_route(driver_coords, passenger_coords, f"Driver -> Passenger {request_obj.id}")
        if not route_info:
            continue  # couldn't compute route

        # route_info["duration"] is in minutes (assuming your get_route divides by 60)
        if route_info["duration"] <= 60:  # <= 1 hour
            # Get passenger user info
            passenger_user = User.query.filter_by(id=request_obj.user_id).first()
            if passenger_user:
                possible_passengers.append({
                    "ride_request_id": request_obj.id,
                    "passenger_id": passenger_user.id,
                    "first_name": passenger_user.first_name,
                    "last_name": passenger_user.last_name,
                    "address": request_obj.address,
                    "day": request_obj.day,
                    "start_hour": request_obj.start_hour,
                    "end_hour": request_obj.end_hour,
                    "route_duration_minutes": route_info["duration"],
                    "distance_km": route_info["distance"],
                    "geometry": route_info["geometry"]
                })

    return jsonify({"possible_passengers": possible_passengers}), 200


@app.route('/offerPassenger', methods=['POST'])
def offer_passenger():
    """
    A driver 'offers' a ride to a passenger's ride request.
    JSON input:
    {
      "driver_id": "<driver UUID>",
      "ride_request_id": "<RideRequest ID>"
    }
    """
    data = request.get_json()
    driver_id = data.get("driver_id")
    ride_request_id = data.get("ride_request_id")

    if not driver_id or not ride_request_id:
        return jsonify({"error": "Missing driver_id or ride_request_id"}), 400

    driver = User.query.filter_by(id=driver_id).first()
    if not driver or not driver.is_driver:
        return jsonify({"error": "Invalid driver"}), 400

    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    # Optionally check if the passenger (ride_request.user_id) is the same as the driver's ID to avoid self-offer
    if ride_request.user_id == driver_id:
        return jsonify({"error": "Cannot offer a ride to oneself"}), 400

    # Create a new DriverOffer record
    new_offer = DriverOffer(
        driver_id=driver_id,
        ride_request_id=ride_request_id,
        status="offered"
    )
    db.session.add(new_offer)
    db.session.commit()

    return jsonify({"message": "Offer created", "driver_offer_id": new_offer.id}), 200

@app.route('/rideOffers/<string:ride_request_id>', methods=['GET'])
def ride_offers(ride_request_id):
    """
    Returns all driver offers for a given ride_request_id.
    The passenger can see multiple offers and decide which to accept.
    """
    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    # You could also check if the current user is indeed the owner of the ride request
    # if current_user.id != ride_request.user_id:
    #     return jsonify({"error": "Unauthorized"}), 403

    offers = DriverOffer.query.filter_by(ride_request_id=ride_request_id).all()

    # Build a list of driver info
    offers_data = []
    for offer in offers:
        driver = User.query.filter_by(id=offer.driver_id).first()
        if driver:
            offers_data.append({
                "offer_id": offer.id,
                "driver_id": driver.id,
                "status": offer.status,
                "driver_name": f"{driver.first_name} {driver.last_name}",
                "driver_address": driver.address
            })

    return jsonify({"offers": offers_data}), 200





if __name__ == '__main__':
    
    with app.app_context():# Crée un contexte de l'application
        db.drop_all()  
        db.create_all()  # Crée la base de données si elle n'existe pas encore    app.run(debug=True)
        
    app.run(debug=True)
