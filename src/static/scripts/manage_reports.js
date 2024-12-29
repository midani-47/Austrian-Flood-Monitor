async function fetchAndDisplayUnverifiedReports() {
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
                    <button onclick="rejectReport(${report.id})">Reject</button>
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
        fetchAndDisplayUnverifiedReports(); // Refresh the table
    } catch (error) {
        console.error('Error verifying report:', error);
        alert('Failed to verify report.');
    }
}

async function rejectReport(reportId) {
    try {
        const response = await fetch(`/api/unverified_reports/${reportId}/reject`, { method: 'PUT' });
        if (!response.ok) throw new Error('Failed to reject report');

        alert('Report rejected successfully!');
        fetchAndDisplayUnverifiedReports(); // Refresh the table
    } catch (error) {
        console.error('Error rejecting report:', error);
        alert('Failed to reject report.');
    }
}


// Fetch and display reports on page load
fetchAndDisplayUnverifiedReports();


