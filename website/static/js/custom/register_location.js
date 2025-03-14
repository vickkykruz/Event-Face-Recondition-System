    let map, marker;
    const platform = new H.service.Platform({
        apikey: "tKFTVWEqw2xC9os4eEjo-TU76mqnLmZ0c4Ra9S5yhps"
    });

    function initMap() {
        const defaultLocation = { lat: 6.5244, lng: 3.3792 }; // Lagos, Nigeria
        const defaultLayers = platform.createDefaultLayers();

        // Check if location details exist
        const locationDetails = document.getElementById("location_details");
        let initialLocation = defaultLocation;
        let useStaticLocation = false;

        if (locationDetails) {
            const lat = parseFloat(locationDetails.getAttribute("data-latitude"));
            const lng = parseFloat(locationDetails.getAttribute("data-longitude"));
            if (!isNaN(lat) && !isNaN(lng)) {
                initialLocation = { lat, lng };
                useStaticLocation = true; // Prevent updates if this is true
            }
        }


        map = new H.Map(
            document.getElementById("mapContainer"),
            defaultLayers.vector.normal.map,
            {
                center: initialLocation,
                zoom: 15,
                pixelRatio: window.devicePixelRatio || 1
            }
        );

        // Enable interaction
        window.addEventListener("resize", () => map.getViewPort().resize());
        new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
        H.ui.UI.createDefault(map, defaultLayers);

        // Create marker
        marker = new H.map.Marker(initialLocation, { volatility: true });
        marker.draggable = false; // The user shouldn't be able to drag the live location marker
        map.addObject(marker);

        // If static location is used, stop further updates
        if (useStaticLocation) {
          return;
        }

        // Function to update coordinates on the UI
        function updateLatLng(coords) {
            document.getElementById("latitude").value = coords.lat.toFixed(6);
            document.getElementById("longitude").value = coords.lng.toFixed(6);
            document.getElementById("lat").innerText = coords.lat.toFixed(6);
            document.getElementById("lng").innerText = coords.lng.toFixed(6);
        }

        // Update the initial position
        updateLatLng(defaultLocation);

        // Watch for user's real-time location
        console.log("navigator.geolocation: ", navigator.geolocation)
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(
                function (position) {
                    console.log("Latitude:", position.coords.latitude);
                    console.log("Longitude:", position.coords.longitude);
                    const userLocation = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };

                    // Move the marker to the new location
                    marker.setGeometry(userLocation);

                    // Smoothly pan the map to the new location
                    map.setCenter(userLocation);

                    // Update the displayed latitude and longitude
                    updateLatLng(userLocation);
                },
                function (error) {
                   console.error("Geolocation error:", error);
                    showAlert("Real-time location tracking failed. Using default location.");
                    //alert("Real-time location tracking failed. Using default location.");
                },
                {
                    enableHighAccuracy: true, // Use GPS for better accuracy
                    maximumAge: 0, // Don't use cached positions
                    timeout: 10000 // Maximum time to wait for location update
                }
            );
        } else {
           console.error("Geolocation is not supported by this browser.");
        }

    }

    document.getElementById("venueForm").addEventListener("submit", function (event) {
      event.preventDefault();

      // Disable the submit button
      const submitBtn = document.getElementById("submitBtn");
      submitBtn.disabled = true;
      submitBtn.innerHTML = "Processing...";

      // Get input values
    const venueName = document.getElementById("venueName").value.trim();
    const venueDesc = document.getElementById("venueDesc").value.trim();
    const venueAddress = document.getElementById("venueAddress").value.trim();
    const latitude = document.getElementById("latitude").value.trim();
    const longitude = document.getElementById("longitude").value.trim();

      // Validate inputs
    if (!venueName || !venueDesc || !venueAddress || !latitude || !longitude) {
        showError("Error: Missing Requirement");
        resetForm();
        return;
    }

    // Prepare data to send
    const venueData = { name: venueName, description: venueDesc, address: venueAddress, latitude, longitude };

            fetch("/admin/page/register-venue", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(venueData)
            })
            .then(response => response.json())
            .then(data => {
                showSuccess(data.message);
        	resetForm();
            })
            .catch(error => {
                console.error("Error:", error);
        	showError("Something went wrong! Please try again.");
        	resetForm();
            });
        });

        // Function to reset the form and re-enable the button
function resetForm() {
    document.getElementById("venueForm").reset(); // Reset form fields
    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = false;
    submitBtn.innerHTML = "Submit"; // Restore button text
}


      function showAlert(message) {
        // Check if an alert already exists, remove it
        let existingAlert = document.getElementById("locationAlert");
    if (existingAlert) {
        existingAlert.remove();
    }

    // Create a Bootstrap alert div
    let alertDiv = document.createElement("div");
    alertDiv.id = "locationAlert";
    alertDiv.className = "alert alert-warning alert-dismissible fade show d-flex justify-content-between mt-3";
    alertDiv.setAttribute("role", "alert");

    // Set alert content
    alertDiv.innerHTML = `
        <div>
            <strong>Warning!!!</strong> ${message}
        </div>
        <div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // Append to a container (e.g., inside a div with id="alertContainer")
    document.getElementById("alertContainer").appendChild(alertDiv);
}

   // Function to display error messages
function showError(message) {
    let errorDiv = document.getElementById("errorContainer");
    errorDiv.innerHTML = `<p style="font-size: 1.1rem; font-weight: 900;" class="text-danger text-center my-3">${message}</p>`;
}

// Function to display success messages
function showSuccess(message) {
    let successDiv = document.getElementById("errorContainer");
    successDiv.innerHTML = `<p style="font-size: 1.1rem; font-weight: 900;" class="text-success text-center my-3">${message}</p>`;
}



    // Ensure map initializes on page load
    window.onload = initMap;
