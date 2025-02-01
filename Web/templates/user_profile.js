document.addEventListener('DOMContentLoaded', function() {
    const userId = window.location.pathname.split('/').pop();
    fetch(`/user/${userId}`)
        .then(response => response.json())
        .then(data => {
            const userProfile = document.getElementById('user-profile');
            userProfile.innerHTML = `
                <div class="user-info">
                    <label>Numéro d'étudiant:</label>
                    <span>${data.id}</span>
                </div>
                <div class="user-info">
                    <label>Prénom:</label>
                    <span>${data.first_name}</span>
                </div>
                <div class="user-info">
                    <label>Nom:</label>
                    <span>${data.last_name}</span>
                </div>
                <div class="user-info">
                    <label>Adresse:</label>
                    <span>${data.address}</span>
                </div>
                <div class="user-info">
                    <label>Conducteur:</label>
                    <span>${data.is_driver ? 'Oui' : 'Non'}</span>
                </div>
            `;
        })
        .catch(error => console.error('Erreur:', error));
});