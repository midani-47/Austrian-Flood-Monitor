// profile.js

document.addEventListener('DOMContentLoaded', function () {
    const userEmail = document.getElementById('user-data').getAttribute('data-user-email');
 
    // Fetch flood reports for the logged-in user
    fetch(`/api/get_flood_reports?email=${userEmail}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            const reportList = document.getElementById('flood-reports-list');
            data.forEach((report) => {
                const listItem = document.createElement('li');
                listItem.textContent = `Severity: ${report.Severity}, Verified: ${report.Verified ? (report.Verified === 1 ? 'Yes' : 'Rejected') : 'No'}`;
                reportList.appendChild(listItem);
            });
        })
        .catch((error) => {
            console.error('Error fetching flood reports:', error);
        });
});
