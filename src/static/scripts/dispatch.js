document.addEventListener("DOMContentLoaded", function () {
    const createDispatchForm = document.getElementById("create-dispatch-form");
    const updateDispatchForm = document.getElementById("update-dispatch-form");
    const removeDispatchForm = document.getElementById("remove-dispatch-form");
    const dispatchTable = document.getElementById("dispatch-table").querySelector("tbody");
    const reportsTable = document.getElementById("reports-table").querySelector("tbody");

    // Fetch existing dispatches and populate the table
    async function fetchDispatches() {
        try {
            const response = await fetch("/api/dispatches");
            if (!response.ok) throw new Error("Failed to fetch dispatches");

            const dispatches = await response.json();
            dispatchTable.innerHTML = ""; // Clear the table
            dispatches.forEach((dispatch) => {
                addDispatchToTable(dispatch.id, dispatch.status, dispatch.report_id);
            });
        } catch (error) {
            console.error("Error fetching dispatches:", error);
        }
    }

    async function fetchReports() {
        try {
            const response = await fetch("/api/reports");
            if (!response.ok) throw new Error("Failed to fetch reports");

            const reports = await response.json();
            reportsTable.innerHTML = ""; // Clear the table
            reports.forEach((report) => {
                addReportToTable(report.id, report.location, report.severity, report.email);
            });
        } catch (error) {
            console.error("Error fetching reports:", error);
        }
    }

    fetchDispatches(); // Call the function on page load
    fetchReports(); // Fetch reports on page load

    // Create Dispatch
    createDispatchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const reportId = document.getElementById("report-id").value;

        const response = await fetch("/api/dispatch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ report_id: reportId }),
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Dispatch created: ${result.dispatch_id}`);
            addDispatchToTable(result.dispatch_id, "Planning", reportId);
        } else {
            alert(`Error: ${result.error}`);
        }
    });

    // Update Dispatch
    updateDispatchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const dispatchId = document.getElementById("dispatch-id").value;
        const status = document.getElementById("status").value;

        const response = await fetch(`/api/dispatch/${dispatchId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status }),
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Dispatch updated to: ${result.new_status}`);
            updateDispatchInTable(dispatchId, result.new_status);
        } else {
            alert(`Error: ${result.error}`);
        }
    });

    // Remove Dispatch
    removeDispatchForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const dispatchId = document.getElementById("remove-dispatch-id").value;

        const response = await fetch(`/api/dispatch/${dispatchId}`, {
            method: "DELETE",
        });

        const result = await response.json();
        if (response.ok) {
            alert(`Dispatch removed: ${result.dispatch_id}`);
            removeDispatchFromTable(dispatchId);
        } else {
            alert(`Error: ${result.error}`);
        }
    });

    // Add Row to Dispatch Table
    function addDispatchToTable(id, status, reportId) {
        const row = dispatchTable.insertRow();
        row.innerHTML = `<td>${id}</td><td>${status}</td><td>${reportId}</td>`;
    }

     // Add Row to Reports Table
    function addReportToTable(id, location, severity, email) {
        const row = reportsTable.insertRow();
        row.innerHTML = `<td>${id}</td><td>${location}</td><td>${severity}</td><td>${email}</td>`;
    }

    // Update Dispatch in Table
    function updateDispatchInTable(id, status) {
        const rows = dispatchTable.rows;
        for (let row of rows) {
            if (row.cells[0].textContent == id) {
                row.cells[1].textContent = status;
                break;
            }
        }
    }

    // Remove Dispatch from Table
    function removeDispatchFromTable(id) {
        const rows = dispatchTable.rows;
        for (let i = 0; i < rows.length; i++) {
            if (rows[i].cells[0].textContent == id) {
                dispatchTable.deleteRow(i);
                break;
            }
        }
    }
});
