from wheremi_app import sql as db, mongo
from datetime import datetime
import time


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(150), nullable=False)
    home_floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'))

    location_mode = db.Column(db.String(50), nullable=False)

    message_collection_name = db.Column(db.String(50), nullable=False)
    location_collection_name = db.Column(db.String(50), nullable=False)
    accelerometer_event_collection_name = db.Column(db.String(50), nullable=False)
    info_collection_name = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', foreign_keys=user_id)
    home_floor = db.relationship('Floor', foreign_keys=home_floor_id)

    def __init__(self, user_id, name, description, home_floor_id):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.home_floor_id = home_floor_id
        self.location_mode = "proximity"
        self.info_collection_name = self.create_device_info_collection_name(user_id, name)
        self.message_collection_name = self.create_message_collection_name(user_id, name)
        self.location_collection_name = self.create_location_collection_name(user_id, name)
        self.accelerometer_event_collection_name = self.create_accelerometer_event_collection_name(user_id, name)

    def __str__(self):
        return "" + str(self.id) + " - " + str(self.user_id) + " - " + self.name

    # defining here how the data collections will be named
    def create_message_collection_name(self, user_id, name):
        return "messages_" + str(user_id) + "_" + name

    def create_location_collection_name(self, user_id, name):
        return "locations_" + str(user_id) + "_" + name

    def create_accelerometer_event_collection_name(self, user_id, name):
        return "accelerometers_" + str(user_id) + "_" + name

    def create_device_info_collection_name(self, user_id, name):
        return "device_info_" + str(user_id) + "_" + name

    # data must be a dict
    def save_message(self, data):
        document = dict()
        document['data'] = data
        document['created_at'] = time.time()
        collection = mongo.db[self.message_collection_name]
        collection.insert(document)

    def save_proximity_location(self, id, timestamp):
        document = dict()
        document['location_type'] = 'proximity'
        document['location'] = {'id': id, 'timestamp':timestamp}
        collection = mongo.db[self.location_collection_name]
        collection.insert(document)

    def save_accelerometer_event_location(self, timestamp):
        document = dict()
        document['timestamp'] = timestamp
        collection = mongo.db[self.accelerometer_event_collection_name]
        collection.insert(document)

    def save_device_info(self, timestamp, battery, temperature):
        document = dict()
        document['timestamp'] = timestamp
        document['info'] = {'battery': battery, 'temperature': temperature}
        collection = mongo.db[self.info_collection_name]
        collection.insert(document)

    # returns a dict with the corresponding data
    def retrieve_all_messages(self):
        collection = mongo.db[self.message_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('created_at', -1)])
        return documents

    def retrieve_all_locations(self):
        collection = mongo.db[self.location_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('location.timestamp', -1)])
        return documents

    def retrieve_last_beacon_location(self):
        collection = mongo.db[self.location_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('location.timestamp', -1)]).limit(1)[0]
        except:
            return None
        return documents

    def retrieve_all_accelerometer_events(self):
        collection = mongo.db[self.accelerometer_event_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('timestamp', -1)])
        return documents

    def retrieve_all_status(self):
        collection = mongo.db[self.info_collection_name]
        documents = collection.find({}, {'_id': False}).sort([('location.timestamp', -1)])
        return documents

    def retrieve_last_status(self):
        collection = mongo.db[self.info_collection_name]
        try:
            documents = collection.find({}, {'_id': False}).sort([('location.timestamp', -1)]).limit(1)[0]
        except:
            return None
        return documents
