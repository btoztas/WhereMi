from wheremi_app import sql as db
from datetime import datetime

class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # this should be as follow: floor -> building -> campus -> organization -> has users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False)
    plant_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, name, plant_name, description):
        self.user_id = user_id
        self.name = name
        self.plant_name = plant_name
        self.description = description

    def __str__(self):
        return "" + str(self.id) + " - " + str(self.user_id) + " - " + self.name