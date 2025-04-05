from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
from testCovoit import geocode_address, get_route, replace_placeholders
from models import db,User,RideRequest,DriverOffer,CalendarEntry,convert_iso_string_to_calendar_slots  # <-- your models
from pingMail import send_offer_email,SENDER_EMAIL,SENDER_PASSWORD
import requests
import uuid
import json



# Importez vos fonctions utilitaires et vos modèles depuis un autre fichier, p. ex.:
# from models import db, User, RideRequest, DriverOffer, CalendarEntry, convert_iso_string_to_calendar_slots
# from testCovoit import geocode_address, get_route, replace_placeholders
# from pingMail import send_offer_email, SENDER_EMAIL, SENDER_PASSWORD

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# db.init_app(app)  # à faire si vous utilisez SQLAlchemy / models init_app

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    address = data['address']
    password = data['password']
    is_driver = data['is_driver']

    # Vérifier email unique
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Cette adresse e-mail est déjà utilisée.'}), 409

    # Geocode
    lat, lon = geocode_address(address)
    if not lat or not lon:
        return jsonify({'error': 'Adresse invalide', 'status': 'error'}), 400

    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        address=address,
        password=password,
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
    print("Received data for login:", data)

    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials : no accounts found'}), 401

    if user.password == password:
        token = user.id
        return jsonify({'token': token, 'status': 'success'})
    else:
        return jsonify({'error': 'Invalid credentials : wrong password'}), 401


@app.route('/user/<string:id>', methods=['GET'])
def user_info(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address,
            'is_driver': user.is_driver
        })
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/passengers/<string:id>', methods=['GET'])
def passengers(id):
    # Récupère tous les users sauf celui dont l'id == id
    users = User.query.filter(User.id != id).all()
    passengers_list = []
    for u in users:
        if not u.is_driver:
            passengers_list.append({
                'first_name': u.first_name,
                'last_name': u.last_name,
                'address': u.address
            })
    return jsonify(passengers_list)


###############################################################################
# Nouveau stockage du calendrier : via la table CalendarEntry (pas user.calendar)
###############################################################################

@app.route('/saveCal', methods=['POST'])
def save_calendar_iso():
    """
    Le front envoie toujours un JSON :
    {
      "user_id": "...",
      "calendar_changes": {
        "weekNumber": 14,
        "days": [
          { "date": "2025-03-30T22:00:00.000Z", "startHour": 9, ... },
          ...
        ]
      }
    }
    On insère dans CalendarEntry pour chaque 'day'.
    """
    data = request.get_json()
    user_id = data.get("user_id")
    calendar_changes = data.get("calendar_changes")

    if not user_id or not calendar_changes:
        return jsonify({"error": "Missing user_id or calendar_changes"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    days = calendar_changes.get("days", [])

    # On peut éventuellement supprimer d'anciennes entrées de la même semaine
    # si on veut "remplacer" complètement. A vous de décider.
    # ex: old_week = calendar_changes["weekNumber"]
    # CalendarEntry.query.filter_by(user_id=user_id, week_number=old_week).delete()

    for day_obj in days:
        date_str = day_obj.get("date")
        if not date_str:
            continue

        iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(date_str)

        # placeholders "Maison" => user.address, par ex.
        if day_obj.get("departAller") == "Maison":
            day_obj["departAller"] = user.address
        if day_obj.get("destinationAller") == "Maison":
            day_obj["destinationAller"] = user.address
        if day_obj.get("departRetour") == "Maison":
            day_obj["departRetour"] = user.address
        if day_obj.get("destinationRetour") == "Maison":
            day_obj["destinationRetour"] = user.address

        new_entry = CalendarEntry(
            user_id=user_id,
            year=iso_year,
            week_number=iso_week,
            day_of_week=iso_day,
            start_hour=day_obj.get("startHour"),
            end_hour=day_obj.get("endHour"),
            depart_aller=day_obj.get("departAller"),
            destination_aller=day_obj.get("destinationAller"),
            depart_retour=day_obj.get("departRetour"),
            destination_retour=day_obj.get("destinationRetour"),
            role_aller=day_obj.get("roleAller"),
            role_retour=day_obj.get("roleRetour"),
            validated_aller=day_obj.get("validatedAller", False),
            validated_retour=day_obj.get("validatedRetour", False)
        )
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({"message": "Calendar ISO entries saved"}), 200


@app.route('/propagateCalendar', methods=['POST'])
def deploy_week():
    """
    Anciennement on dupliquait user.calendar[source_week] -> toutes les semaines.
    Maintenant qu'on n'a plus user.calendar, on doit lire la table CalendarEntry.
    On garde la même signature JSON, mais on change la logique.
    
    { "user_id": "...", "source_week": 6 }
    On copie toutes les entrées de la semaine 6 vers les semaines 1..52
    """
    data = request.get_json()
    user_id = data.get("user_id")
    ref_week_number = data.get("source_week")

    if not user_id or ref_week_number is None:
        return jsonify({"error": "Missing user_id or week_number"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Récupérer toutes les entrées de la semaine source
    ref_entries = CalendarEntry.query.filter_by(user_id=user_id, week_number=ref_week_number).all()
    if not ref_entries:
        return jsonify({"error": f"No data found for source_week {ref_week_number}"}), 400

    # Copie pour semaines 1..52
    # Vous pouvez ignorer la source_week = 6 si vous voulez éviter de la dupliquer sur elle-même
    for w_num in range(1, 53):
        for ref_e in ref_entries:
            # deep copy
            e = CalendarEntry(
                user_id=user_id,
                year=ref_e.year,  # on garde l'année telle quelle
                week_number=w_num,
                day_of_week=ref_e.day_of_week,

                start_hour=ref_e.start_hour,
                end_hour=ref_e.end_hour,
                depart_aller=ref_e.depart_aller,
                destination_aller=ref_e.destination_aller,
                depart_retour=ref_e.depart_retour,
                destination_retour=ref_e.destination_retour,
                role_aller=ref_e.role_aller,
                role_retour=ref_e.role_retour,
                validated_aller=ref_e.validated_aller,
                validated_retour=ref_e.validated_retour
            )
            db.session.add(e)
    db.session.commit()

    return jsonify({
        "message": f"Week {ref_week_number} deployed to all weeks (1..52)",
        "new_calendar_size": 52 * len(ref_entries)
    }), 200


@app.route('/getCal/<string:user_id>', methods=['GET'])
def get_calendar(user_id):
    """
    L'endpoint acceptait ?indexWeek=...
    On récupère toutes les entrées (CalendarEntry) pour user_id + week_number=indexWeek,
    et on reconstruit:
    {
      "weekNumber": <indexWeek>,
      "days": [
        {
          "date": "...",
          "startHour": ...,
          "endHour": ...,
          "departAller": ...,
          ...
        },
        ...
      ]
    }
    En recalcule la date via fromisocalendar.
    """
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    index_week_str = request.args.get('indexWeek', default=None, type=str)
    if not index_week_str:
        return jsonify({'error': 'Missing "indexWeek" query parameter'}), 400

    try:
        index_week = int(index_week_str)
    except ValueError:
        return jsonify({'error': '"indexWeek" must be an integer'}), 400

    # On récupère toutes les entrées pour la "weekNumber" demandée
    entries = CalendarEntry.query.filter_by(user_id=user_id, week_number=index_week).all()
    if not entries:
        print(f"No data found for week {index_week}")
        return jsonify({'calendar': None}), 200

    days_list = []
    for e in entries:
        # Recalcule la date via fromisocalendar
        # day_of_week: 1..7 (1=lundi, 7=dimanche)
        # week_number: 1..53
        import datetime
        try:
            real_date = datetime.date.fromisocalendar(e.year, e.week_number, e.day_of_week)
            # Format ISO + suffix
            date_str = real_date.isoformat() + "T00:00:00.000Z"
        except ValueError:
            # Si e.year/e.week_number/e.day_of_week sortent du cadre ISO,
            # on peut gérer autrement, ici on met None
            date_str = None

        days_list.append({
            "date": date_str,
            "startHour": e.start_hour,
            "endHour": e.end_hour,
            "departAller": e.depart_aller,
            "destinationAller": e.destination_aller,
            "departRetour": e.depart_retour,
            "destinationRetour": e.destination_retour,
            "roleAller": e.role_aller,
            "roleRetour": e.role_retour,
            "validatedAller": e.validated_aller,
            "validatedRetour": e.validated_retour
        })

    requested_week = {
        "weekNumber": index_week,
        "days": days_list
    }
    return jsonify({'calendar': requested_week}), 200



@app.route('/request_ride', methods=['POST'])
def request_ride():
    data = request.get_json()
    user_id = data.get('user_id')
    day_str = data.get('day')  # ex. "2025-02-03"
    time_slot = data.get('timeSlot')  # "morning" ou "evening"

    if not user_id or not day_str:
        return jsonify({"error": "Missing user_id or day"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Convert day_str => iso
    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)
    entry = CalendarEntry.query.filter_by(
        user_id=user_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()
    if not entry:
        return jsonify({"error": f"No calendar entry found for day {day_str}"}), 400

    if not time_slot:
        time_slot = "morning"

    start_hour = entry.start_hour or 8
    end_hour = entry.end_hour or 18

    if time_slot == "morning":
        departure_address = entry.depart_aller or user.address
        destination_address = entry.destination_aller or user.address
        entry.validated_aller = True
    else:
        departure_address = entry.depart_retour or user.address
        destination_address = entry.destination_retour or user.address
        entry.validated_retour = True

    lat, lon = geocode_address(departure_address)
    if not lat or not lon:
        return jsonify({'error': 'Unable to geocode departure address'}), 400

    ride_request = RideRequest(
        user_id=user_id,
        day=day_str,
        address=departure_address,
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
    print("Received JSON data:", request.get_json(), flush=True)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    driver_id = data.get('user_id')
    day_str = data.get('day')
    time_slot = data.get('time_slot', 'morning')

    if not driver_id or not day_str:
        return jsonify({"error": "Missing required parameters ('driver_id', 'day')"}), 400

    driver = User.query.filter_by(id=driver_id).first()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)
    entry = CalendarEntry.query.filter_by(
        user_id=driver_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()
    if not entry:
        print("No calendar data found for that day", flush=True)
        return jsonify({"possible_passengers": []}), 200

    driver_start_hour = entry.start_hour
    driver_end_hour = entry.end_hour
    if driver_start_hour is None or driver_end_hour is None:
        print("Driver's start/end hours not found", flush=True)
        return jsonify({"possible_passengers": []}), 200

    if time_slot.lower() == "morning":
        driver_destination = entry.destination_aller or driver.address
        driver_time = driver_start_hour
    else:
        driver_destination = entry.destination_retour or driver.address
        driver_time = driver_end_hour

    driver_coords = geocode_address(driver.address)
    if not driver_coords:
        return jsonify({"error": "Driver's start address invalid"}), 400
    dest_coords = geocode_address(driver_destination)
    if not dest_coords:
        return jsonify({"error": "Driver's destination invalid"}), 400

    ride_requests = RideRequest.query.filter_by(day=day_str, matched_driver_id=None).all()

    time_tolerance = 0.5  # ±30 min
    possible_passengers = []
    print(f"Found {len(ride_requests)} ride requests for {day_str}", flush=True)

    for request_obj in ride_requests:
        passenger_time = (request_obj.start_hour
                          if time_slot.lower() == "morning"
                          else request_obj.end_hour)
        if passenger_time is None:
            continue

        if abs(driver_time - passenger_time) > time_tolerance:
            continue

        if time_slot.lower() == "morning":
            # Comparer destinations
            if request_obj.destination != driver_destination:
                continue

        passenger_coords = (request_obj.lat, request_obj.lon)
        if not passenger_coords or passenger_coords == (None, None):
            continue

        route_to_passenger = get_route(driver_coords, passenger_coords, f"Driver->Passenger {request_obj.id}")
        if not route_to_passenger:
            continue
        route_to_destination = get_route(passenger_coords, dest_coords, "Passenger->Destination")
        if not route_to_destination:
            continue

        total_duration = route_to_passenger["duration"] + route_to_destination["duration"]
        # Dans l'ancien code, vous aviez <= 6000 => ~1h40
        # Ajustez selon la logique désirée
        if total_duration <= 6000:
            passenger_user = User.query.filter_by(id=request_obj.user_id).first()
            if passenger_user:
                normal_route = get_route(driver_coords, dest_coords, "Driver->Destination")
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
                    "passengers_duration": total_duration,
                    "normal_duration": normal_route["duration"] if normal_route else None,
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
    data = request.get_json()
    driver_id = data.get("driver_id")
    ride_request_id = data.get("ride_request_id")
    departure_hour = data.get("departure_hour")
    if not driver_id or not ride_request_id:
        return jsonify({"error": "Missing driver_id or ride_request_id"}), 400

    driver = User.query.filter_by(id=driver_id).first()
    if not driver or not driver.is_driver:
        return jsonify({"error": "Invalid driver"}), 400

    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    if ride_request.user_id == driver_id:
        return jsonify({"error": "Cannot offer a ride to oneself"}), 400

    new_offer = DriverOffer(
        driver_id=driver_id,
        ride_request_id=ride_request_id,
        departure_hour=departure_hour,
        status="offered"
    )

    passenger = User.query.filter_by(id=ride_request.user_id).first()
    if passenger and passenger.email:
        send_offer_email(
            driver=driver,
            passenger=passenger,
            deparure_hour=departure_hour,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD
        )

    db.session.add(new_offer)
    db.session.commit()

    return jsonify({"message": "Offer created", "driver_offer_id": new_offer.id}), 200


@app.route('/rideOffers', methods=['POST'])
def ride_offers():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    ride_request_id = data.get('ride_request_id')
    if not ride_request_id:
        return jsonify({"error": "Missing 'ride_request_id' in JSON"}), 400

    ride_request = RideRequest.query.filter_by(id=ride_request_id).first()
    if not ride_request:
        return jsonify({"error": "Ride request not found"}), 404

    offers = DriverOffer.query.filter_by(ride_request_id=ride_request_id).all()

    offers_data = []
    for off in offers:
        driver = User.query.filter_by(id=off.driver_id).first()
        if driver:
            offers_data.append({
                "offer_id": off.id,
                "status": off.status,
                "driver_name": f"{driver.first_name} {driver.last_name}",
                "driver_address": driver.address
            })

    return jsonify({"offers": offers_data}), 200


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True)
