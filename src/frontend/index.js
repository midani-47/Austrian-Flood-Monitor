const map = L.map('map', {
  center: [47.5162, 14.5501],
  zoom: 7,
  minZoom: 7,
  maxZoom: 13, 
  maxBounds: [
    [46.25, 9.0], // Southwest boundary 
    [49.0, 17.0]   // Northeast corner 
  ],
  maxBoundsViscosity: 1.0
}); 


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);