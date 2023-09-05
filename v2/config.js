document.addEventListener('DOMContentLoaded', function () {
    const submitButton = document.getElementById('submitButton');

    submitButton.addEventListener('click', function () {

        const originalBackgroundColor = this.style.backgroundColor;
        this.style.backgroundColor = '#3f3535';

        setTimeout(() => {
            this.style.backgroundColor = originalBackgroundColor;
        }, 500);


    });
});
