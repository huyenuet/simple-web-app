const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const passwordFeedback = passwordInput.nextElementSibling;

loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    event.stopPropagation();
    loginForm.classList.add('was-validated');

    if (loginForm.checkValidity() === false) {
        return;
    }

    const email = emailInput.value;
    const password = passwordInput.value;
    console.log(email)
    console.log(password)
    
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password }),
    });

    if (!response.ok) {
        const data = await response.json();
        passwordFeedback.textContent = data.detail;
        passwordInput.classList.add('is-invalid');
    }

    try {
        const data = await response.json();
        console.log('Access token:', data.access_token);
        // Save the access token and use it for authenticated API calls
        localStorage.setItem('access_token', data.access_token);
        window.location.href = data.redirect_url;
    } catch (error) {
        console.error('Login failed:', error.message);
    }
});

passwordInput.addEventListener('input', () => {
    if (passwordInput.checkValidity()) {
        passwordInput.classList.remove('is-invalid');
        passwordFeedback.textContent = '';
    } else {
        passwordInput.classList.add('is-invalid');
        passwordFeedback.textContent = 'Incorrect email or password.';
    }
});
