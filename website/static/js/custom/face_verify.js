const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("capture");
const submitBtn = document.getElementById("submit");
const statusText = document.getElementById("status")

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(error => { console.error("Error accessing webcam:", error); });

// Capture image from video
captureBtn.addEventListener("click", () => {
    const context = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to Base64
    const imageData = canvas.toDataURL("image/png");

    // Show submit button
    submitBtn.style.display = "inline-block";

    // Save captured image
    submitBtn.dataset.image = imageData;
});

// Submit image for verification
submitBtn.addEventListener("click", () => {
    const imageData = submitBtn.dataset.image;

    fetch(verifyUrl, {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusText.innerText = "✅ Face Verified! Redirecting...";
            statusText.classList.add("text-success", "fw-bold");

            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 3000);
        } else {
            statusText.innerText = "❌ " + data.error;
            statusText.classList.add("text-danger", "fw-bold");
        }
    })
    .catch(error => {
        console.error("Error verifying face:", error);
        statusText.innerText = "❌ Verification Failed. Try Again.";
        statusText.classList.add("text-danger", "fw-bold");
    });
});

