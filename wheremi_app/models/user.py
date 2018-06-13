from flask_login import UserMixin
from wheremi_app import sql as db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __str__(self):
        return "" + str(self.id) + " - " + self.username
