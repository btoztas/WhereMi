$(document).ready(function () {



    var path = window.location.pathname.split('/');
    var floor_id = path[2];
    var layers = [];

    $.ajax({
        url: '/api/floors/' + floor_id,
        dataType: "json",

        success: function (data) {


            var plan_size_x = data['floor']['x_size'];
            var plan_size_y = data['floor']['y_size'];

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


            Object.keys(data['beacons']).forEach(function (key) {

                var x = data['beacons'][key]['x'];
                var y = data['beacons'][key]['y'];
                var name = data['beacons'][key]['name'];
                var description = data['beacons'][key]['description'];
                var identifier = data['beacons'][key]['identifier'];


                // ICON----
                var iconFeature = new ol.Feature({
                    geometry: new ol.geom.Point([x, y]),
                    identifier: identifier,
                    description: description,
                    name: name
                });

                var iconStyle = new ol.style.Style({
                    image: new ol.style.Icon(/** @type {module:ol/style/Icon~Options} */ ({
                        src: 'https://cdn1.iconfinder.com/data/icons/map-and-navigation-9/64/58-512.png',
                        scale: 0.1
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
                console.log(layers);
            });


            var map = new ol.Map({
                layers: layers,
                target: 'map',
                view: new ol.View({
                    projection: projection,
                    center: [plan_size_x / 2, plan_size_y / 2, plan_size_x / 2, plan_size_y / 2],
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


        },
        error: function () {
            alert("Error loading beacons to map");
        }
    });


});