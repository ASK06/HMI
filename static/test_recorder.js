// Wait for the DOM to be ready
document.addEventListener("DOMContentLoaded", function () {
  // Get references to the buttons and other elements
  var recordButton = document.getElementById("record");
  var displayImage=document.getElementById('display_image')
  var fullScreen = document.getElementById("fullScreen");
  var cropScreen = document.getElementById("cropScreen");
  var stopButton = document.getElementById("stop");
  var saveButton = document.getElementById("save");
  var uploadButton = document.getElementById("upload");
  var copyButton = document.getElementById("copy");


  let isRecording = false;
  let recordedActions = [];


  // Initially display only the specified buttons
  show(['record', 'fullScreen', 'cropScreen', 'save', 'upload', 'clipboard'], true);
  show(['stop'], false); // Hide other buttons initially


  // Event listeners for the buttons
  recordButton.addEventListener("click", async function () {
    // Handle record button click
    console.log("Record button clicked");
    toggle({ target: recordButton, canSave: false });
    await startRecording();
  });

  stopButton.addEventListener("click", function () {
    // Handle stop button click
    stopRecording();
    console.log("Stop button clicked");
    toggle({ target: stopButton, canSave: true });
  });

  cropScreen.addEventListener("click", function () {
    // Handle cropScreen button click
    openRegionCaptureWindow();
    console.log("cropScreen button clicked");
    toggle({ target: cropScreen, canSave: false });
  });

  fullScreen.addEventListener("click", function () {
    // Handle fullScreen button click
    console.log("fullScreen button clicked");
    captureFullScreen();
    toggle({ target: fullScreen, canSave: false });
  });

  saveButton.addEventListener("click", function () {
    // Handle save button click
    downloadRobotFile();
    console.log("Save button clicked");
    toggle({ target: saveButton, canSave: true });
  });

  uploadButton.addEventListener('click', () => {
        document.getElementById('fileInput').click();
  });

  fileInput.addEventListener('change', (event) => {
        handleFileSelection(event);
  });

  copyButton.addEventListener("click", function () {
    // Handle copy button click
    const textarea = document.getElementById('robotScript');
    textarea.select();
    document.execCommand('copy');
    textarea.setSelectionRange(0, 0);
    alert('Copied to clipboard');
    console.log("Copy button clicked");
    toggle({ target: copyButton, canSave: false });
  });


  // You can add more functionality and event listeners as needed.
  function toggle(e) {
    // Existing toggle function...
    console.log("Toggle function called");
    logger(e.target.id);
    if (e.target.id === 'record' || e.target.id === 'fullScreen' || e.target.id === 'cropScreen') {
      show(['stop'], true);
      show(['record'], false);
    } else if (e.target.id === 'stop') {
      show(['record', 'save'], true);
      show(['resume', 'stop', 'pause'], false);
      enable(['settings-panel'], true);
    } else if (e.target.id === 'settings') {
      analytics(['_trackEvent', 'settings', '⚙️']);
      settingsPanel.classList.toggle('hidden');
    }

    if ((e.canSave === false) || (e.target.id === 'record')) {
      saveButton.disabled = true;
    } else if ((e.canSave === true) || (e.target.id === 'stop')) {
      saveButton.disabled = false;
    }
  }

  // Sample utility functions used in the `toggle` function
  function show(ids, isVisible) {
    ids.forEach(function (id) {
      var element = document.getElementById(id);
      if (element) {
        element.style.display = isVisible ? 'inline-block' : 'none';
      }
    });
  }

  function enable(ids, isEnabled) {
    ids.forEach(function (id) {
      var element = document.getElementById(id);
      if (element) {
        element.disabled = !isEnabled;
      }
    });
  }

  function logger(message) {
    console.log(message);
  }


  async function startRecording() {
        isRecording = true;
        recordedActions = [];
        updateDisplay();
       try {
           const defaultPath = 'HMI Web_App_1\\HMI Web_App\\Test Results\\Test Scripts';
           const rootDirectory = await showDirectoryPicker({ defaultPath });
           const projectName = prompt('Enter the project name:');
           if (!projectName) {
               console.log('Project creation cancelled by user.');
               return;
           }
           const projectDirectoryHandle = await rootDirectory.getDirectoryHandle(projectName, { create: true });
           const testCaseName = prompt('Enter the test case name:');
           if (!testCaseName) {
               console.log('Test case creation cancelled by user.');
               return;
           }
           const testCaseExists = await directoryExists(projectDirectoryHandle, testCaseName);
           if (testCaseExists) {
               const overrideConfirmed = confirm('The test case directory already exists. Do you want to override it?');
               if (!overrideConfirmed) {
                   console.log('Test case creation cancelled by user.');
                   return;
               }
           }
           const testCaseHandle = await projectDirectoryHandle.getDirectoryHandle(testCaseName, { create: true });
           const imagesFolder = await testCaseHandle.getDirectoryHandle('images', { create: true });
           const robotScriptFile = await testCaseHandle.getFileHandle('robot_script.robot', { create: true });
           console.log('Test case path:', testCaseHandle);
           alert(`Recording started in project: ${projectName}, Test case: ${testCaseName}`);
       } catch (error) {
           console.error('Error:', error.message || error);
       }
  }
  async function directoryExists(parentDirectoryHandle, directoryName) {
       try {
           await parentDirectoryHandle.getDirectoryHandle(directoryName);
           return true;
       } catch (error) {
           if (error.name === 'NotFoundError') {
               return false;
           }
           throw error;
       }
  }

  function stopRecording() {
        isRecording = false;
  }

  function downloadRobotFile() {
        const robotScript=document.getElementById('robotScript').value;
        const blob = new Blob([robotScript], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'recorded_script.robot';
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
  }

    function addRecordedAction(buttonId) {
        if (isRecording) {
            recordedActions.push(buttonId);
            updateDisplay();
        }
    }

        // Add click event listener to all buttons that should be recorded
    const buttonsToRecord = document.querySelectorAll('.horizontal-button, .vertical-button');
    buttonsToRecord.forEach(button => {
        button.addEventListener('click', function () {
        addRecordedAction(button.id);
        });
    });


    function openFileSelection() {
       const uploadInput = document.createElement('input');
       uploadInput.type = 'file';
       uploadInput.accept = '.robot';
       uploadInput.style.display = 'none'; // Hide the file input
       uploadInput.addEventListener('change', (event) => handleFileSelection(event));
       document.body.appendChild(uploadInput);
       uploadInput.click();
       document.body.removeChild(uploadInput);
    }

    function handleFileSelection(event) {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            uploadedFileName = selectedFile.name;
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedFileContent = e.target.result;
                const keysArray = extractContentAfterId(uploadedFileContent);
                displayKeys(keysArray);
            };
            reader.readAsText(selectedFile);

            // Clear the input value to enable uploading the same file again
            event.target.value = '';
        }
    }

    function extractContentAfterId(content) {
      return content.split('\n').map(line => {
        const matchId = /id:(\S+)/.exec(line);
        const matchCompare = /Compare Images\s+(.+)$/.exec(line);

        if (matchId) {
          return matchId[1]; // Extract the part after 'id'
        } else if (matchCompare) {
          const paths = matchCompare[1].split(/\s+/); // Split by whitespace
          return paths[paths.length - 1]; // Return the last element (second path)
        } else {
          return '';
        }
      }).filter(Boolean); // Filter out any empty strings
    }

    function displayKeys(keysArray) {
       recordedActions=recordedActions.concat(keysArray);
       updateDisplay();
    }

    function updateDisplay() {
       const textarea = document.getElementById('robotScript');

        let formattedActions = [];

        if (isRecording) {
            // Display initial settings and test cases when recording
            formattedActions.push('    Open Browser   http://127.0.0.1:5000/  gc');
            formattedActions.push('    Maximize Browser Window');
        }
        formattedActions = formattedActions.concat(recordedActions.map((action, index) => {
            let formattedAction;
            if (action.endsWith('KEY')) {
                formattedAction = `    Click Element  id:${action}`;
            } else if (action.endsWith('.jpg')) {
                formattedAction = `    Compare Images  static\\images\\hat_current_image.jpg  ${action}`;
            }
            return `${formattedAction}`;
        }));
        const robotScript = `*** Settings ***\nLibrary SeleniumLibrary\n\n*** Test Cases ***\nRecorded Actions\n${formattedActions.join('\n')}\n    Close Browser`;
        textarea.value = robotScript;
    }

    function captureFullScreen() {
        if (isRecording){
            const imageElement = document.getElementById('display_image');
            const canvas = document.createElement('canvas');
            canvas.width = 800;
            canvas.height = 480;
            const context = canvas.getContext('2d');
            context.drawImage(imageElement, 0, 0);
            canvas.toBlob(blob => {
                const filename = 'full_screen_screenshot.jpg';
                window.showDirectoryPicker()
                    .then(fileHandle => {
                        const imagePath = fileHandle.name + '/' + filename; // Extracted from the fileHandle
                        recordedActions.push(imagePath); // Add imagePath to recordedActions
                        return fileHandle.getFileHandle(filename, { create: true });
                    })
                    .then(file => file.createWritable())
                    .then(writable => {
                        writable.write(blob);
                        return writable.close();
                    })
                    .then(() => {
                        updateDisplay(); // Update the display with the new path
                    })
                    .catch(error => console.error('Error saving file:', error));
            }, 'image/jpeg');
        }

    }

    function openRegionCaptureWindow() {
        const previewImage = document.getElementById('display_image');
        const regionCaptureWindow = window.open('', 'Region Capture', 'width=800,height=600');

        regionCaptureWindow.document.body.innerHTML = `
            <div>
                <img id="capturedImage" src="${previewImage.src}" style="cursor:crosshair;">
                <button id="cropButton">Crop</button>
                <span id="coordinates"></span>
            </div>`;

        const capturedImage = regionCaptureWindow.document.getElementById('capturedImage');
        const cropButton = regionCaptureWindow.document.getElementById('cropButton');
        const coordinatesSpan = regionCaptureWindow.document.getElementById('coordinates');

        let isCropping = false;
        let startX, startY, cropBox;

        capturedImage.style.cursor = 'initial';
        capturedImage.draggable = false;
        coordinatesSpan.textContent = '';

        capturedImage.addEventListener('mousemove', (event) => {
            if (isCropping) {
                const x = event.clientX - capturedImage.getBoundingClientRect().left;
                const y = event.clientY - capturedImage.getBoundingClientRect().top;
                coordinatesSpan.textContent = `Coordinates: (${x}, ${y})`;
            }
        });

        cropButton.addEventListener('click', () => {
            isCropping = true;
            coordinatesSpan.textContent = 'Select the region to crop.';
            capturedImage.style.cursor = 'crosshair';
            capturedImage.addEventListener('mousedown', startCrop);
            capturedImage.addEventListener('mouseup', finishCrop);
        });

    function startCrop(event) {
        startX = event.clientX - capturedImage.getBoundingClientRect().left;
        startY = event.clientY - capturedImage.getBoundingClientRect().top;

        cropBox = regionCaptureWindow.document.createElement('div');
        cropBox.style.position = 'absolute';
        cropBox.style.border = '2px dashed red';
        cropBox.style.left = `${startX}px`;
        cropBox.style.top = `${startY}px`;

        capturedImage.parentElement.appendChild(cropBox);

        capturedImage.removeEventListener('mouseup', finishCrop);
        capturedImage.addEventListener('mousemove', updateCrop);
        capturedImage.addEventListener('mouseup', finishCrop);
    }

    function updateCrop(event) {
        if (isCropping) {
            const x = event.clientX - capturedImage.getBoundingClientRect().left;
            const y = event.clientY - capturedImage.getBoundingClientRect().top;

            cropBox.style.width = `${Math.abs(x - startX)}px`;
            cropBox.style.height = `${Math.abs(y - startY)}px`;
            cropBox.style.left = `${Math.min(startX, x)}px`;
            cropBox.style.top = `${Math.min(startY, y)}px`;
        }
    }

    function finishCrop() {
        isCropping = false;
        capturedImage.style.cursor = 'initial';

        const x = parseInt(cropBox.style.left.replace('px', ''));
        const y = parseInt(cropBox.style.top.replace('px', ''));
        const width = parseInt(cropBox.style.width.replace('px', ''));
        const height = parseInt(cropBox.style.height.replace('px', ''));

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = width;
        canvas.height = height;

        ctx.drawImage(capturedImage, x, y, width, height, 0, 0, width, height);

    // Download the cropped image as 'croppedimage.jpg'
        const croppedImageData = canvas.toDataURL('image/jpeg');
        const croppedDownloadLink = document.createElement('a');
        croppedDownloadLink.href = croppedImageData;
        croppedDownloadLink.download = 'croppedimage.jpg';
        croppedDownloadLink.click();

    // Download the original 'display_image'
        const originalImageData = previewImage.src;
        const originalDownloadLink = document.createElement('a');
        originalDownloadLink.href = originalImageData;
        originalDownloadLink.download = 'originalimage.jpg';
        originalDownloadLink.click();

        capturedImage.removeEventListener('mousemove', updateCrop);
        capturedImage.removeEventListener('mouseup', finishCrop);
        cropBox.remove();
    }
}
















//    function openRegionCaptureWindow() {
//        const displayImage = document.getElementById('display_image');
//        let isCropping = false;
//        let startX, startY, cropBox;
//        displayImage.style.cursor = 'crosshair';
//        displayImage.draggable = false;
//        displayImage.addEventListener('mousedown', startCrop);
//    function startCrop(event) {
//        isCropping = true;
//        startX = event.clientX - displayImage.getBoundingClientRect().left;
//        startY = event.clientY - displayImage.getBoundingClientRect().top;
//        cropBox = document.createElement('div');
//        cropBox.style.position = 'absolute';
//        cropBox.style.border = '2px solid red';
//        cropBox.style.left = `${startX}px`;
//        cropBox.style.top = `${startY}px`;
//        displayImage.parentElement.appendChild(cropBox);
//        displayImage.addEventListener('mousemove', updateCrop);
//        document.addEventListener('mouseup', finishCrop);
//    }
//    function updateCrop(event) {
//        if (isCropping) {
//            const x = event.clientX - displayImage.getBoundingClientRect().left;
//            const y = event.clientY - displayImage.getBoundingClientRect().top;
//            cropBox.style.width = `${x - startX}px`;
//            cropBox.style.height = `${y - startY}px`;
//        }
//    }
//    let hasDownloaded = false;
//    async function finishCrop(event) {
//      isCropping = false;
//      displayImage.style.cursor = 'initial';
//      try {
//        if (!hasDownloaded) {
//          const directoryHandle = await window.showDirectoryPicker();
//          const x = Math.min(startX, event.clientX - displayImage.getBoundingClientRect().left);
//          const y = Math.min(startY, event.clientY - displayImage.getBoundingClientRect().top);
//          const width = Math.abs(event.clientX - displayImage.getBoundingClientRect().left - startX);
//          const height = Math.abs(event.clientY - displayImage.getBoundingClientRect().top - startY);
//          // Crop the image
//          const canvasToBlob = (canvas) => {
//            return new Promise((resolve) => {
//              canvas.toBlob((blob) => {
//                resolve(blob);
//              }, 'image/jpeg');
//            });
//          };
//          const displayWidth = displayImage.naturalWidth;
//          const displayHeight = displayImage.naturalHeight;
//          const cropX = Math.max(x * (displayWidth / displayImage.clientWidth), 0);
//          const cropY = Math.max(y * (displayHeight / displayImage.clientHeight), 0);
//          const cropWidth = Math.min(width * (displayWidth / displayImage.clientWidth), displayWidth);
//          const cropHeight = Math.min(height * (displayHeight / displayImage.clientHeight), displayHeight - cropY);
//          const canvas = document.createElement('canvas');
//          const ctx = canvas.getContext('2d');
//          canvas.width = cropWidth;
//          canvas.height = cropHeight;
//          ctx.drawImage(
//            displayImage,
//            cropX,
//            cropY,
//            cropWidth,
//            cropHeight,
//            0,
//            0,
//            cropWidth,
//            cropHeight
//          );
//          // Save the cropped image
//          const croppedBlob = await canvasToBlob(canvas);
//          const croppedImageFileHandle = await directoryHandle.getFileHandle('cropped_image.jpg', { create: true });
//          const croppedImageWritable = await croppedImageFileHandle.createWritable();
//          await croppedImageWritable.write(croppedBlob);
//          await croppedImageWritable.close();
//          // Download the original image in 650x390 resolution
//          const targetWidth = 650;
//          const targetHeight = 390;
//          canvas.width = targetWidth;
//          canvas.height = targetHeight;
//          ctx.drawImage(displayImage, 0, 0, targetWidth, targetHeight);
//          const imageBlob = await canvasToBlob(canvas);
//          const imageFileHandle = await directoryHandle.getFileHandle('original_image.jpg', { create: true });
//          const imageWritable = await imageFileHandle.createWritable();
//          await imageWritable.write(imageBlob);
//          await imageWritable.close();
//          hasDownloaded = true;
//        }
//      } catch (error) {
//        console.error('Error while using showDirectoryPicker:', error);
//      } finally {
//        isDownloaded = false;
//        displayImage.removeEventListener('mousemove', updateCrop);
//        document.removeEventListener('mouseup', finishCrop);
//        cropBox.remove();
//      }
//    }
//}



});
