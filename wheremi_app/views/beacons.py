from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Device, Floor, Beacon
from wheremi_app import sql as db

@app.route("/floors/<home_floor_id>/beacons")
@login_required
def list_beacons(home_floor_id):
    username = current_user.username
    home_floor = Floor.query.filter_by(user=current_user, id=home_floor_id).first()
    beacons = Beacon.query.filter_by(home_floor=home_floor).all()
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
        new_beacon = Beacon(identifier=identifier, name=name, description=description, home_floor_id=home_floor_id)
        db.session.add(new_beacon)
        db.session.commit()

        return redirect('/floors/' + str(home_floor_id) + '/beacons')


@app.route("/floors/<home_floor_id>/beacons/<beacon_id>", methods = ['POST', 'GET'])
@login_required
def get_beacon(home_floor_id, beacon_id):
    username = current_user.username

    beacon = Beacon.query.filter_by(id=beacon_id).first()
    if beacon != None:
        if current_user == beacon.user:
            return render_template('beacon.html', beacon=beacon, username=username)

    abort(401)
