from flask import render_template
from flask_login import current_user
from flask_user import login_required

from wheremi_app import app

@app.route("/")
@login_required
def home():
    username = current_user.username
    return render_template('home.html',username=username)