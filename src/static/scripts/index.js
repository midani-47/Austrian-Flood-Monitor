// Initialize the Leaflet map
const map = L.map('map', {
  zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria (default zoom)

// Add MapTiler Basic Map tiles
L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=fuckthisShit', {
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


// Fetch reports from the backend and display them on the map
async function fetchAndDisplayReports() {
  try {
      const response = await fetch('/api/reports');
      if (!response.ok) {
          throw new Error('Failed to fetch reports');
      }

      const reports = await response.json();

      reports.forEach(report => {
          // Rejected reports don't get displayed
          if (report.verified === 2) return;

          // Set marker color based on verification status
          const markerColor = report.verified === 1 ? 'red' : 'gray';

          // Create the color of the marker
          const customIcon = L.divIcon({
              className: 'custom-marker',
              html: `<div style="background-color: ${markerColor}; width: 12px; height: 12px; border-radius: 50%;"></div>`,
              iconSize: [10, 10],
          });

          // Extract latitude and longitude
          const [latitude, longitude] = report.location.split(',').map(Number);
          if (isNaN(latitude) || isNaN(longitude)) return;

          // Create a marker
          L.marker([latitude, longitude], { icon: customIcon })
              .addTo(map)
              .bindPopup(`
                  <strong>Report ID:</strong> ${report.id}<br>
                  <strong>Severity:</strong> ${report.severity}<br>
                  <strong>Verified:</strong> ${markerColor === 'red' ? 'Verified' : 'Unverified'}<br>
                  <strong>Location:</strong> ${report.location}
              `);
      });
  } catch (error) {
      console.error('Error fetching and displaying reports:', error);
  }
}

// Call the function to fetch and display reports
fetchAndDisplayReports();


