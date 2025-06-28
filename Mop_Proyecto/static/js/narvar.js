document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const toggle = document.getElementById('theme-toggle');
    const circle = toggle.querySelector('span');
    const label = document.getElementById('theme-label');

    function toggleTheme() {
        const dark = html.classList.toggle('dark');
        if (dark) {
            toggle.classList.add('bg-[#4FD1C5]');
            circle.classList.add('translate-x-5');
            label.textContent = 'Modo oscuro';
            toggle.setAttribute('aria-pressed', 'true');
        } else {
            toggle.classList.remove('bg-[#4FD1C5]');
            circle.classList.remove('translate-x-5');
            label.textContent = 'Modo claro';
            toggle.setAttribute('aria-pressed', 'false');
        }
    }

    toggle.addEventListener('click', toggleTheme);
    toggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleTheme();
        }
    });

    const langBtn = document.getElementById('lang-btn');
    const langMenu = document.getElementById('lang-menu');

    function toggleLangMenu() {
        const expanded = langMenu.classList.toggle('hidden');
        langBtn.setAttribute('aria-expanded', String(!expanded));
    }

    langBtn.addEventListener('click', toggleLangMenu);
    langBtn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleLangMenu();
        }
    });

    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    function toggleMobileMenu() {
        const expanded = mobileMenu.classList.toggle('hidden');
        menuBtn.setAttribute('aria-expanded', String(!expanded));
    }

    menuBtn.addEventListener('click', toggleMobileMenu);
    menuBtn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleMobileMenu();
        }
    });
});