document.addEventListener('DOMContentLoaded', function () {

    const btn = document.getElementById('theme-toggle');

    if (!btn) {
        console.warn('Theme toggle button not found');
        return;
    }

    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');


    function setTheme(mode) {

        if (mode === 'dark') {

            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');

            // Update icon kalau ada
            if (darkIcon && lightIcon) {
                darkIcon.classList.add('hidden');
                lightIcon.classList.remove('hidden');
            }

        } else {

            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');

            if (darkIcon && lightIcon) {
                lightIcon.classList.add('hidden');
                darkIcon.classList.remove('hidden');
            }
        }
    }


    // INIT
    const savedTheme = localStorage.getItem('color-theme');

    setTheme(savedTheme === 'dark' ? 'dark' : 'light');


    // CLICK
    btn.addEventListener('click', function (e) {

        e.preventDefault();
        e.stopPropagation();

        console.log('Theme toggle clicked');

        const isDark =
            document.documentElement.classList.contains('dark');

        setTheme(isDark ? 'light' : 'dark');
    });

});
