// Function to fetch and display reports
async function fetchAndDisplayReports() {
    const tableBody = document.getElementById('reports-table-body');
    tableBody.innerHTML = '';

    try {
        const response = await fetch('/api/unverified_reports');
        if (!response.ok) throw new Error('Failed to fetch reports');

        const reports = await response.json();
        reports.forEach(report => {
            const row = document.createElement('tr');

            row.innerHTML = `
                <td>${report.id}</td>
                <td>${report.location}</td>
                <td>${report.email}</td>
                <td>${report.phone || 'N/A'}</td>
                <td>${report.description || 'N/A'}</td>
                <td>${report.severity}</td>
                <td>
                    ${report.picture ? `<a href="${report.picture}" target="_blank">View</a>` : 'N/A'}
                </td>
                <td>
                    <button onclick="verifyReport(${report.id})">Verify</button>
                    <button onclick="deleteReport(${report.id})" class="delete-button">Delete</button>
                </td>
            `;

            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching and displaying reports:', error);
    }
}

// Function to verify a report
async function verifyReport(reportId) {
    try {
        const response = await fetch(`/api/unverified_reports/${reportId}/verify`, { method: 'PUT' });
        if (!response.ok) throw new Error('Failed to verify report');

        alert('Report verified successfully!');
        fetchAndDisplayReports(); // Refresh the table
    } catch (error) {
        console.error('Error verifying report:', error);
        alert('Failed to verify report.');
    }
}

// Function to delete a report
async function deleteReport(reportId) {
    try {
        const response = await fetch(`/api/unverified_reports/${reportId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete report');

        alert('Report deleted successfully!');
        fetchAndDisplayReports(); // Refresh the table
    } catch (error) {
        console.error('Error deleting report:', error);
        alert('Failed to delete report.');
    }
}

// Fetch and display reports on page load
fetchAndDisplayReports();