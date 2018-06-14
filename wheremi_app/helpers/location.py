import operator
from wheremi_app import Beacon


def get_location(device):
    data = device.retrieve_last(5)
    result = dict()

    try:
        for entry in data:
            for beacon in entry['data']['reading']:
                if beacon['id'] in result:
                    result[beacon['id']].append(beacon['rssi'])
                else:
                    result[beacon['id']] = list()
                    result[beacon['id']].append(beacon['rssi'])
    except KeyError:
        return None

    mean = dict()
    for beacon_id, beacon_rssi in result.iteritems():
        mean[beacon_id] = sum(beacon_rssi)/5
        print("Beacon "+beacon_id+" = "+ str(beacon_rssi))

    beacon_id = max(mean.iteritems(), key=operator.itemgetter(1))[0]

    return Beacon.query.filter_by(id=beacon_id).first()


