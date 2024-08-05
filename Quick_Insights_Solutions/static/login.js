document.getElementById('showRegister').addEventListener('click', function() {
    document.querySelectorAll('.form-container')[0].classList.add('hidden');
    document.querySelectorAll('.form-container')[1].classList.remove('hidden');
});

document.getElementById('showLogin').addEventListener('click', function() {
    document.querySelectorAll('.form-container')[1].classList.add('hidden');
    document.querySelectorAll('.form-container')[0].classList.remove('hidden');
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    fetch('http://127.0.0.1:5003/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = 'http://127.0.0.1:5003/dashboard.html';
        } else {
            alert('Login failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    fetch('http://127.0.0.1:5003/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('otpSection').classList.remove('hidden');
            document.getElementById('registerSection').classList.add('hidden');
        } else {
            alert('Registration failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('otpForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('registerEmail').value;
    const otp = document.getElementById('otp').value;

    fetch('http://127.0.0.1:5003/verify_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, otp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = 'http://127.0.0.1:5003/dashboard.html';
        } else {
            alert('OTP verification failed: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
