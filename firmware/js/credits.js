document.addEventListener('DOMContentLoaded', function() {
    setActiveLink();
    loadContributors();
});

function setActiveLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    
    links.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

function loadContributors() {
    // Example: Assuming the contributors' data could be fetched from an API
    fetch('/contributors')
        .then(response => response.json())
        .then(contributors => {
            const listElement = document.querySelector('.credits-list');
            contributors.forEach(contributor => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div class="credit-info">
                        <h3>${contributor.name}</h3>
                        <div class="social-links">
                            ${contributor.socialLinks.map(link => `
                                <a href="${link.url}" target="_blank">
                                    <img src="${link.icon}" alt="${link.name}">
                                </a>
                            `).join('')}
                        </div>
                    </div>
                `;
                listElement.appendChild(li);
            });
        })
        .catch(error => console.error('Failed to load contributor data:', error));
}