import json
from bson.json_util import dumps
from flask import render_template, request, redirect, url_for, abort
from flask_user import login_required
from flask_login import current_user
from wheremi_app import app, Device, Floor
from wheremi_app import sql
from wheremi_app.helpers.location import save_message, get_n_location
import time


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
            location = get_n_location(device, 0)
            movements = device.retrieve_all_accelerometer_events()
            status = device.retrieve_last_status()
            temperature = device.retrieve_last_temperature()
            battery = device.retrieve_last_battery()
            return render_template(
                'device.html',
                device=device,
                username=username,
                location=location,
                movements=movements,
                status=status,
                temperature=temperature,
                battery=battery
            )

    abort(401)


@app.route("/api/devices/<device_id>")
@login_required
def device_info(device_id):
    device = Device.query.filter_by(id=device_id).first()
    response = {
        'id': device.id,
        'name': device.name,
        'description': device.description
    }
    return dumps(response), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/messages", methods = ['POST', 'GET'])
def device_messages(device_id):

    if request.method == 'POST':
        device = Device.query.filter_by(id=device_id).first()
        data = request.get_json()
        save_message(device, data)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    if request.method == 'GET':
        device = Device.query.filter_by(id=device_id).first()
        data = device.retrieve_all_messages()
        return dumps(data), 200, {'ContentType': 'application/json'}

@app.route("/api/devices/<device_id>/messages/many", methods = ['POST', 'GET'])
def device_many_messages(device_id):

    if request.method == 'POST':
        device = Device.query.filter_by(id=device_id).first()
        messages = request.get_json()
        for data in messages:
            save_message(device, data)

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route("/api/devices/<device_id>/locations")
@login_required
def device_location_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_locations()
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/status")
@login_required
def device_status_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_status()
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/movements")
@login_required
def device_movement_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_accelerometer_events()
    return dumps(data), 200, {'ContentType': 'application/json'}

@app.route("/api/devices/<device_id>/temperature")
@login_required
def device_temperature_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_temperature()
    return dumps(data), 200, {'ContentType': 'application/json'}

@app.route("/api/devices/<device_id>/battery")
@login_required
def device_battery_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    data = device.retrieve_all_battery()
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


# Highcharts

@app.route("/api/devices/<device_id>/high_charts/temperature")
@login_required
def device_highcharts_temperature_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    raw_data = device.retrieve_all_temperature()
    data = list()
    for entry in raw_data:
        data.append( [ entry['timestamp'] * 1000, entry['temperature'] ] )

    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/high_charts/battery")
@login_required
def device_highcharts_battery_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    raw_data = device.retrieve_all_battery()
    data = list()
    for entry in raw_data:
        data.append( [ entry['timestamp'] * 1000, entry['battery'] ] )

    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/high_charts/movements")
@login_required
def device_highcharts_movement_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    raw_data = device.retrieve_all_accelerometer_events()
    data = list()
    for entry in raw_data:
        data.append([ entry['timestamp'] * 1000, 1 ])
    return dumps(data), 200, {'ContentType': 'application/json'}


@app.route("/api/devices/<device_id>/high_charts/status")
@login_required
def device_highcharts_status_data(device_id):
    device = Device.query.filter_by(id=device_id).first()
    raw_data = device.retrieve_all_status()
    data = dict()

    for i, entry in enumerate(raw_data):
        if entry['status'] == 1 or entry['status'] == 2:
            status = 2

        elif entry['status'] == 3:
            status = 1
        else:
            status = 0
        timestamp = entry['timestamp']

        if status not in data:
            data[status] = list()

        if i == 0:
            data[status].append([ timestamp*1000 , int(time.time()*1000) ])
        else:
            data[status].append([ timestamp*1000 , previous*1000 ])

        previous = timestamp


    return dumps(data), 200, {'ContentType': 'application/json'}



@app.route("/api/devices/<device_id>/location")
@login_required
def device_location_api(device_id):
    device = Device.query.filter_by(user=current_user, id=device_id).first()
    if device != None:
        if current_user == device.user:
            location = get_n_location(device, 0)
            if 'beacon' in location: del location['beacon']
            floor = Floor.query.filter_by(id=location['floor_id']).first()
            return dumps(
                {
                    'location': location,
                    'floor': floor.serialize()
                }
            ), 200, {'ContentType': 'application/json'}

    abort(401)


@app.route("/api/devices/<device_id>/location/<int:n>")
@login_required
def device_location_n_api(device_id, n):
    device = Device.query.filter_by(user=current_user, id=device_id).first()
    if device != None:
        if current_user == device.user:
            location = get_n_location(device, n)
            if 'beacon' in location: del location['beacon']
            floor = device.home_floor
            return dumps(
                {
                    'location': location,
                    'floor': floor.serialize()
                }
            ), 200, {'ContentType': 'application/json'}

    abort(401)

