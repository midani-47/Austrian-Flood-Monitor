// Initialize the Leaflet map
const map = L.map('map', {
  zoomControl: false, // Disable default zoom controls
}).setView([47.5162, 14.5501], 7); // Center of Austria

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
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
map.setMinZoom(7); // Prevent zooming out too far
map.setMaxZoom(11); // Prevent excessive zooming in

// Add a marker for the center of Austria
L.marker([47.5162, 14.5501]).addTo(map).bindPopup('Center of Austria').openPopup();
