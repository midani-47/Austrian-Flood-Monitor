// Initialize the Leaflet map
const map = L.map('map', {
  zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria

const apiKey = "The_api_key"

// Add Corto's tiles
L.tileLayer('https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=${apiKey}', {
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



// Add a marker for the center of Austria
L.marker([47.5162, 14.5501]).addTo(map).bindPopup('Center of Austria').openPopup();
