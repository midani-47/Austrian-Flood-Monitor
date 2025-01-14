// Initialize the Leaflet map
const map = L.map('map', {
    zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria (default zoom)

// Add MapTiler Basic Map tiles
L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=worked\n', {
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

// Global variable for the popup
let reportPopup;

// Handle right-click on the map to show the popup
map.on('contextmenu', (e) => {
    console.log("Right-click detected:", e.latlng);

    // Remove existing popup
    if (reportPopup) {
        map.removeLayer(reportPopup);
    }

    // Create a new popup with a form
    reportPopup = L.popup()
        .setLatLng(e.latlng)
        .setContent(`
            <div style="font-size: 14px; padding: 10px;">
                <p><strong>Report Flooding</strong></p>
                <form id="floodReportForm">
                    <label>Email (required):</label><br>
                    <input type="email" id="email" required style="width: 100%; margin-bottom: 8px;"><br>
                    
                    <label>Phone (optional):</label><br>
                    <input type="text" id="phone" style="width: 100%; margin-bottom: 8px;"><br>
                    
                    <label>Description (optional):</label><br>
                    <textarea id="description" style="width: 100%; margin-bottom: 8px;"></textarea><br>
                    
                    <label>Severity:</label><br>
                    <select id="severity" required style="width: 100%; margin-bottom: 8px;">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="catastrophical">Catastrophical</option>
                    </select><br>
                    
                    <button type="button" id="submitReport" style="
                        background-color: #007bff; 
                        color: white; 
                        border: none; 
                        padding: 5px 10px; 
                        border-radius: 5px; 
                        cursor: pointer;">
                        Submit Report
                    </button>
                </form>
            </div>
        `)
        .openOn(map);

    // Add an event listener to the submit button
    setTimeout(() => {
        const submitButton = document.getElementById('submitReport');
        if (submitButton) {
            submitButton.addEventListener('click', () => {
                const email = document.getElementById('email').value.trim();
                const phone = document.getElementById('phone').value.trim();
                const description = document.getElementById('description').value.trim();
                const severity = document.getElementById('severity').value;
                createFloodReport(e.latlng.lat, e.latlng.lng, email, phone, description, severity);
                map.closePopup(reportPopup); // Close the popup after submitting
            });
        }
    }, 100); // Slight delay to ensure popup content is rendered
});

// Function to send a flood report to the backend
async function createFloodReport(lat, lng, email, phone, description, severity) {
    try {
        console.log("Sending flood report data:", {
            lat, lng, email, phone, description, severity
        });

        const response = await fetch('/api/reports', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: "true",
                lat: lat,
                long: lng,
                email: email,
                phone_number: phone || null, // Send null if phone is empty
                description: description || null, // Send null if description is empty
                severity: severity,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Backend error:", errorData.error);
            throw new Error('Failed to create flood report');
        }

        const result = await response.json();
        console.log('Flood report created:', result);
        alert('Flood report successfully created!');

        // Refresh the page to show the new report
        location.reload(); // Automatically refresh the page
    } catch (error) {
        console.error('Error creating flood report:', error);
        alert('Failed to create flood report');
    }
}



// Fetch and display reports on the map
async function fetchAndDisplayReports() {
    try {
        const response = await fetch('/api/reports');
        if (!response.ok) {
            throw new Error('Failed to fetch reports');
        }

        const reports = await response.json();

        reports.forEach(report => {
            if (report.verified === 2) return; // Skip rejected reports

            const markerColor = report.verified === 1 ? 'red' : 'gray'; // Set marker color

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${markerColor}; width: 12px; height: 12px; border-radius: 50%;"></div>`,
                iconSize: [10, 10],
            });

            const [latitude, longitude] = report.location.split(',').map(Number);
            if (isNaN(latitude) || isNaN(longitude)) return;

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
