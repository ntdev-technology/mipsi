document.addEventListener('DOMContentLoaded', function () {
    const submitButton = document.getElementById('submitButton');
    const usernameInput = document.getElementById('UsernameInput');
    const passwordInput = document.getElementById('PasswordInput');

    submitButton.addEventListener('click', function () {

        const originalBackgroundColor = this.style.backgroundColor;
        this.style.backgroundColor = '#3f3535';

        setTimeout(() => {
            this.style.backgroundColor = originalBackgroundColor;
        }, 500);


        const username = usernameInput.value;
        const password = passwordInput.value;


        const userData = { username, password };

        fetch('/submit_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response form Backend:', data)
        })
        .catch(error => {
            console.error('Error:', error)
        })
    });
});
