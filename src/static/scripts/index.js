// Initialize the Leaflet map
const map = L.map('map', {
  zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria

// Add MapTiler Basic Map tiles
L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=THE_API_KEY', {
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
map.setMaxZoom(11); // Prevent excessive zooming in

// Load GeoJSON data and add as a layer
// This needs to be finished while Beutifiying the map


// Add a marker for the center of Austria
// This is just a demo marker
L.marker([47.5162, 14.5501]).addTo(map).bindPopup('Center of Austria').openPopup();

