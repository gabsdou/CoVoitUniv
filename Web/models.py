from flask_sqlalchemy import SQLAlchemy
import uuid
import datetime
from dateutil.parser import parse
db = SQLAlchemy()



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
    departure_hour = db.Column(db.Integer, nullable=False)    # e.g. 9  
    # e.g. "offered", "accepted", "declined"
    # Up to you how you handle states.

    # Optionally record timestamps, etc.
    def __repr__(self):
        return f"<DriverOffer {self.id} driver={self.driver_id} request={self.ride_request_id} status={self.status}>"

class CalendarEntry(db.Model):
    __tablename__ = 'calendar_entry'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    year = db.Column(db.Integer, nullable=False)         # ex: 2025
    week_number = db.Column(db.Integer, nullable=False)  # ISO week 1..53
    day_of_week = db.Column(db.Integer, nullable=False)  # ISO day 1..7 (1 = lundi)

    start_hour = db.Column(db.Integer, nullable=True)
    end_hour = db.Column(db.Integer, nullable=True)

    depart_aller = db.Column(db.String(200), nullable=True)
    destination_aller = db.Column(db.String(200), nullable=True)
    depart_retour = db.Column(db.String(200), nullable=True)
    destination_retour = db.Column(db.String(200), nullable=True)

    role_aller = db.Column(db.String(50), nullable=True)
    role_retour = db.Column(db.String(50), nullable=True)

    validated_aller = db.Column(db.Boolean, default=False)
    validated_retour = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return (f"<CalendarEntry {self.id} user={self.user_id} "
                f"year={self.year} week={self.week_number} day={self.day_of_week}>")




def to_real_date(year, week_number, day_of_week):
    return datetime.date.fromisocalendar(year, week_number, day_of_week)




def convert_iso_string_to_calendar_slots(date_str):
    """
    Convertit un string 'YYYY-MM-DDTHH:MM:SSZ' (approx) en (year, week_num, day_of_week).
    """
    dt = parse(date_str)  # ex: 2025-03-30T22:00:00.000Z
    iso_year, iso_week, iso_day = dt.isocalendar()  # ex: (2025, 13, 7) par exemple
    return iso_year, iso_week, iso_day



###########################################################################################################################################DATABASE############################################################################################################