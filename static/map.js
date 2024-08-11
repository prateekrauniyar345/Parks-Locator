
// initialize the map
var map = L.map('map', {
    center :[39.8283, -98.5795],
    zoom :3
    // drawControl : true
});

// set the tiles for view
var OpenStreetMap_Mapnik = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var Stadia_AlidadeSatellite = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	// attribution: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'jpg'
});

// making two baselayers for the map
var basLayers = {
    'OpenstreetMap' : OpenStreetMap_Mapnik, 
    'Stadia_AlidadeSatellite' : Stadia_AlidadeSatellite
}
// add the baselayers
L.control.layers(basLayers).addTo(map);
// add the scale for zoom in/out
L.control.scale().addTo(map);

// update the zoom level value when the map is zoomed in or out
var zoomLevel = document.getElementById('zoom-level');
// initial zoom level
var initialZoom = map.getZoom();
zoomLevel.innerHTML = 'Zoom Level: ' + initialZoom;

map.on('zoomend', function(){
    var zoomValue = map.getZoom();
    zoomLevel.innerHTML = 'Zoom Level: ' + zoomValue;
});

/// Fetch the GeoJSON file, parse it, and then add it to the map
fetch('static/data/usa_boundary.geojson')
.then(response => {
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json();
})
.then(data => {
    console.log('GeoJSON data loaded:', data);  // Debug: Check if data is loaded

    L.geoJSON(data, {
        style: function(feature) {
            console.log('Feature:', feature);  // Debug: Check each feature
            return {
                color: 'gray',      // Set the border color
                fillColor: 'red',  // Set the fill color
                fillOpacity: 0.19     // Set the fill opacity
            };
        }
    }).addTo(map);
    
})
.catch(error => {
    console.error('Error loading GeoJSON data:', error);
});

//addding the draw control
var drawItems = new L.featureGroup();
map.addLayer(drawItems);
var drawControl  = new L.Control.Draw({
    edit:{
        featureGroup : drawItems,    //link to th efeature group for editing\
        remove : true     //enable remove functionality (delete)
    }, 
    draw : {
        circle: false, // Disable circle tool
        marker: false,
        polygon: true,
        polyline: false,
        rectangle: true,
        circlemarker: false
    }
}).addTo(map);

// add the draw event handlers
map.on(L.Draw.Event.CREATED, function(event) {
    var type = event.layerType;
    var layer = event.layer;
    map.addLayer(layer);
    drawItems.addLayer(layer)

    // add the drawn items to the Geojson format and console log it
    var geojson = layer.toGeoJSON();
    // Display GeoJSON data in the console and on the page
    console.log('Drawn GeoJSON:', geojson);

});

// adding the delete event handler
map.on(L.Draw.Event.DELETED, function(event){
    var type = event.layerType;
    var layer = event.layer;
    if(layer){
        layer.eachLayer(function(layer){
            drawItems.remove(layer);
            console.log("Deleted layer is: ", layer);
        });
    }
    console.log("Deleted layer is: ", layer);
});


/// Send GeoJSON data to Flask when the button is clicked
document.addEventListener('DOMContentLoaded', function() {
const button = document.querySelector('#btn-send-result');
button.addEventListener('click', function() {
    // alert('button cliked.')
    var allGeojson = drawItems.toGeoJSON();
    console.log('All drawn GeoJSONs are: ', allGeojson);
    fetch('/api/data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(allGeojson)
    })
    .then(function(response) {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(function(data) {
        console.log('Response to Flask:', data);
    })
    .catch(function(error) {
        console.error('Error sending GeoJSON data:', error);
    });
});
});
