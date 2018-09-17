import os
import errno
from flask import render_template, request, redirect, url_for, abort, send_file
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Floor, Beacon
from wheremi_app import sql as db
from wheremi_app.helpers.files import allowed_file, get_file_extension
from bson.json_util import dumps


@app.route("/floors")
@login_required
def list_floors():
    username = current_user.username
    floors = Floor.query.filter_by(user=current_user).all()
    return render_template('floors.html', username=username, floors=floors)


@app.route("/floors/new", methods=['POST', 'GET'])
@login_required
def new_floor():
    if request.method == 'GET':
        username = current_user.username
        return render_template('new_floor.html', username=username)

    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file = request.files['file']
        x_offset = request.form['x-offset']
        x_ratio = request.form['x-ratio']
        y_offset = request.form['y-offset']
        y_ratio = request.form['y-ratio']
        x_size = request.form['x-size']
        y_size = request.form['y-size']
        username = current_user.username

        if file and allowed_file(file.filename):
            plant_name = "plant." + get_file_extension(file.filename)
            new_floor = Floor(user_id=current_user.id, name=name, plant_name=plant_name, description=description,
                              x_ratio=x_ratio, x_offset=x_offset, y_offset=y_offset, y_ratio=y_ratio, y_size=y_size,
                              x_size=x_size)
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


@app.route("/floors/<floor_id>", methods=['POST', 'GET'])
@login_required
def get_floor(floor_id):
    username = current_user.username
    floor = Floor.query.filter_by(user=current_user, id=floor_id).first()

    if floor != None:
        if current_user == floor.user:
            return render_template('floor.html', floor=floor, username=username)

    abort(401)



@app.route("/floors/<floor_id>/plan")
@login_required
def get_floor_plan(floor_id):
    username = current_user.username
    floor = Floor.query.filter_by(user=current_user, id=floor_id).first()
    if floor != None:
        if current_user == floor.user:
            filename = 'static/files/' + username +'/' + floor_id + '/' + floor.plant_name

            return send_file(filename, mimetype='image/' + get_file_extension(floor.plant_name))

    abort(404)

@app.route("/api/floors/<home_floor_id>")
@login_required
def api_list_beacons(home_floor_id):
    home_floor = Floor.query.filter_by(id=home_floor_id).first()

    if home_floor:
        beacons_raw = Beacon.query.filter_by(home_floor=home_floor).order_by(Beacon.identifier).all()
        beacons = []
        if beacons_raw:
            beacons = [beacon.serialize_for_map() for beacon in beacons_raw]
        data = {
            'floor': home_floor.serialize(),
            'beacons': beacons
        }
        return dumps(data), 200, {'ContentType': 'application/json'}
    abort(404)
