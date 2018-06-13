import os
import errno
from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Floor
from wheremi_app import sql as db
from wheremi_app.helpers.files import allowed_file, get_file_extension


@app.route("/floors")
@login_required
def list_floors():
    username = current_user.username
    floors = Floor.query.filter_by(user=current_user).all()
    return render_template('floors.html', username=username, floors=floors)


@app.route("/floors/new", methods = ['POST', 'GET'])
@login_required
def new_floor():

    if request.method == 'GET':
        username = current_user.username
        return render_template('new_floor.html', username=username)

    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file = request.files['file']
        username = current_user.username

        if file and allowed_file(file.filename):
            plant_name = "plant." + get_file_extension(file.filename)
            new_floor = Floor(user_id=current_user.id, name=name, plant_name=plant_name, description=description)
            db.session.add(new_floor)
            db.session.commit()

            file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                     username + "/" + str(new_floor.id) + "/" + plant_name)

            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            file.save(file_path)
            return redirect(url_for('list_floors'))

        return redirect(url_for('new'))


@app.route("/floors/<floor_id>", methods = ['POST', 'GET'])
@login_required
def get_floor(floor_id):
    username = current_user.username
    floor = Floor.query.filter_by(user=current_user, id=floor_id).first()
    
    if floor != None:
        if current_user == floor.user:
            return render_template('floor.html', floor=floor, username=username)

    abort(401)
