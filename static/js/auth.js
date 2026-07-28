// Shared bearer-token helpers, used by both the login page (to check if a
// session is already active) and the main Employee Manager page (to guard
// itself and attach the token to every API call).

function getToken() {
    return localStorage.getItem('token');
}

function isTokenValid() {
    const expiresAt = Number(localStorage.getItem('token_expires_at') || 0);
    return Boolean(getToken()) && Date.now() < expiresAt;
}

function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('token_expires_at');
}

function goToLogin() {
    clearToken();
    window.location.href = '/login';
}

function logout() {
    goToLogin();
}

// Wrapper around fetch that attaches the bearer token and redirects to
// the login screen if the server reports the session is no longer valid.
async function apiFetch(url, options = {}) {

    if (!isTokenValid()) {
        goToLogin();
        return Promise.reject(new Error('Not authenticated'));
    }

    const headers = Object.assign({}, options.headers, {
        Authorization: `Bearer ${getToken()}`
    });

    const res = await fetch(url, Object.assign({}, options, { headers }));

    if (res.status === 401) {
        goToLogin();
        return Promise.reject(new Error('Session expired'));
    }

    return res;
}
