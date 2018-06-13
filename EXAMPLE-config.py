DEBUG = True
PRODUCTION = False

# DB Configurations
if PRODUCTION:
#    MONGO_DBNAME = 'stacker'
#    MONGO_URI = 'mongodb://stacker:kP9K8SvB@127.0.0.1/stacker'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://wheremi:kP9K8SvB@127.0.0.1/wheremi'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
else:
    MONGO_DBNAME = 'wheremi'
    MONGO_URI = 'mongodb://wheremi:wheremi123@ds155730.mlab.com:55730/wheremi'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/brunofgo/projects/wheremi/storage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-User Configurations
USER_ENABLE_EMAIL = False
USER_LOGIN_URL = '/login'
USER_LOGOUT_URL = '/logout'
USER_REGISTER_URL = '/register'

# CSRF
SECRET_KEY = '1d94e52c-1c89-4515-b87a-f48cf3cb7f0b'
CSRF_ENABLED = True

# File upload rules
UPLOAD_FOLDER = 'wheremi_app/static/files'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']



