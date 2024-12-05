document.addEventListener("DOMContentLoaded", function () {
    const createDispatchForm = document.getElementById("create-dispatch-form");
    const updateDispatchForm = document.getElementById("update-dispatch-form");
    const dispatchTable = document.getElementById("dispatch-table").querySelector("tbody");

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

    // Add Row to Dispatch Table
    function addDispatchToTable(id, status, reportId) {
        const row = dispatchTable.insertRow();
        row.innerHTML = `<td>${id}</td><td>${status}</td><td>${reportId}</td>`;
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
});
