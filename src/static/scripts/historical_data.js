// Initialize the Leaflet map
const map = L.map('map', {
    zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria (default zoom)

// Add MapTiler Basic Map tiles
L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=\n', {
  attribution: '&copy; <a href="https://www.maptiler.com/">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  maxZoom: 19,
}).addTo(map);

// Add custom zoom controls below the navbar
L.control.zoom({
    position: 'bottomright', // Move to bottom right
}).addTo(map);

// Restrict the map to Austria's approximate bounds
const bounds = [
    [45.5, 8.5],   // Southwest corner
    [49.5, 17.5],  // Northeast corner
];
map.setMaxBounds(bounds);
map.setMinZoom(8); // Prevent zooming out too far
map.setMaxZoom(16); // Prevent excessive zooming in

// Fetch GeoJSON data for Austria boundaries
fetch('/static/scripts/geoBoundaries-AUT-ADM0_simplified.geojson')
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(geojsonData => {
    console.log('GeoJSON data loaded:', geojsonData);

    // Extract Austria's geometry (MultiPolygon)
    const austriaPolygon = geojsonData.features[0].geometry;
    console.log('Austria Polygon:', austriaPolygon);

    // Ensure Austria Polygon is a valid MultiPolygon
    if (austriaPolygon.type !== 'MultiPolygon' || !Array.isArray(austriaPolygon.coordinates) || austriaPolygon.coordinates.length < 1) {
      console.error('Invalid Austria MultiPolygon coordinates');
      return;
    }

    // Create a layer for Austria with a black border and no fill
    const austriaLayer = L.geoJSON(austriaPolygon, {
      style: {
        color: 'black', // Black border for Austria
        weight: 2,
        fillOpacity: 0,  // Make the fill fully transparent (no fill color)
      }
    });

    // Add the Austria layer to the map
    austriaLayer.addTo(map);
  })
  .catch(error => console.error('Error loading GeoJSON:', error));

// WFS parameters
var wfsUrl = 'https://gis.lfrz.gv.at/wmsgw/';
var params = {
    key: 'a64a0c9c9a692ed7041482cb6f03a40a',
    service: 'WFS',
    version: '2.0.0',
    request: 'GetFeature',
    TYPENAME: 'inspire:pegelaktuell', // <FeatureType> from https://gis.lfrz.gv.at/wmsgw/?key=a64a0c9c9a692ed7041482cb6f03a40a&VERSION=2.0.0&REQUEST=GetCapabilities&SERVICE=WFS
    srsname: 'EPSG:4326',
    outputFormat: 'application/json'
};

// Construct the full WFS request URL
var queryString = Object.keys(params).map(key => key + '=' + encodeURIComponent(params[key])).join('&');
var fullUrl = wfsUrl + '?' + queryString;

// Fetch WFS data and add to map
fetch(fullUrl)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Add GeoJSON layer to the map
        L.geoJSON(data, {
            style: function (feature) {
                return { color: 'blue' };
            },
            onEachFeature: function (feature, layer) {
                if (feature.properties) {
                    layer.bindPopup(Object.keys(feature.properties).map(function (k) {
                        return k + ": " + feature.properties[k];
                    }).join("<br />"), {
                        maxHeight: 200
                    });
                }
            }
        }).addTo(map);
    })
    .catch(error => {
        console.error('Error fetching WFS data:', error);
    });