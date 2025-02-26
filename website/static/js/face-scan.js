const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture');
const submitBtn = document.getElementById('submit');
const statusText = document.getElementById('status');

const previewImage = document.getElementById("preview");
const countdownText = document.getElementById("countdown");

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(error => { console.error("Error accessing webcam:", error); });

// Countdown before capturing
function startCountdown(callback) {
    let count = 3;
    countdownText.innerText = `Capturing in ${count}...`;
    const interval = setInterval(() => {
        count--;
        countdownText.innerText = `Capturing in ${count}...`;
        if (count === 0) {
            clearInterval(interval);
            countdownText.innerText = "";
            callback();
        }
    }, 1000);
}

// Capture image from video
captureBtn.addEventListener('click', () => {
    startCountdown(() => {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to Base64
        const imageData = canvas.toDataURL("image/png");

        // Display preview
        previewImage.src = imageData;
        previewImage.style.display = "block";
        previewImage.style.width = "100px";

        // Show Submit button
        submitBtn.style.display = "inline-block";
    });
});


// Submit image to Flask
submitBtn.addEventListener('click', () => {
    const imageData = canvas.toDataURL('image/png');  // Convert to base64
    console.log("Button has been clicked")

    fetch(fetchUrl, {
        method: "POST",
        body: JSON.stringify({ image: imageData }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response Data: ", data)
        if (data.success) {
            statusText.innerText = " ✅ Face Registered Successfully!";
            statusText.classList.add("text-success", "fw-bold");

            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 3000);
        } else {
            statusText.innerText = "❌ Error: " + data.error;
            statusText.classList.add("text-danger", "fw-bold");
        }
    })
    .catch(error => {
        console.error("Error submitting image:", error)
        statusText.innerText = "❌ Submission Failed. Try Again.";
        statusText.classList.add("text-danger", "fw-bold");
    });
});
