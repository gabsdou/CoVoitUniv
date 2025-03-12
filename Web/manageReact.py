from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
from testCovoit import geocode_address, get_route, replace_placeholders
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

class AddressCache(db.Model):
    __tablename__ = "address_cache"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(255), unique=True, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<AddressCache {self.address} lat={self.lat} lon={self.lon}>"
    
    
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(100),unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Plain-text or hashed
    address = db.Column(db.String(200), nullable=False)
    is_driver = db.Column(db.Boolean, default=False)
    calendar = db.Column(db.Text, nullable=True)


class RideRequest(db.Model):
    __tablename__ = "ride_request"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)        # e.g. "2025-02-03" or "monday"
    address = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
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
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    password = data['password']  # Should be hashed in production
    is_driver = data['is_driver']

    # 1) Check if email is already used
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Cette adresse e-mail est déjà utilisée.'}), 409

    # 2) Optionally geocode to get lat/lon
    lat, lon = geocode_address(address)
    if not lat or not lon:
        return jsonify({'error': 'Adresse invalide', 'status': 'error'}), 400

    # 3) Create new user
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        address=address,
        password=password,  # in production => use hashed password
        is_driver=is_driver
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'Inscription réussie !',
        'status': 'success',
        'user_id': new_user.id
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    print("Received data for login:", data)  # Debug

    numero = data['email']
    password = data['password']

    # Retrieve user by student number
    user = User.query.filter_by(email=numero).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials : no accounts found'}), 401

    # Compare the provided password with the one stored in DB
    # If you are hashing passwords, you’d do something like:
    # if check_password_hash(user.password, password):
    if user.password == password:
        # Generate a token (for simplicity, we'll just use a placeholder)
        token = user.id
        return jsonify({'token': token, 'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials : wrong password'}), 401

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
    user_id = data.get("user_id")
    calendar_changes = data.get("calendar_changes")

    if not user_id or calendar_changes is None:
        return jsonify({'error': 'Missing user_id or calendar_changes'}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Load the existing calendar from the DB (if any)
    if user.calendar:
        existing_calendar = json.loads(user.calendar)
    else:
        existing_calendar = {}

    # Merge the new data into existing_calendar
    existing_calendar.update(calendar_changes)

    # Replace placeholders, including "maison" -> user.address
    updated_calendar = replace_placeholders(existing_calendar, user.address)

    # Now store the updated dictionary back in the database
    user.calendar = json.dumps(updated_calendar)
    db.session.commit()

    return jsonify({'message': 'Calendar updated successfully'}), 200

#permet de recuperer le calendrier pour son User
@app.route('/getCal/<string:user_id>', methods=['GET'])
def get_calendar(user_id):
    calendar_data = None
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
    if calendar_data.get('weekNumber') == index_week:
        requested_week = calendar_data
    
    if not requested_week:
        # If there's no entry matching that weekNumber
        print(f'No data found for week {index_week}')

    return jsonify({'calendar': requested_week}), 200

@app.route('/request_ride', methods=['POST'])
def request_ride():
   
    data = request.get_json()
    user_id = data.get('user_id')
    day_str = data.get('day')          # e.g. "2025-02-03"
    time_slot = data.get('timeSlot')   # e.g. "morning" or "evening" (optional)

    if not user_id or not day_str:
        return jsonify({"error": "Missing user_id or day"}), 400

    # 1) Retrieve the user
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 2) Parse the user's calendar
    if not user.calendar:
        return jsonify({"error": "User has no calendar data"}), 400
    
    try:
        calendar_data = json.loads(user.calendar)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"error": "Invalid calendar format"}), 400

    
    days = calendar_data.get('days')
    if not isinstance(days, list):
        return jsonify({"error": "Calendar data missing 'days' list"}), 400

    day_info = None
    for d in days:
        # For example, if "date" is "2025-02-03T23:00:00.000Z", check if it starts with "2025-02-03"
        if isinstance(d, dict) and "date" in d:
            if day_str in d["date"]:
                day_info = d
                break

    if not day_info:
        return jsonify({"error": f"No calendar entry found for day {day_str}"}), 400

    if time_slot is None:
        time_slot = "morning"

    # Default to the times stored in day_info
    start_hour = day_info.get("startHour", 8)
    end_hour   = day_info.get("endHour", 18)

    if time_slot == "morning":
        depart_field      = "departAller"
        destination_field = "destinationAller"
    else:
        # fallback or "evening"
        depart_field      = "departRetour"
        destination_field = "destinationRetour"

    # Use the day_info fields or fallback to user.address
    departure_address    = day_info.get(depart_field, user.address)
    destination_address  = day_info.get(destination_field, user.address)

    # 5) Geocode the passenger's departure address
    lat, lon = geocode_address(departure_address)
    if not lat or not lon:
        return jsonify({'error': 'Unable to geocode departure address', 'status': 'error'}), 400

    # 6) Create a new RideRequest
    ride_request = RideRequest(
        user_id=user_id,
        day=day_str,                # e.g. "2025-02-03"
        address=departure_address,  # passenger's starting address
        destination=destination_address,
        lat=lat,
        lon=lon,
        start_hour=start_hour,
        end_hour=end_hour
    )
    db.session.add(ride_request)
    db.session.commit()

    return jsonify({
        "message": "Ride request created from calendar data",
        "ride_request_id": ride_request.id,
        "departure": departure_address,
        "destination": destination_address,
        "start_hour": start_hour,
        "end_hour": end_hour
    }), 200




@app.route('/find_passengers', methods=['POST'])
def find_passengers():
    # Parse JSON body
    print("Received JSON data:", request.get_json(),flush=True)  # Debug
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Extract required fields from JSON
    driver_id = data.get('user_id')
    day = data.get('day')
    time_slot = data.get('time_slot', 'morning')  # default to "morning" if not provided

    if not driver_id or not day:
        return jsonify({"error": "Missing required parameters ('driver_id', 'day')"}), 400

    # 1) Fetch the driver
    driver = User.query.filter_by(id=driver_id).first()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    # 2) Parse the driver's calendar
    driver_calendar = {}
    if driver.calendar:
        try:
            driver_calendar = json.loads(driver.calendar)
        except (json.JSONDecodeError, TypeError):
            return jsonify({"error": "Driver calendar is invalid JSON"}), 400

    # Example calendar structure:
    # {
    #   "weekNumber": 6,
    #   "days": [
    #     {
    #       "date": "2025-02-03T23:00:00.000Z",
    #       "startHour": 9,
    #       "endHour": 17,
    #       "matinDestination": "Villetaneuse",
    #       "soirDestination": "Bobigny"
    #     },
    #     ...
    #   ]
    # }

    days_list = driver_calendar.get("days", [])
    if not isinstance(days_list, list):
        return jsonify({"error": "Driver calendar has no valid 'days' list"}), 400

    # 3) Find the day entry matching the requested date
    day_info = None
    for d in days_list:
        if isinstance(d, dict) and "date" in d and day in d["date"]:
            day_info = d
            break
    print("Found day info:", day_info,flush=True)
    if not day_info:
        print("No calendar data found for that day",flush=True)
        return jsonify({"possible_passengers": []}), 200  # No data for that day => empty
    print("Driver's calendar entry:", day_info,flush=True)
    # 4) Extract the driver's start/end times
    driver_start_hour = day_info.get("startHour")
    driver_end_hour = day_info.get("endHour")
    if driver_start_hour is None or driver_end_hour is None:
        print("Driver's start/end hours not found",flush=True)
        return jsonify({"possible_passengers": []}), 200
    
    print(f"Driver's start hour: {driver_start_hour}, end hour: {driver_end_hour}",flush=True)
    # 5) Determine the driver's final destination from the calendar
    if time_slot.lower() == "morning":
        driver_destination = day_info.get("destinationAller")
        driver_time = driver_start_hour
    else:
        driver_destination = day_info.get("destinationRetour")
        driver_time = driver_end_hour
    print(f"Driver's destination: {driver_destination}",flush=True)
    # Fall back to the driver's stored address if none found
    if not driver_destination:
        driver_destination = driver.address

    # 6) Geocode driver's start address + final destination
    driver_coords = geocode_address(driver.address)
    if not driver_coords:
        return jsonify({"error": "Driver's start address invalid"}), 400
    print(f"Driver's start address: {driver.address}",flush=True)
    dest_coords = geocode_address(driver_destination)
    if not dest_coords:
        return jsonify({"error": "Driver's destination invalid"}), 400
    print(f"Driver's destination: {driver_destination}",
flush=True)
    # 7) Find unmatched passenger requests for that day
    ride_requests = RideRequest.query.filter_by(day=day, matched_driver_id=None).all()

    # ±30-min (0.5 hr) tolerance
    time_tolerance = 0.5
    possible_passengers = []
    print(f"Found {len(ride_requests)} ride requests for {day}",flush=True)
    for request_obj in ride_requests:
        # If "morning", compare driver's startHour with passenger's start_hour
        # If "evening", compare driver's endHour with passenger's end_hour
        passenger_time = request_obj.start_hour if (time_slot.lower() == "morning") else request_obj.end_hour
        if passenger_time is None:
            continue
        print(f"Checking passenger {request_obj.id} with time {passenger_time}",flush=True)
        # Compare times
        if abs(driver_time - passenger_time) > time_tolerance:
            continue
        print("Time match!",flush=True)
        # (Optional) check if passenger's destination matches driver's for morning
        if time_slot.lower() == "morning" and request_obj.destination != driver_destination:
            print(f"Destination mismatch {request_obj.destination} , {driver_destination}",flush=True)
            continue
        print("Destination match!",flush=True)
        # 8) Check route times
        passenger_coords = (request_obj.lat, request_obj.lon)
        if not passenger_coords or passenger_coords == (None, None):
            continue
        print(f"Found passenger {request_obj.id} at {passenger_coords}",flush=True)
        route_to_passenger = get_route(driver_coords, passenger_coords, f"Driver->Passenger {request_obj.id}")
        if not route_to_passenger:
            print(f"No route found to passenger {request_obj.id}",flush=True)
            continue
        print(f"Route to passenger {request_obj.id}: {route_to_passenger}",flush=True)
        route_to_destination = get_route(passenger_coords, dest_coords, "Passenger->Destination")
        if not route_to_destination:
            print(f"No route found from passenger {request_obj.id} to destination",flush=True)
            continue
        print(f"Route to destination: {route_to_destination}",flush=True)
        # Calculate total duration
        total_duration = route_to_passenger["duration"] + route_to_destination["duration"]
        # If total detour <= 60 minutes
        if total_duration <= 6000:
            print(f"Possible passenger: {request_obj.id}",flush=True)
            passenger_user = User.query.filter_by(id=request_obj.user_id).first()
            if passenger_user:
                possible_passengers.append({
                    "ride_request_id": request_obj.id,
                    "passenger_id": passenger_user.id,
                    "first_name": passenger_user.first_name,
                    "last_name": passenger_user.last_name,
                    "start_address": request_obj.address,
                    "passenger_destination": request_obj.destination,
                    "day": request_obj.day,
                    "start_hour": request_obj.start_hour,
                    "end_hour": request_obj.end_hour,
                    "driver_destination": driver_destination,
                    "route_duration_minutes": total_duration,
                    "routes": {
                        "driver_to_passenger": {
                            "duration": route_to_passenger["duration"],
                            "distance": route_to_passenger["distance"],
                            "geometry": route_to_passenger["geometry"]
                        },
                        "passenger_to_destination": {
                            "duration": route_to_destination["duration"],
                            "distance": route_to_destination["distance"],
                            "geometry": route_to_destination["geometry"]
                        }
                    }
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

@app.route('/rideOffers', methods=['POST'])
def ride_offers():

    # Parse JSON body
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Retrieve the ride_request_id from JSON
    ride_request_id = data.get('ride_request_id')
    if not ride_request_id:
        return jsonify({"error": "Missing 'ride_request_id' in JSON"}), 400

    # Lookup the RideRequest
    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    # (Optional) check if the current user is indeed the owner of this ride request
    # if current_user.id != ride_request.user_id:
    #     return jsonify({"error": "Unauthorized"}), 403

    # Query all offers for this ride request
    offers = DriverOffer.query.filter_by(ride_request_id=ride_request_id).all()

    # Build the list of offers
    offers_data = []
    for offer in offers:
        driver = User.query.filter_by(id=offer.driver_id).first()
        if driver:
            offers_data.append({
                "offer_id": offer.id,
                "status": offer.status,
                "driver_name": f"{driver.first_name} {driver.last_name}",
                "driver_address": driver.address
            })

    return jsonify({"offers": offers_data}), 200





if __name__ == '__main__':
    
    with app.app_context():# Crée un contexte de l'application  
        db.create_all()  # Crée la base de données si elle n'existe pas encore    app.run(debug=True)
    app.run(debug=True)
