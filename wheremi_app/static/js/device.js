function getMap(n, data) {

    document.getElementById('map').innerHTML = '';

    var layers = [];

    var plan_size_x = data['floor']['x_size'];
    var plan_size_y = data['floor']['y_size'];
    var floor_id = data['floor']['id'];
    var x = data['location']['x'];
    var y = data['location']['y'];

    // Map views always need a projection.  Here we just want to map image
    // coordinates directly to map coordinates, so we create a projection that uses
    // the image extent in pixels.
    var extent = [0, 0, plan_size_x, plan_size_y];
    var projection = new ol.proj.Projection({
        units: 'pixels',
        extent: extent
    });

    var map_layer = new ol.layer.Image({
        source: new ol.source.ImageStatic({
            url: '/floors/' + floor_id + '/plan',
            projection: projection,
            imageExtent: extent
        })
    });

    layers.push(map_layer);


    if (data['location']['type'] == 'Precision') {

        Object.keys(data['location']['zone']).forEach(function (key) {

            var x = data['location']['zone'][key]['x'];
            var y = data['location']['zone'][key]['y'];
            var radius = data['location']['zone'][key]['radius'];
            var circle = new ol.geom.Circle([x, y], radius);
            var circleFeature = new ol.Feature(circle);

            // Source and vector layer
            var vectorSource = new ol.source.Vector({
                features: [circleFeature]
            });

            var vectorLayer = new ol.layer.Vector({
                source: vectorSource
            });

            layers.push(vectorLayer);
            console.log(layers);
        });
    }

    // ICON----
    var iconFeature = new ol.Feature({
        geometry: new ol.geom.Point([x, y]),
        name: 'Device Location'
    });

    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon(/** @type {module:ol/style/Icon~Options} */ ({
            src: 'http://www.myiconfinder.com/uploads/iconsets/256-256-76f453c62108782f0cad9bfc2da1ae9d.png',
            scale: 0.2,
            offset: [0, 0]
        }))
    });

    iconFeature.setStyle(iconStyle);

    var vectorSource = new ol.source.Vector({
        features: [iconFeature]
    });

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });
    // ICON----

    layers.push(vectorLayer);

    var map = new ol.Map({
        layers: layers,
        target: 'map',
        view: new ol.View({
            projection: projection,
            center: [plan_size_x / 2, plan_size_y / 2],
            zoom: 1,
            maxZoom: 4
        })
    });

    var element = document.getElementById('popup');

    var popup = new ol.Overlay({
        element: element,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, 0]
    });
    map.addOverlay(popup);

    // display popup on click
    map.on('click', function (evt) {
        var feature = map.forEachFeatureAtPixel(evt.pixel,
            function (feature) {
                return feature;
            });
        if (feature) {
            var coordinates = feature.getGeometry().getCoordinates();
            popup.setPosition(coordinates);
            $(element).popover({
                placement: 'top',
                html: true,
                content: feature.get('name')
            });
            $(element).popover('show');
        } else {
            $(element).popover('destroy');
        }
    });

    // change mouse cursor when over marker
    map.on('pointermove', function (e) {
        if (e.dragging) {
            $(element).popover('destroy');
            return;
        }
        var pixel = map.getEventPixel(e.originalEvent);
        var hit = map.hasFeatureAtPixel(pixel);
        map.getTarget().style.cursor = hit ? 'pointer' : '';
    });


}

function updatePositionHTML(n, data) {

    document.getElementById("locationCount").innerHTML = n;

    document.getElementById("locationAlgorithm").innerHTML = data['location']['type'];

    if (data['location']['type'] == 'Proximity') {

        document.getElementById("locationPosition").innerHTML = "Strongest Beacon - " + data['location']['beacon_info']['identifier'] + " - " + data['location']['beacon_info']['name'] + " - " + data['location']['beacon_info']['description']

    } else if (data['location']['type'] == 'Precision') {

        document.getElementById("locationPosition").innerHTML = "" +
            "<b>X = </b> " + data['location']['x_real'] + " cm || " +
            "<b>Y = </b> " + data['location']['y_real'] + " cm || <br>" +
            "<b>Strongest Beacon</b>: " + data['location']['beacon_info']['identifier'] + " - " + data['location']['beacon_info']['name'] + " - " + data['location']['beacon_info']['description'];
    } else {
        document.getElementById("locationPosition").innerHTML = "Unknown";
    }

    timestamp = new Date(data['location']['timestamp'] * 1000);

    day = (timestamp.getDate() < 10) ? ('0' + timestamp.getDate()) : (timestamp.getDate());
    month = (timestamp.getMonth()+1 < 10) ? ('0' + (timestamp.getMonth() + 1)) : (timestamp.getMonth() + 1);
    year = timestamp.getFullYear();
    hours = (timestamp.getHours() < 10) ? ('0' + timestamp.getHours()) : (timestamp.getHours());
    minutes = (timestamp.getMinutes() < 10) ? ('0' + timestamp.getMinutes()) : (timestamp.getMinutes());
    seconds = (timestamp.getSeconds() < 10) ? ('0' + timestamp.getSeconds()) : (timestamp.getSeconds());

    document.getElementById("locationTimestamp").innerHTML = day + '/' + month + '/' + year + ' ' + hours + ':' + minutes + ':' + seconds;

}

function updatePosition(n) {
    var path = window.location.pathname.split('/');
    var device_id = path[2];


    $.ajax({
        url: '/api/devices/' + device_id + '/location/' + n,
        dataType: "json",

        success: function (data) {

            if (data['location']['exists'] == true) {

                getMap(n, data);
                updatePositionHTML(n, data);
            }
        },
        error: function () {
            alert("Error loading beacons to map");
        }
    });


}

function backHistory() {
    count = Number(document.getElementById('locationCount').innerText) - 1;
    if (count != -1) {
        updatePosition(count);
    }
}

function nextHistory() {
    count = Number(document.getElementById('locationCount').innerText) + 1;
    updatePosition(count);


}

$(document).ready(function () {


    var path = window.location.pathname.split('/');
    var device_id = path[2];


    $.ajax({
        url: '/api/devices/' + device_id + '/location',
        dataType: "json",

        success: function (data) {

            getMap(0, data);

        },
        error: function () {
            alert("Error loading beacons to map");
        }
    });


    Highcharts.setOptions({
        time: {
            timezoneOffset: -60
        }
    });


    // TEMPERATURE
    $.ajax({
        url: '/api/devices/' + device_id + '/high_charts/temperature',
        dataType: "json",
        success: function (data) {

            console.log(data);

            Highcharts.chart('temperatureChart', {
                chart: {
                    type: 'spline',
                    zoomType: 'xy'
                },
                title: {
                    text: 'Temperature'
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Temperature (ºC)'
                    },
                    min: 0
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x:%e. %b - %H:%M:%S}: {point.y} ºC'
                },

                plotOptions: {
                    spline: {
                        marker: {
                            enabled: true
                        }
                    }
                },

                colors: ['#000'],

                // Define the data points. All series have a dummy year
                // of 1970/71 in order to be compared on the same x axis. Note
                // that in JavaScript, months start at 0 for January, 1 for February etc.
                series: [{
                    name: "Temperature",
                    data: data
                }]
            });
        },
        error: function () {
            alert("Error loading temperature");
        }
    });

    // BATTERY
    $.ajax({
        url: '/api/devices/' + device_id + '/high_charts/battery',
        dataType: "json",
        success: function (data) {

            Highcharts.chart('batteryChart', {
                chart: {
                    type: 'spline',
                    zoomType: 'xy'
                },
                title: {
                    text: 'Battery'
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Battery (V)'
                    },
                    min: 0
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x:%e. %b - %H:%M:%S}: {point.y:.2f} V'
                },

                plotOptions: {
                    spline: {
                        marker: {
                            enabled: true
                        }
                    }
                },

                colors: ['#000'],

                // Define the data points. All series have a dummy year
                // of 1970/71 in order to be compared on the same x axis. Note
                // that in JavaScript, months start at 0 for January, 1 for February etc.
                series: [{
                    name: "Battery",
                    data: data
                }]
            });
        },
        error: function () {
            alert("Error loading battery");
        }
    });


    // MOVEMENTS
    $.ajax({
        url: '/api/devices/' + device_id + '/high_charts/movements',
        dataType: "json",
        success: function (data) {


            Highcharts.chart('movementChart', {
                chart: {
                    type: 'scatter',
                    zoomType: 'x'
                },
                title: {
                    text: 'Movement History'
                },
                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: { // don't display the dummy year
                        month: '%e. %b',
                        year: '%b'
                    },
                    title: {
                        text: 'Date'
                    }
                },
                yAxis: {
                    title: {
                        text: 'Movement Counts'
                    }
                },
                legend: {
                    layout: 'vertical',
                    align: 'left',
                    verticalAlign: 'top',
                    x: 100,
                    y: 70,
                    floating: true,
                    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
                    borderWidth: 1
                },
                plotOptions: {
                    scatter: {
                        marker: {
                            radius: 5,
                            states: {
                                hover: {
                                    enabled: true,
                                    lineColor: 'rgb(100,100,100)'
                                }
                            }
                        },
                        states: {
                            hover: {
                                marker: {
                                    enabled: false
                                }
                            }
                        },
                        tooltip: {
                            headerFormat: '<b>Movement</b><br>',
                            pointFormat: '{point.x:%e. %b - %H:%M:%S}'
                        }
                    }
                },
                series: [{
                    name: 'Movements',
                    color: 'rgba(0, 0, 0, .5)',
                    data: data
                }]
            });


        },
        error: function () {
            alert("Error loading movement history");
        }
    });

    // STATUS
    $.ajax({
        url: '/api/devices/' + device_id + '/high_charts/status',
        dataType: "json",

        success: function (data) {
            var series = [];

            Object.keys(data).forEach(function (key) {
                var state;
                var color;
                switch (key) {
                    case '0':
                        state = 'Stationary';
                        color = 'black';
                        break;
                    case '1':
                        state = 'Stopped';
                        color = 'grey';
                        break;
                    case '2':
                        state = 'Moving';
                        color = 'red';
                        break;
                    default:
                        state = 'Unknown';
                        color = 'blue';
                }
                var dataRaw = data[key];
                var serie = {
                    name: state,
                    color: color,
                    dataRaw: [{
                        y: 1,
                        xRanges: dataRaw
                    }]
                };
                series.push(serie);
            });
            console.log(series);
            series.map(function (series) {
                series.data = [];
                series.dataRaw.forEach(function (dataRaw) {
                    dataRaw.xRanges.forEach(function (xRange) {
                        series.data.push([xRange[0], dataRaw.y], [xRange[1], dataRaw.y], [xRange[1], null]); // null breakes the line
                    }); // forEach
                }); // forEach
                return series;
            });

            Highcharts.chart('statusChart', {
                chart: {
                    type: 'scatter',
                    zoomType: 'x'
                },
                title: {
                    text: 'Status History'
                },
                tooltip: {
                    formatter: function () {
                        return Highcharts.dateFormat('%H:%M', this.x);
                    }
                },
                plotOptions: {
                    series: {
                        lineWidth: 5,
                        marker: {
                            enabled: false,
                            symbol: 'circle'
                        }
                    }
                },
                xAxis: {
                    title: {
                        text: 'Time'
                    },
                    type: 'datetime'
                },

                yAxis: {
                    tickInterval: 1
                },
                series: series
            });
        },
        error: function () {
            alert("Error loading movement history");
        }
    });
});