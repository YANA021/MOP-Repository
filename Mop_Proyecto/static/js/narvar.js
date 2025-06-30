document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const toggle = document.getElementById('theme-toggle');
    const sun = document.getElementById('sun-icon');
    const moon = document.getElementById('moon-icon');

    if (!toggle || !sun || !moon) return;

    const storedTheme = localStorage.getItem('theme');
      if (storedTheme === 'dark') {
        html.classList.add('dark');
        sun.classList.add('hidden');
        moon.classList.remove('hidden');
    }

    function toggleTheme() {
        const dark = html.classList.toggle('dark');
        sun.classList.toggle('hidden', dark);
        moon.classList.toggle('hidden', !dark);
        localStorage.setItem('theme', dark ? 'dark' : 'light');
    }

    if (toggle) {
        toggle.addEventListener('click', toggleTheme);
        toggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleTheme();
            }
        });
    }

    const langBtn = document.getElementById('lang-btn');
    const langMenu = document.getElementById('lang-menu');

if (langBtn && langMenu) {
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
    }

    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

if (menuBtn && mobileMenu) {
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
    }
});