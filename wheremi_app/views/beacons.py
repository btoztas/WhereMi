import json

from bson.json_util import dumps
from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Device, Floor, Beacon
from wheremi_app import sql as db
from flask import jsonify

@app.route("/floors/<home_floor_id>/beacons")
@login_required
def list_beacons(home_floor_id):
    username = current_user.username
    home_floor = Floor.query.filter_by(user=current_user, id=home_floor_id).first()
    beacons = Beacon.query.filter_by(home_floor=home_floor).order_by(Beacon.identifier).all()
    return render_template('beacons.html', username=username, beacons=beacons, floor=home_floor)


@app.route("/floors/<home_floor_id>/beacons/new", methods = ['POST', 'GET'])
@login_required
def new_beacon(home_floor_id):

    if request.method == 'GET':
        username = current_user.username
        floor = Floor.query.filter_by(user=current_user, id=home_floor_id).first()
        return render_template('new_beacon.html', username=username, floor=floor)

    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        identifier = request.form['identifier']
        x = request.form['x']
        y = request.form['y']
        new_beacon = Beacon(identifier=identifier, name=name, description=description, home_floor_id=home_floor_id, x=x, y=y)
        db.session.add(new_beacon)
        db.session.commit()

        return redirect('/floors/' + str(home_floor_id) + '/beacons')




@app.route("/floors/<home_floor_id>/beacons/<beacon_id>")
@login_required
def beacon(home_floor_id, beacon_id):
    username = current_user.username

    beacon = Beacon.query.filter_by(id=beacon_id).first()
    if beacon != None:
        if current_user == beacon.home_floor.user:
            return render_template('beacon.html', username=username, device=beacon)

    abort(401)

@app.route("/api/floors/<home_floor_id>/beacons/<beacon_id>")
@login_required
def beacon_api(home_floor_id, beacon_id):
    username = current_user.username

    beacon = Beacon.query.filter_by(id=beacon_id).first()
    if beacon != None:
        if current_user == beacon.home_floor.user:
            return dumps(beacon.serialize_for_map()), 200, {'ContentType': 'application/json'}

    abort(401)


@app.route("/api/floors/<home_floor_id>/beacons", methods=['POST', 'GET'])
def new_beacon_api(home_floor_id):

    if request.method == 'POST':
        if Floor.query.filter_by(id=home_floor_id).first():
            data = request.get_json()
            for beacon in data:
                try:
                    name = beacon['name']
                    description = beacon['description']
                    identifier = beacon['identifier']
                    x = beacon['x']
                    y = beacon['y']
                    new_beacon = Beacon(identifier=identifier, name=name, description=description, home_floor_id=home_floor_id, x=x, y=y)
                    db.session.add(new_beacon)
                except:
                    return json.dumps(
                        {
                            'success': False,
                            'error': 'Exception adding beacons to database'
                        }), 400, {'ContentType': 'application/json'}

            db.session.commit()
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    return abort(404)

