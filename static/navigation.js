function showContent(sectionId) {
    // Hide all sections
    document.getElementById('homeContent').classList.add('hidden');
    document.getElementById('recorderContent').classList.add('hidden');
    document.getElementById('aboutContent').classList.add('hidden');
    console.log("sectionId", `${sectionId}Content`)
    // Show the selected section
    document.getElementById(`${sectionId}Content`).classList.remove('hidden');

    if (sectionId === 'recorder') {
        document.getElementById('homeContent').classList.remove('hidden');
    }
    // Enable or disable recorder tab based on the sectionId
    var recorderTab = document.getElementById('recorderContent');
    if (sectionId === 'home') {
        // Enable recorder tab when on the home page
        recorderTab.disabled = false;
    } else {
        // Disable recorder tab for other sections
        recorderTab.disabled = true;
    }

    // Additional logic for the recorder popup
    var recorderPopup = document.getElementById('recorderPopup');
    var closeButton = document.getElementById('close');

    if (`${sectionId}Content` === "recorderContent") {
        console.log("popup")
        recorderPopup.style.display = 'block';
    } else {
        recorderPopup.style.display = 'none';
    }

    // Add click event listener to close the popup
    closeButton.addEventListener('click', function () {
        // Hide the popup
        recorderPopup.style.display = 'none';
    });
}
