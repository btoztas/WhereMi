DEBUG = True
PRODUCTION = False

# DB Configurations
if PRODUCTION:
#    MONGO_DBNAME = 'mydbname'
#    MONGO_URI = 'mongodb://myuser:mypass@127.0.0.1/stacker'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://myuser:mypass@127.0.0.1/wheremi'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
else:
    MONGO_DBNAME = 'mydbname'
    MONGO_URI = 'mongodb://myuser:mypass@127.0.0.1/stacker'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/brunofgo/projects/wheremi/storage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-User Configurations
USER_ENABLE_EMAIL = False
USER_LOGIN_URL = '/login'
USER_LOGOUT_URL = '/logout'
USER_REGISTER_URL = '/register'

# CSRF
SECRET_KEY = 'mysecretkey'
CSRF_ENABLED = True

# File upload rules
UPLOAD_FOLDER = 'wheremi_app/static/files'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']



