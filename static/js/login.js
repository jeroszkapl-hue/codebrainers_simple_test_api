// Login page logic. Depends on the shared helpers in auth.js (isTokenValid)
// and theme.js, which must be loaded first.

function showError(message) {
    const box = document.getElementById('errorBox');
    box.innerText = message;
    box.style.display = 'block';
}

function clearError() {
    const box = document.getElementById('errorBox');
    box.innerText = '';
    box.style.display = 'none';
}

// If already logged in with a valid token, skip the login screen.
if (isTokenValid()) {
    window.location.href = '/';
}

document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    clearError();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    let res;

    try {
        res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
    } catch (err) {
        showError('Unable to reach the server');
        return;
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        showError(error.detail || 'Invalid username or password');
        return;
    }

    const data = await res.json();

    localStorage.setItem('token', data.access_token);
    localStorage.setItem('token_expires_at', Date.now() + data.expires_in * 1000);

    window.location.href = '/';
});
