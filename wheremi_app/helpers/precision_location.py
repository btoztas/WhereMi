import json
import math
import numpy as np
from scipy.optimize import minimize


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x= %d; y=%d" % (self.x, self.y)

    def __repr__(self):
        return "x= %d; y=%d" % (self.x, self.y)

    def distance_to(self, other):
        return math.sqrt(pow(self.x - other.x, 2.0) + pow(self.y - other.y, 2.0))


class Circle(object):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __str__(self):
        return str(self.center) + "|" + str(self.radius)

    def __repr__(self):
        return str(self.center) + "|" + str(self.radius)


def location_error(pos, *args):
    p = Point(pos[0], pos[1])
    zone = args[0]
    N = len(zone)

    #print("TRYING POS:" + str(pos))

    error = 0
    for circle in zone:
        #print("CIRCLE:" + str(circle))
        error += pow(circle.radius - p.distance_to(circle.center), 2.0)
        #print(error)

    mse = error / N

    print("MSE:" + str(mse))
    return mse


def circle_constraint(pos, *args):
    circle = args[0]
    return - (pow((pos[0] - circle.center.x), 2) + pow((pos[1] - circle.center.y), 2) - pow(circle.radius, 2))


def get_location(zone):

    #initial_pos = np.array([ zone[0].center.x, zone[0].center.y ])
    initial_pos = np.array([ 0, 0 ])
    print(initial_pos)

    cons = []
    for entry in zone:
        cons.append( {'type': 'ineq', 'fun': circle_constraint, 'args': [entry]})
    # bnds = (
    #     (0, self.w),
    #     (0, self.h)
    # )

    result = minimize(
        location_error,  # The error function
        initial_pos,  # The initial guess
        args=(zone),  # Additional parameters for mse
        #bounds=bnds,
        method='SLSQP',  # The optimisation algorithm
        constraints=cons
    )

    location = result.x
    print(location)
    return (location[0], location[1])

def distance_to_beacon(rssi, beacon):
    distance = 100 * math.pow(10, (beacon.rssi_ref - rssi) / (10 * beacon.decay))
    return distance

# measurement is list with where each entry has the beacon and its rssi
def get_precision_location(measurement):

    zone = []
    for entry in measurement:
        beacon = entry['beacon']
        rssi = entry['rssi']
        radius = distance_to_beacon(rssi, beacon)

        circle_beacon = Circle(center=Point(beacon.x, beacon.y), radius=radius)
        zone.append(circle_beacon)
    print("zone:")
    print(zone)
    location = get_location(zone)
    area = []
    for circle in zone:
        area.append({
                'x': circle.center.x,
                'y': circle.center.y,
                'radius': circle.radius
            } )
    return {
        'x': location[0],
        'y': location[1],
        'zone': area
    }