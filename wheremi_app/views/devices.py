import json
from bson.json_util import dumps
from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Device, Floor
from wheremi_app import sql

@app.route("/devices")
@login_required
def list_devices():
    username = current_user.username
    devices = Device.query.filter_by(user=current_user).all()
    return render_template('devices.html', username=username, devices=devices)


@app.route("/devices/new", methods = ['POST', 'GET'])
@login_required
def new_device():

    if request.method == 'GET':
        username = current_user.username
        floors = Floor.query.filter_by(user=current_user).all()
        return render_template('new_device.html', username=username, floors=floors)

    elif request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        home_floor_id = request.form['home_floor_id']
        new_device = Device(user_id=current_user.id, name=name, description=description, home_floor_id=home_floor_id)
        sql.session.add(new_device)
        sql.session.commit()

        return redirect(url_for('list_devices'))


@app.route("/devices/<device_id>", methods = ['POST', 'GET'])
@login_required
def get_device(device_id):
    username = current_user.username

    device = Device.query.filter_by(user=current_user, id=device_id).first()
    if device != None:
        if current_user == device.user:
            return render_template('device.html', device=device, username=username)

    abort(401)


@app.route("/api/devices/<device_id>", methods = ['POST', 'GET'])
def device_data(device_id):

    if request.method == 'POST':
        device = Device.query.filter_by(id=device_id).first()
        data = request.get_json()

        device.save_data(data)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    if request.method == 'GET':
        device = Device.query.filter_by(id=device_id).first()
        data = device.retrieve_last(3)
        return dumps(data), 200, {'ContentType': 'application/json'}