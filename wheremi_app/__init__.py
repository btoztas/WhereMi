from flask import Flask
from flask_pymongo import PyMongo
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager
from flask_migrate import Migrate, MigrateCommand
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config')

# MongoDB
mongo = PyMongo(app)

# SQLAlchemy
sql = SQLAlchemy(app)

# Import User Model and manage it
from wheremi_app.models.user import User
from wheremi_app.models.beacon import Beacon
from wheremi_app.models.device import Device
from wheremi_app.models.floor import Floor

sql_adapter = SQLAlchemyAdapter(sql, User)
user_manager = UserManager(sql_adapter, app)

# To do DB migrations
migrate = Migrate(app, sql)

# Manager
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from wheremi_app.views import home, floors, devices, beacons

# Admin
admin = Admin(app, name='whereami')
admin.add_view(ModelView(User, sql.session))
admin.add_view(ModelView(Beacon, sql.session))
admin.add_view(ModelView(Device, sql.session))
admin.add_view(ModelView(Floor, sql.session))