from datetime import datetime
from wheremi_app import app

@app.template_filter('format_unix_time')
def format_unix_time(s):
    return datetime.fromtimestamp(s).strftime('%d/%m/%Y %H:%M:%S')

@app.template_filter('format_time_from_time_object')
def format_time_from_time_object(s):
    return s.strftime('%d/%m/%Y %H:%M:%S')