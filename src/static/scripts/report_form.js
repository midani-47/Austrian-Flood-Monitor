// Log to verify the script is loaded successfully
console.log("JavaScript loaded successfully!");

document.addEventListener("DOMContentLoaded", async function () {
    const emailInput = document.getElementById("email");

    try {
        const response = await fetch('/api/user_email');
        if (!response.ok) throw new Error('Failed to fetch user email');

        const data = await response.json();
        const userEmail = data.email;

        if (userEmail) {
            emailInput.value = userEmail;
            emailInput.setAttribute("readonly", true); // Make the email field readonly
            console.log("Email field populated with logged-in user's email.");
        }
    } catch (error) {
        console.error('Error fetching user email:', error);
    }
});

    const removeFileIcon = document.getElementById("remove-file-icon");
    const fileInput = document.getElementById("picture"); // todo:important for future file handling

    removeFileIcon.addEventListener("click", function () {
        fileInput.value = ""; // Clear the file input value
        console.log("File selection cleared.");
    });

var lat;
var long;
var currloc = false;

function wait(ms){
    var start = new Date().getTime();
    var end = start;
    while(end < start + ms) {
      end = new Date().getTime();
   }
 }

function getLocation() {
    console.log("Location tracking button clicked!");
    currloc = true;

    const getLoc = async () => {
    var acc;
    var rep = 0;

    const latLabel = document.getElementById('lat');
    const longLabel = document.getElementById('long');

    do {
        if(currloc) {
            navigator.geolocation.getCurrentPosition(function(location) {
               lat = Number(location.coords.latitude.toFixed(6));
               long = Number(location.coords.longitude.toFixed(6));
               acc = location.coords.accuracy;

               latLabel.innerHTML = lat;
               longLabel.innerHTML = long;
            });
       }
       rep++;
       console.log("failed to get good accuracy, attempting again in 0.2 seconds, attempt nr " + rep);

       wait(200);
    }
    while(acc > 50 + ((rep - 1) * 50) && rep < 20);
    
    if(rep >= 20) {
        console.log("failed go get good accuracy in 20+ attempts, aborting");
        currloc = false;
    }
    };
    
    getLoc();
}

// Add a submit event listener to the form
document.getElementById('flood-report-form').addEventListener('submit', async function (event) {
    console.log("Submit button clicked!");

    // Prevent the default form submission behavior (page reload)
    event.preventDefault();

    console.log("Ready for checks");

    // Get form input values
    const email = document.getElementById('email').value.toLowerCase();
    const phoneNumber = document.getElementById('phone_number').value;
    const description = document.getElementById('description').value;
    const severity = document.getElementById('severity').value;

    // Validate email format
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
        alert("Please enter a valid email address.");
        return;
    }

    console.log("Email address test passed!");

    // Validate phone number (digits only, 10–15 digits)
    const phoneRegex = /^\d{10,15}$/;
    if (phoneNumber && !phoneRegex.test(phoneNumber)){
        alert("Please enter a valid phone number (10–15 digits, digits only).");
        return;
    }

        console.log("phone test passed!");


    // Validate description length
    if (description.length > 255) {
        alert("Description must be no more than 255 characters.");
        return;
    }

    console.log("description  test passed!");


    // Validate severity selection
    if (!severity || severity === "Choose") {
        alert("Please select a valid severity level.");
        return;
    }

        console.log("severity test passed!");


    // Create a FormData object to hold form input values
    const formData = new FormData();
    formData.append('email', document.getElementById('email').value); // Email (required)
    formData.append('phone_number', document.getElementById('phone_number').value); // Phone number (optional)
    formData.append('description', document.getElementById('description').value); // Description (optional)
    formData.append('picture', document.getElementById('picture').files[0]); // Picture file (optional)
    formData.append('severity', document.getElementById('severity').value); // Severity (required)

    if(currloc) {
        formData.append('location', true);
        formData.append('lat', lat);
        formData.append('long', long);
        console.log("appended location data");
    }
    else {
        formData.append('location', false);
        formData.append('lat', 0);
        formData.append('long', 0);
        console.log("appended no location data");
    }

    try {
        // Send a POST request to the backend API
        const response = await fetch('/api/reports', {
            method: 'POST',
            body: JSON.stringify({
                email: formData.get('email'), // Get email value
                phone_number: formData.get('phone_number'), // Get phone number value
                description: formData.get('description'), // Get description value
                severity: formData.get('severity'), // Get severity value
                location: formData.get('location'),
                lat: formData.get('lat'),
                long: formData.get('long')
            }),
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data format
            }
        });

        // Handle the server's response
        if (response.ok) {
            // If successful, display the report ID in an alert
            const result = await response.json();
            alert(`Flood report submitted successfully. Report ID: ${result.report_id}`);
        } else {
            // If an error occurred, display the error message
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (err) {
        // Handle unexpected errors (e.g., network issues)
        alert(`An unexpected error occurred: ${err}`);
    }
});
