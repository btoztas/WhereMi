$(document).ready(function () {

    Highcharts.setOptions({
        time: {
            timezoneOffset: -60
        }
    });

    var path = window.location.pathname.split('/');
    var device_id = path[2];

    // TEMPERATURE
    $.ajax({
        url: '/api/devices/' + device_id + '/high_charts/temperature',
        dataType: "json",
        success: function (data) {

            console.log(data);

            Highcharts.chart('temperatureChart', {
                chart: {
                    type: 'spline'
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
                    type: 'spline'
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
                    zoomType: 'xy'
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
                switch(key) {
                    case '0':
                        state = 'Resting';
                        color = 'black';
                        break;
                    case '1':
                        state = 'Moving';
                        color = 'red';
                        break;
                    default:
                        state = 'Unknown';
                        color = 'grey';
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
                    type: 'scatter'
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
                    type: 'datetime',
                    dateTimeLabelFormats: { //force all formats to be hour:minute
                        second: '%H:%M',
                        minute: '%H:%M',
                        hour: '%H:%M',
                        day: '%H:%M',
                        week: '%H:%M',
                        month: '%H:%M',
                        year: '%H:%M'
                    }
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