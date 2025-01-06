// Initialize the Leaflet map
const map = L.map('map', {
  zoomControl: false, // Disable default zoom controls
}).setView([47.7162, 14.5501], 7); // Center of Austria (default zoom)

// Add MapTiler Basic Map tiles
L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=OhHg54JGb8sOVzBhT5uo\n', {
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

// Global variable for the popup
let reportPopup;

// Handle right-click on the map to show a popup
map.on('contextmenu', (e) => {
    console.log("Right-click detected:", e.latlng);

    // Remove existing popup
    if (reportPopup) {
        map.removeLayer(reportPopup);
    }

    // Create a new popup
    reportPopup = L.popup()
        .setLatLng(e.latlng)
        .setContent(`
            <div style="font-size: 14px; padding: 10px;">
                <p><strong>Report Flooding</strong></p>
                <button id="reportFloodButton" style="
                    background-color: #007bff; 
                    color: white; 
                    border: none; 
                    padding: 5px 10px; 
                    border-radius: 5px; 
                    cursor: pointer;">
                    Report Here
                </button>
            </div>
        `)
        .openOn(map);

    // Add an event listener to the button inside the popup
    setTimeout(() => {
        const reportButton = document.getElementById('reportFloodButton');
        if (reportButton) {
            reportButton.addEventListener('click', () => {
                console.log("Report Flooding button clicked!");
                createFloodReport(e.latlng.lat, e.latlng.lng);
                map.closePopup(reportPopup); // Close the popup after reporting
            });
        }
    }, 100); // Slight delay to ensure popup content is rendered
});

// Function to send a flood report to the backend
async function createFloodReport(lat, lng) {
    try {
        const response = await fetch('/api/reports', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location: "true",
                lat: lat,
                long: lng,
                email: "example@example.com", // Replace with the actual user email
                severity: "low", // Default severity
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to create flood report');
        }

        const result = await response.json();
        console.log('Flood report created:', result);
        alert('Flood report successfully created!');
    } catch (error) {
        console.error('Error creating flood report:', error);
        alert('Failed to create flood report');
    }
}

// Fetch and display reports (existing functionality remains unchanged)
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
