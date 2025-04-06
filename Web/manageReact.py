from flask import Flask, request, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_cors import CORS # type: ignore
from testCovoit import geocode_address, get_route, replace_placeholders
from models import db,User,RideRequest,DriverOffer,CalendarEntry,convert_iso_string_to_calendar_slots,local_midnight_to_utc_iso, SavedAddress
from pingMail import send_offer_email,SENDER_EMAIL,SENDER_PASSWORD


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


@app.route('/user/<id>', methods=['GET'])
def user_info(id):
    user = User.query.filter_by(id=id).first()
    if user:
        return jsonify({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
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
    data = request.get_json()
    user_id = data.get("user_id")
    calendar_changes = data.get("calendar_changes")

    if not user_id or not calendar_changes:
        return jsonify({"error": "Missing user_id or calendar_changes"}), 400

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    days = calendar_changes.get("days", [])
    for day_obj in days:
        date_str = day_obj.get("date")
        if not date_str:
            continue

        iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(date_str)
        print(f"Processing date: {date_str} -> Year: {iso_year}, Week: {iso_week}, Day: {iso_day}", flush=True)

        # placeholders ...
        
        # -- RECHERCHE D'UNE ENTREE EXISTANTE --
        existing_entry = CalendarEntry.query.filter_by(
            user_id=user_id,
            year=iso_year,
            week_number=iso_week,
            day_of_week=iso_day
        ).first()
        
        if existing_entry:
            # MISE A JOUR
            existing_entry.start_hour = day_obj.get("startHour")
            existing_entry.end_hour = day_obj.get("endHour")
            existing_entry.depart_aller = replace_placeholders(day_obj.get("departAller"),user.address)
            existing_entry.destination_aller = replace_placeholders(day_obj.get("destinationAller"),user.address)
            existing_entry.depart_retour = replace_placeholders(day_obj.get("departRetour"),user.address)
            print("disabled",day_obj.get("disabled", False), flush=True)
            existing_entry.disabled=day_obj.get("disabled", False)
            existing_entry.destination_retour = replace_placeholders(day_obj.get("destinationRetour"), user.address)
            existing_entry.role_aller = day_obj.get("roleAller")
            existing_entry.role_retour = day_obj.get("roleRetour")
            existing_entry.validated_aller = day_obj.get("validatedAller", False)
            existing_entry.validated_retour = day_obj.get("validatedRetour", False)
            
        else:
            # CREATION
            print("disabled",day_obj.get("disabled", False), flush=True)
            new_entry = CalendarEntry(
                user_id=user_id,
                year=iso_year,
                week_number=iso_week,
                day_of_week=iso_day,
                start_hour=day_obj.get("startHour"),
                end_hour=day_obj.get("endHour"),
                depart_aller=replace_placeholders(day_obj.get("departAller"),user.address),
                destination_aller=replace_placeholders(day_obj.get("destinationAller"),user.address),
                depart_retour=replace_placeholders(day_obj.get("departRetour"),user.address),
                destination_retour=replace_placeholders(day_obj.get("destinationRetour"),user.address),
                disabled=day_obj.get("disabled", False),  # Si l'utilisateur a désactivé cette entrée
                role_aller=day_obj.get("roleAller"),
                role_retour=day_obj.get("roleRetour"),
                validated_aller=day_obj.get("validatedAller", False),
                validated_retour=day_obj.get("validatedRetour", False)
            )
            db.session.add(new_entry)

    db.session.commit()
    return jsonify({"message": "Calendar ISO entries upserted"}), 200



@app.route('/propagateCalendar', methods=['POST'])
def deploy_week():
    """
    Anciennement on dupliquait user.calendar[source_week] -> toutes les semaines.
    Maintenant qu'on n'a plus user.calendar, on lit la table CalendarEntry.
    On garde la même signature JSON, mais on change la logique.
    
    { "user_id": "...", "source_week": 6 }
    On copie toutes les entrées de la semaine 6 vers les semaines 1..52,
    en évitant les doublons (check de non-duplication).
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

    count_created = 0
    # Copier pour semaines 1..52
    for w_num in range(1, 53):
        for ref_e in ref_entries:
            # Vérifier s'il existe déjà une entrée pour (user_id, year, w_num, day_of_week)
            existing_entry = CalendarEntry.query.filter_by(
                user_id=user_id,
                year=ref_e.year,
                week_number=w_num,
                day_of_week=ref_e.day_of_week
            ).first()

            if existing_entry:
                # Optionnel: vous pourriez faire une mise à jour si désiré. Ici, on skip pour éviter duplication.
                continue

            # Sinon on crée une nouvelle entrée
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
                disabled=ref_e.disabled,   # <-- un-comment if your model has it

                role_aller=ref_e.role_aller,
                role_retour=ref_e.role_retour,
                validated_aller=ref_e.validated_aller,
                validated_retour=ref_e.validated_retour
            )
            db.session.add(e)
            count_created += 1

    db.session.commit()

    return jsonify({
        "message": f"Week {ref_week_number} deployed to all weeks (1..52)",
        "new_calendar_size": count_created
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
            real_date = local_midnight_to_utc_iso(e.year, e.week_number, e.day_of_week)
            # Format ISO + suffix
            date_str = real_date
        except ValueError:
            # Si e.year/e.week_number/e.day_of_week sortent du cadre ISO,
            # on peut gérer autrement, ici on met None
            date_str = None
        print("disabled",e.disabled, flush=True)
        days_list.append({
            "date": date_str,
            "startHour": e.start_hour,
            "endHour": e.end_hour,
            "departAller": e.depart_aller,
            "destinationAller": e.destination_aller,
            "departRetour": e.depart_retour,
            "destinationRetour": e.destination_retour,
            "disabled": e.disabled,
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

    # Convert day_str => iso (year, week, day_of_week)
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

    # Determine start/end hours from the calendar entry
    start_hour = entry.start_hour or 8
    end_hour = entry.end_hour or 18

    # Determine addresses
    if time_slot == "morning":
        departure_address = replace_placeholders(entry.depart_aller, user_address=user.address)
        destination_address = replace_placeholders(entry.destination_aller, user_address=user.address)
        entry.validated_aller = True
    else:
        departure_address = replace_placeholders(entry.depart_retour, user_address=user.address)
        destination_address = replace_placeholders(entry.destination_retour, user_address=user.address)
        entry.validated_retour = True

    lat, lon = geocode_address(departure_address)
    if not lat or not lon:
        return jsonify({'error': 'Unable to geocode departure address'}), 400

    # Check if a RideRequest already exists for this user & day
    existing_request = RideRequest.query.filter_by(user_id=user_id, day=day_str).first()

    if existing_request:
        # ---- Update existing request ----
        existing_request.address = departure_address
        existing_request.destination = destination_address
        existing_request.lat = lat
        existing_request.lon = lon
        existing_request.start_hour = start_hour
        existing_request.end_hour = end_hour
        db.session.commit()

        return jsonify({
            "message": "Ride request updated from calendar data",
            "ride_request_id": existing_request.id,
            "departure": departure_address,
            "destination": destination_address,
            "start_hour": start_hour,
            "end_hour": end_hour
        }), 200
    else:
        # ---- Create a new RideRequest ----
        new_request = RideRequest(
            user_id=user_id,
            day=day_str,
            address=departure_address,
            destination=destination_address,
            lat=lat,
            lon=lon,
            start_hour=start_hour,
            end_hour=end_hour
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({
            "message": "Ride request created from calendar data",
            "ride_request_id": new_request.id,
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

    # 1) Récupérer le driver (conducteur)
    driver = User.query.filter_by(id=driver_id).first()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    # Convertir la date (ex: "2025-02-03") en (year, week_number, day_of_week)
    iso_year, iso_week, iso_day = convert_iso_string_to_calendar_slots(day_str)

    # 2) Récupérer l'entrée de calendrier du driver pour ce jour
    entry = CalendarEntry.query.filter_by(
        user_id=driver_id,
        year=iso_year,
        week_number=iso_week,
        day_of_week=iso_day
    ).first()
    if not entry:
        print("No calendar data found for that day", flush=True)
        return jsonify({"possible_passengers": []}), 200

    # Récupérer les heures de début/fin dans le calendrier
    driver_start_hour = entry.start_hour
    driver_end_hour = entry.end_hour
    if driver_start_hour is None or driver_end_hour is None:
        print("Driver's start/end hours not found in calendar", flush=True)
        return jsonify({"possible_passengers": []}), 200

    # Selon "morning" ou "evening", on prend la destination du conducteur
    if time_slot.lower() == "morning":
        driver_destination = replace_placeholders(entry.destination_aller, driver.address)
        driver_departure = replace_placeholders(entry.depart_aller, driver.address)
        driver_time = driver_start_hour
    else:
        driver_destination = replace_placeholders(entry.destination_retour, driver.address)
        driver_departure = replace_placeholders(entry.depart_retour, driver.address)
        driver_time = driver_end_hour

    # Géocoder l'adresse de départ du conducteur et sa destination
    driver_coords = geocode_address(driver_departure)
    if not driver_coords:
        return jsonify({"error": "Driver's start address invalid"}), 400

    dest_coords = geocode_address(driver_destination)
    if not dest_coords:
        return jsonify({"error": "Driver's destination invalid"}), 400

    # 3) Récupérer les demandes de trajet (RideRequest) pour ce jour qui ne sont pas encore matchées
    ride_requests = RideRequest.query.filter_by(day=day_str, matched_driver_id=None).all()

    time_tolerance = 0.5  # ±0.5h => ±30 min
    possible_passengers = []
    print(f"Found {len(ride_requests)} ride requests for {day_str}", flush=True)

    for request_obj in ride_requests:
        # Récupérer l'utilisateur passager
        passenger_user = User.query.filter_by(id=request_obj.user_id).first()
        if not passenger_user:
            continue

        # 4) Récupérer l'entrée de calendrier du passager
        passenger_entry = CalendarEntry.query.filter_by(
            user_id=passenger_user.id,
            year=iso_year,
            week_number=iso_week,
            day_of_week=iso_day
        ).first()
        if not passenger_entry:
            continue  # Aucun calendrier pour ce passager ce jour-là

    

        # Selon morning/evening, on va chercher l'adresse de départ/destination et l'heure
        if time_slot.lower() == "morning":
            passenger_address = replace_placeholders(passenger_entry.depart_aller, passenger_user.address)
            passenger_destination = replace_placeholders(passenger_entry.destination_aller, passenger_user.address)
            passenger_time = passenger_entry.start_hour

            # ❗ Vérification : le passager et le conducteur doivent avoir la même destination le matin
            if passenger_destination != driver_destination:
                continue

        else:
            passenger_address = replace_placeholders(passenger_entry.depart_retour, passenger_user.address)
            passenger_destination = replace_placeholders(passenger_entry.destination_retour, passenger_user.address)
            passenger_time = passenger_entry.end_hour

            # ❗ Vérification : le passager et le conducteur doivent avoir la même adresse de départ le soir
            if passenger_address != driver_departure:
                continue

        if passenger_time is None:
            continue

        # Vérifier la tolérance horaire entre driver_time et passenger_time
        if abs(driver_time - passenger_time) > time_tolerance:
            continue

        # Géocoder les adresses du passager
        passenger_coords = geocode_address(passenger_address)
        if not passenger_coords:
            continue
        passenger_dest_coords = geocode_address(passenger_destination)
        if not passenger_dest_coords:
            continue

        # Itinéraire du conducteur jusqu'au passager
        route_to_passenger = get_route(driver_coords, passenger_coords, f"Driver->Passenger {request_obj.id}")
        if not route_to_passenger:
            continue

        # Itinéraire du passager jusqu'à la destination finale (selon son calendrier)
        route_to_destination = get_route(passenger_coords, passenger_dest_coords, "Passenger->Destination")
        if not route_to_destination:
            continue

        # Durée totale en prenant le passager
        total_duration = route_to_passenger["duration"] + route_to_destination["duration"]

        # Calculer la durée du trajet normal conducteur (direct) pour comparaison
        normal_route = get_route(driver_coords, dest_coords, "Driver->Destination")

        # Exemple d'une limite fixée à <= 6000s (~1h40), ajustez selon vos besoins
        if total_duration <= 6000:
            possible_passengers.append({
                "ride_request_id": request_obj.id,
                "passenger_id": passenger_user.id,
                "first_name": passenger_user.first_name,
                "last_name": passenger_user.last_name,
                "passenger_address": passenger_address,
                "passenger_destination": passenger_destination,
                "day": request_obj.day,
                "driver_destination": driver_destination,
                "passenger_time": passenger_time,
                "driver_time": driver_time,
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

# Route pour récupérer les adresses sauvegardées d'un utilisateur
@app.route('/user/<id>/addresses', methods=['GET'])
def get_addresses(id):
    addresses = SavedAddress.query.filter_by(user_id=id).all()
    addresses_list = [
        {'id': addr.id, 'name': addr.name, 'address': addr.address}
        for addr in addresses
    ]
    return jsonify(addresses_list)

# Route pour ajouter une nouvelle adresse
@app.route('/user/<id>/addresses', methods=['POST'])
def add_address(id):
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    if not name or not address:
        return jsonify({'error': 'Champ manquant'}), 400
    new_address = SavedAddress(name=name, address=address, user_id=id)
    db.session.add(new_address)
    db.session.commit()
    return jsonify({'message': 'Adresse ajoutée', 'id': new_address.id}), 201


if __name__ == '__main__':
    with app.app_context():
        db.init_app(app)
        db.create_all()
    app.run(debug=True)
