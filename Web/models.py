from flask_sqlalchemy import SQLAlchemy
import uuid
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

###########################################################################################################################################DATABASE############################################################################################################