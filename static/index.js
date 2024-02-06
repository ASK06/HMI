document.addEventListener("DOMContentLoaded", function () {
    // Get references to the button and status text elements
    const connectButton = document.getElementById("hmi_connect_disconnect");
    const statusText = document.getElementById("status_text");
    const screenImage = document.getElementById("display_image");
    const otherButtons = document.querySelectorAll(".main-frame button:not(#hmi_connect_disconnect)");
    const captureScreenButton = document.getElementById("capture_screen");
    const videoRecordingButton = document.getElementById("video_recording");

    // Add references to the navigation buttons (F1_KEY, F2_KEY, F3_KEY, etc.)
    const f1Button = document.getElementById("F1_KEY");
    const f2Button = document.getElementById("F2_KEY");
    const f3Button = document.getElementById("F3_KEY");
    const upButton = document.getElementById("UP_KEY");
    const downButton = document.getElementById("DOWN_KEY");
    const rightButton = document.getElementById("RIGHT_KEY");
    const leftButton = document.getElementById("LEFT_KEY");
    const centerButton = document.getElementById("CENTER_KEY");
    const dfButton = document.getElementById("DF_KEY");
    const ccButton = document.getElementById("CC_KEY");
    const gaButton = document.getElementById("GA_KEY");
    const mmpButton = document.getElementById("MMP_KEY");

    // Initial state
    let isConnected = false;
    let isRecording = false;
    let isSetup = false;
    let updateInterval;

    function UpdateSSHStatus() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", '/get_ssh_status', true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.result === true) {
                    if (response.server === true) {
                        isConnected = true;
                        updateStatus();
                    } else {
                        isConnected = false;
                        isSetup = true;
                        updateStatus();
                    }
                } else {
                    isConnected = false;
                    isSetup = false;
                    updateStatus();
                }
            }
        };
        xhr.send();
    }
    setInterval(UpdateSSHStatus, 700);

    // Function to update button and status text
    function updateStatus() {
        if (isConnected) {
            connectButton.textContent = "Disconnect HMI";
            statusText.textContent = "Connected";
            statusText.style.color = "green"; // Set the color to green for "Connected" state
            enableButtons(otherButtons, true);
            update_image();
//            updateScreenImage(true);
        } else {
            if (isSetup) {
                connectButton.textContent = "Connect HMI";
                statusText.textContent = "Connecting....please wait";
                statusText.style.color = "yellow";
                enableButtons(otherButtons, false);
                updateScreenImage(false);
            } else {
                connectButton.textContent = "Connect HMI";
                statusText.textContent = "Disconnected";
                statusText.style.color = "red";
                enableButtons(otherButtons, false);
                updateScreenImage(false);
            }
        }
    }

    // Function to enable or disable buttons
    function enableButtons(buttons, isEnabled) {
        buttons.forEach(function (button) {
            button.disabled = !isEnabled;
        });
    }

    // Function to update the screen image with a cache-busting query parameter
    function updateScreenImage(isConnected) {
        const imageSrc = isConnected
            ? `static/assets/hat_current_image.jpg?cache=${new Date().getTime()}`
            : "";
        screenImage.src = imageSrc;
    }

    // Function to capture and update the image
    function update_image() {
        // Make an AJAX request to trigger the image update
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/update_image_route", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // The image update request was successful
                updateScreenImage(true); // Update the image on the client side
            }
        };
        xhr.send(JSON.stringify({ action: "update_image" }));
    }

    function save_image() {
        // Make an AJAX request to trigger the image update
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/save_image_route", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // The image update request was successful
                updateScreenImage(true); // Update the image on the client side
            }
        };
        xhr.send(JSON.stringify({ action: "update_image" }));
    }

    // Function to start video recording
    function startRecording() {
        // Make an AJAX request to the Flask route for starting video recording
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/start_video_recording", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // The request was successful, you can update the UI if needed
                isRecording = true;
                videoRecordingButton.textContent = "Stop Recorder";
                connectButton.disabled = true;
                captureScreenButton.disabled = true;
                // Start the interval to update the screen image
            }
        };
        xhr.send(JSON.stringify({ action: "start_recording" }));
    }


    function stopRecording() {
        // Make an AJAX request to the Flask route for stopping video recording
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/stop_video_recording", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                // The request was successful, you can update the UI if needed
                isRecording = false;
                videoRecordingButton.textContent = "Video Recorder";
                connectButton.disabled = false;
                captureScreenButton.disabled = false;
                clearInterval(updateInterval)
            }
        };
        xhr.send(JSON.stringify({ action: "stop_recording" }));
    }

    //function for handling button clicks
    function handleButtonClicked(buttonElement, keyName) {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/press_key_route", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(keyName, 'pressed')
            }
        };
        xhr.send(JSON.stringify({ action: "press_key", key_name: keyName }));
    }

    // Function to display a warning message
    function showWarningMessage(message) {
        alert(message); // You can replace this with a styled modal or notification
    }

    // Initial update of the status
    enableButtons(otherButtons, false); // Disable all buttons except "hmi_connect_disconnect"
    updateStatus();

    // Add click event listener to the "Start Recorder" button
    videoRecordingButton.addEventListener("click", function () {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });


    // Add click event listener to the "Capture Screen" button
    captureScreenButton.addEventListener("click", function () {
        // Call the update_image() function to capture and update the image
        save_image();
    });

    // Common ancestor of your buttons
    const keyboardContainer = document.querySelector('.keyboard');

    // Event delegation for button clicks
    keyboardContainer.addEventListener('click', function (event) {
        const buttonId = event.target.id;
        if (buttonId) {
            handleButtonClicked(event.target, buttonId);
        }
    });


    // Add click event listener to the "Connect/Disconnect" button
    connectButton.addEventListener("click", function () {
        if (isConnected) {
            // Make an AJAX request to the Flask route for disconnect
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/disconnect_hmi", true);
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    isConnected = false;
                    isSetup = false;
                    updateStatus();
                }
            };
            xhr.send(JSON.stringify({ action: "disconnect" }));
        } else {
            // Make an AJAX request to the Flask route for connect
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/connect_hmi", true);
            xhr.setRequestHeader("Content-Type", "application.json");
            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    updateStatus();
                }
            };
            xhr.send(JSON.stringify({ action: "connect" }));
        }
    });
});



