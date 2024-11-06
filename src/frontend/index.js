// Initialize the map and set the view to the center of Austria
const map = L.map('map', {
  center: [47.5162, 14.5501], // Center of Austria
  zoom: 8, // Initial zoom level for Austria
  minZoom: 7, // Minimum zoom level to prevent zooming out too far
  maxZoom: 13, // Maximum zoom level for closer views
  maxBounds: [
    [46.25, 9.0], // Southwest boundary (approximate)
    [49.0, 17.0]   // Northeast corner (approximate)
  ],
  maxBoundsViscosity: 1.0 // Keeps the map within bounds
});

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);