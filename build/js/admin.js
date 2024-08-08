function loadConfig() {
    fetch('/get_config')
        .then(response => response.json())
        .then(config => {
            document.getElementById('startupColor').value = config.startupColor;
            document.getElementById('apPassword').value = config.apPassword;
            document.getElementById('personalizedMsg').value = config.personalizedMsg;
            document.getElementById('coeff1').value = config.coeff1;
            document.getElementById('coeff2').value = config.coeff2;
            document.getElementById('coeff3').value = config.coeff3;
            document.getElementById('version').value = config.version;
        })
        .catch(error => console.error('Error loading config:', error));
}

function saveConfig() {
    const config = {
        startupColor: document.getElementById('startupColor').value,
        apPassword: document.getElementById('apPassword').value,
        personalizedMsg: document.getElementById('personalizedMsg').value,
        coeff1: parseFloat(document.getElementById('coeff1').value),
        coeff2: parseFloat(document.getElementById('coeff2').value),
        coeff3: parseFloat(document.getElementById('coeff3').value),
        version: document.getElementById('version').value,
    };

    fetch('/set_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        alert('Configuration saved successfully!');
    })
    .catch(error => {
        console.error('Error saving config:', error);
        alert('Failed to save configuration.');
    });
}
