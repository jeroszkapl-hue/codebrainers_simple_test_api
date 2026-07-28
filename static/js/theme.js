// Shared dark/light theme toggle, used by both the login page and the main
// Employee Manager page. The choice is persisted in localStorage so it
// survives navigation between the two pages and page reloads.

function toggleTheme() {

    const body = document.body;

    const newTheme =
        body.classList.contains('dark')
        ? 'light'
        : 'dark';

    body.className = newTheme;

    localStorage.setItem('theme', newTheme);
}

(function initTheme() {

    const saved = localStorage.getItem('theme');

    if (saved) {
        document.body.className = saved;
    }

})();
