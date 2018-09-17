from wheremi_app import sql as db
from datetime import datetime

class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # this should be as follow: floor -> building -> campus -> organization -> has users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(50), nullable=False, unique=True)
    plant_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    x_ratio = db.Column(db.Float, nullable=False, default=0)
    x_offset = db.Column(db.Float, nullable=False, default=0)
    y_ratio = db.Column(db.Float, nullable=False, default=0)
    y_offset = db.Column(db.Float, nullable=False, default=0)
    y_size = db.Column(db.Float, nullable=False, default=0)
    x_size = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, name, plant_name, description, x_ratio, x_offset, y_ratio, y_offset, x_size, y_size):
        self.user_id = user_id
        self.name = name
        self.plant_name = plant_name
        self.description = description
        self.x_ratio = x_ratio
        self.x_offset = x_offset
        self.y_ratio = y_ratio
        self.y_offset = y_offset
        self.y_size = y_size
        self.x_size = x_size

    def __str__(self):
        return "" + str(self.id) + " - " + str(self.user_id) + " - " + self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'y_size': self.y_size,
            'x_size': self.x_size
        }

    def plan_file_path(self):
        return "files/%s/%d/%s" % (self.user.username, self.id, self.plant_name)


    def get_x_coordinate_on_map(self, x):
        x_map = x * self.x_ratio + self.x_offset

        return int(x_map)


    def get_y_coordinate_on_map(self, y):
        y_map = y * self.y_ratio + self.y_offset

        return int(y_map)