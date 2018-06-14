from wheremi_app import sql as db, mongo
from datetime import datetime
import time


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    home_floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', foreign_keys=user_id)
    home_floor = db.relationship('Floor', foreign_keys=home_floor_id)

    def __init__(self, user_id, name, description, home_floor_id):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.home_floor_id = home_floor_id

    def __str__(self):
        return "" + str(self.id) + " - " + str(self.user_id) + " - " + self.name

    # data must be a dict
    def save_data(self, data):
        document = dict()
        document['data'] = data
        document['created_at'] = time.time()
        collection = mongo.db[str(self.id)]
        collection.insert(document)

    # returns a dict with the corresponding data
    def retrieve_all_data(self):
        collection = mongo.db[str(self.id)]
        documents = collection.find({}, {'_id': False})
        return documents

    # returns a dict with the corresponding data
    def retrieve_last(self, size):
        collection = mongo.db[str(self.id)]
        documents = collection.find({}, {'_id': False}).skip(collection.count() - size)
        return documents

