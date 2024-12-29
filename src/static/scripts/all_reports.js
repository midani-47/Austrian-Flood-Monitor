async function fetchAndDisplayAllReports() {
    const tableBody = document.getElementById('reports-table-body');
    tableBody.innerHTML = '';

    try {
        const response = await fetch('/api/reports');
        if (!response.ok) throw new Error('Failed to fetch reports');

        const reports = await response.json();
        reports.forEach(report => {
            const row = document.createElement('tr');

            // Determine the verified status label
            const verifiedLabel = report.verified === 0 ? 'Unverified' :
                                  report.verified === 1 ? 'Verified' :
                                  report.verified === 2 ? 'Rejected' : 'Unknown';

            // Determine the row color based on verified status
            const rowColor = report.verified === 0 ? '' : 
                             report.verified === 1 ? 'background-color: #d4edda;' :
                             report.verified === 2 ? 'background-color: #f8d7da;' : '';

            row.style = rowColor;

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
                <td>${verifiedLabel}</td>
            `;

            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching and displaying reports:', error);
    }
}


fetchAndDisplayAllReports();