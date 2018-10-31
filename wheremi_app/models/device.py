from wheremi_app import sql as db, mongo
from datetime import datetime
import time


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(150), nullable=False)
    home_floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'))

    message_collection_name = db.Column(db.String(50), nullable=False)
    location_collection_name = db.Column(db.String(50), nullable=False)
    accelerometer_event_collection_name = db.Column(db.String(50), nullable=False)
    status_collection_name = db.Column(db.String(50), nullable=False)
    battery_collection_name = db.Column(db.String(50), nullable=False)
    temperature_collection_name = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', foreign_keys=user_id)
    home_floor = db.relationship('Floor', foreign_keys=home_floor_id)

    def __init__(self, user_id, name, description, home_floor_id):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.home_floor_id = home_floor_id
        self.battery_collection_name = self.create_battery_collection_name(user_id, name)
        self.temperature_collection_name = self.create_temperature_collection_name(user_id, name)
        self.message_collection_name = self.create_message_collection_name(user_id, name)
        self.location_collection_name = self.create_location_collection_name(user_id, name)
        self.status_collection_name = self.create_status_collection_name(user_id, name)
        self.accelerometer_event_collection_name = self.create_accelerometer_event_collection_name(user_id, name)

    def __str__(self):
        return "" + str(self.id) + " - " + str(self.user_id) + " - " + self.name


    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'home_floor_id': self.home_floor_id,
            'name': self.name,
            'description': self.description
        }



    # defining here how the data collections will be named
    def create_message_collection_name(self, user_id, name):
        return "messages_" + str(user_id) + "_" + name

    def create_location_collection_name(self, user_id, name):
        return "locations_" + str(user_id) + "_" + name

    def create_accelerometer_event_collection_name(self, user_id, name):
        return "accelerometers_" + str(user_id) + "_" + name

    def create_temperature_collection_name(self, user_id, name):
        return "temperature" + str(user_id) + "_" + name

    def create_battery_collection_name(self, user_id, name):
        return "battery" + str(user_id) + "_" + name

    def create_status_collection_name(self, user_id, name):
        return "status" + str(user_id) + "_" + name

    # data must be a dict
    def save_message(self, data):
        document = dict()
        document['data'] = data
        document['created_at'] = time.time()
        collection = mongo.db[self.message_collection_name]
        collection.insert(document)

    def save_location(self, timestamp, location):
        document = dict()
        document['timestamp'] = timestamp
        document['location'] = location
        collection = mongo.db[self.location_collection_name]
        collection.insert(document)

    def save_accelerometer_event(self, timestamp):
        document = dict()
        document['timestamp'] = timestamp
        collection = mongo.db[self.accelerometer_event_collection_name]
        collection.insert(document)

    def save_battery(self, timestamp, battery):
        document = dict()
        document['timestamp'] = timestamp
        document['battery'] = battery
        collection = mongo.db[self.battery_collection_name]
        collection.insert(document)

    def save_temperature(self, timestamp, temperature):
        document = dict()
        document['timestamp'] = timestamp
        document['temperature'] = temperature
        collection = mongo.db[self.temperature_collection_name]
        collection.insert(document)

    def save_status(self, timestamp, status):
        document = dict()
        document['timestamp'] = timestamp
        document['status'] = status
        collection = mongo.db[self.status_collection_name]
        collection.insert(document)


    # returns a dict with the corresponding data
    def retrieve_all_messages(self):
        collection = mongo.db[self.message_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('created_at', -1)])
        return documents

    def retrieve_all_locations(self):
        collection = mongo.db[self.location_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_last_location(self, n):
        collection = mongo.db[self.location_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)]).skip(n).limit(1)[0]
        except:
            return None
        return documents

    def retrieve_all_accelerometer_events(self):
        collection = mongo.db[self.accelerometer_event_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_all_temperature(self):
        collection = mongo.db[self.temperature_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_last_temperature(self):
        collection = mongo.db[self.temperature_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)]).limit(1)[0]
        except:
            return None
        return documents

    def retrieve_all_battery(self):
        collection = mongo.db[self.battery_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_last_battery(self):
        collection = mongo.db[self.battery_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)]).limit(1)[0]
        except:
            return None
        return documents

    def retrieve_all_status(self):
        collection = mongo.db[self.status_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_last_status(self):
        collection = mongo.db[self.status_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)]).limit(1)[0]
        except:
            return None
        return documents


    def rename(self, new_name):

        self.name=new_name

        collection_status = mongo.db[self.status_collection_name]
        self.status_collection_name = self.create_status_collection_name(self.user_id, new_name)
        collection_status.rename(self.status_collection_name)

        collection_battery = mongo.db[self.battery_collection_name]
        self.battery_collection_name = self.create_battery_collection_name(self.user_id, new_name)
        collection_battery.rename(self.battery_collection_name)

        collection_temperature = mongo.db[self.temperature_collection_name]
        self.temperature_collection_name = self.create_temperature_collection_name(self.user_id, new_name)
        collection_temperature.rename(self.temperature_collection_name)

        collection_message = mongo.db[self.message_collection_name]
        self.message_collection_name = self.create_message_collection_name(self.user_id, new_name)
        collection_message.rename(self.message_collection_name)

        collection_accelerometer_event = mongo.db[self.accelerometer_event_collection_name]
        self.accelerometer_event_collection_name = self.create_accelerometer_event_collection_name(self.user_id, new_name)
        collection_accelerometer_event.rename(self.accelerometer_event_collection_name)

        collection_location = mongo.db[self.location_collection_name]
        self.location_collection_name = self.create_location_collection_name(self.user_id, new_name)
        collection_location.rename(self.location_collection_name)

        db.session.commit()
