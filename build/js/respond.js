function triggerResponse() {
    // Fetch the target AP name first
    fetch('/get_ap_name')
        .then(response => response.json())
        .then(data => {
            // Display the AP name
            const responseText = document.getElementById('responseText');
            responseText.textContent = data.response;

            // Start the update polling
            startPolling();
        })
        .catch(error => {
            console.error('Error fetching AP name:', error);
            document.getElementById('responseText').textContent = "Failed to fetch AP name";
        });
}

function startPolling() {
    const endTime = Date.now() + 10 * 60 * 1000; // Stop after 10 minutes

    function poll() {
        if (Date.now() >= endTime) {
            document.getElementById('responseText').textContent = "Polling ended.";
            return;
        }

        // Send an AJAX request to get updates
        fetch('/get_scan_update')
            .then(response => response.json())
            .then(data => {
                // Check if the status field is true
                if (data.status === true) {
                    document.getElementById('responseText').textContent = data.update;
                    return; // Exit the function after handling the complete state
                }

                // Update the display with the result from the server
                document.getElementById('responseText').textContent = data.update;

                // Schedule the next poll
                setTimeout(poll, 1000); // Poll after a response has been handled
            })
            .catch(error => {
                console.error('Error during update polling:', error);
                setTimeout(poll, 1000); // Attempt to poll again after an error
            });
    }

    poll(); // Start the polling process
}

document.addEventListener('DOMContentLoaded', function() {
    var currentPath = window.location.pathname;
    var links = document.querySelectorAll('.nav-link');

    links.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});