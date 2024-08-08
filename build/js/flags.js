document.addEventListener('DOMContentLoaded', function() {
    var currentPath = window.location.pathname;
    var links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Fetch flag statuses and then initialize the flags
    fetch('/flags_status')
        .then(response => response.json())
        .then(flagStatuses => {
            initializeFlags(flagStatuses);
        })
        .catch(error => {
            console.error('Failed to load flags:', error);
        });
});

function initializeFlags(flagStatuses) {
    const flags = ["Easy", "Comms", "Dial", "Credits", "Firmware", "Authorized", "Respond", "Secured"];
    const container = document.getElementById('flagsContainer');
    flags.forEach(flag => {
        const captured = flagStatuses[flag];
        const statusText = captured ? "Captured" : "Not Captured";
        const color = captured ? "green" : "red";
        container.innerHTML += `
            <div class="flag-entry">
                <div class="flag-details">
                    <h3 class="center">${flag} Flag</h3>
                </div>
                <div class="flag-input">
                    <input type="text" id="${flag.toLowerCase()}FlagInput" placeholder="${captured ? 'CAPTURED' : 'Enter ' + flag + ' Flag'}" value="${captured ? 'FLAG CAPTURED' : ''}" ${captured ? 'disabled' : ''}>
                    <button onclick="captureFlag('${flag}')" ${captured ? 'disabled' : ''}>Capture</button>
                </div>
                <div class="flag-indicator">
                    <p class="center capture-indicator" id="captureIndicator-${flag}" style="color: ${color};">${statusText}</p>
                </div>
            </div>
        `;
    });
}

function captureFlag(flagName) {
    var flagValue = document.getElementById(`${flagName.toLowerCase()}FlagInput`).value;
    var inputElement = document.getElementById(`${flagName.toLowerCase()}FlagInput`);
    var buttonElement = document.querySelector(`button[onclick="captureFlag('${flagName}')"]`);
    var indicatorElement = document.getElementById(`captureIndicator-${flagName}`);

    fetch(`/capture_flag/${flagName}?value=${encodeURIComponent(flagValue)}`)
        .then(response => response.json())
        .then(data => {
            indicatorElement.textContent = data.captured ? "Captured" : "Not Captured";
            indicatorElement.style.color = data.captured ? "green" : "red";
            inputElement.value = data.captured ? "FLAG CAPTURED" : "";
            inputElement.disabled = data.captured ? true : false;
            buttonElement.disabled = data.captured ? true : false;
        })
        .catch(error => {
            console.error('Error capturing flag:', error);
            indicatorElement.textContent = "Error";
            indicatorElement.style.color = "red";
        });
}
