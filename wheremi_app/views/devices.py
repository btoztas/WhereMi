import json
from bson.json_util import dumps
from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Device, Floor, Beacon
from wheremi_app import sql
from wheremi_app.helpers.location import get_location_based_on_last_scans, decode_location_timestamp, \
    decode_accelerometer_event_timestamp, get_last_location, save_message


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
            location = get_last_location(device)
            movements= device.retrieve_all_accelerometer_events()
            status = device.retrieve_last_status()
            return render_template('device.html',
                                   device=device, username=username, location=location, movements=movements, status=status)

    abort(401)


@app.route("/api/devices/<device_id>", methods = ['POST', 'GET'])
def device_data(device_id):

    if request.method == 'POST':
        device = Device.query.filter_by(id=device_id).first()
        data = request.get_json()
        save_message(device, data)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    if request.method == 'GET':
        device = Device.query.filter_by(id=device_id).first()
        data = device.retrieve_all_messages()
        return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/locations")
def device_location_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_locations()
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/status")
def device_status_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_status()
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/accelerometer_events")
def device_accelerometer_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_accelerometer_events()
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/messages", methods = ['POST', 'GET'])
def device_save_message():
    if request.method == 'POST':
        data = request.get_json()
        device = Device.query.filter_by(name=data['device']).first()
        if device == None:
            abort(404)
        save_message(device, data)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    if request.method == 'GET':
        devices = Device.query.all()
        response = dict()
        for device in devices:
            response[device.name] = device.retrieve_all_messages()
        return dumps(response), 200, {'ContentType': 'application/json'}