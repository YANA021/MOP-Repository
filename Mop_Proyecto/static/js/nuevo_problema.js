document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navbar.classList.add('backdrop-blur', 'bg-white/70', 'shadow-sm');
        } else {
            navbar.classList.remove('backdrop-blur', 'bg-white/70', 'shadow-sm');
        }
    });

    const restricciones = [];
    const addBtn = document.getElementById('add-restriccion');
    addBtn.addEventListener('click', () => {
        const x1 = document.getElementById('rest-x1').value;
        const x2 = document.getElementById('rest-x2').value;
        const op = document.getElementById('rest-op').value;
        const val = document.getElementById('rest-val').value;
        if (x1 && x2 && val) {
            restricciones.push({ x1, x2, op, val });
            document.getElementById('rest-x1').value = '';
            document.getElementById('rest-x2').value = '';
            document.getElementById('rest-val').value = '';
        }
    });

    const form = document.getElementById('form');
    form.addEventListener('submit', () => {
        document.getElementById('restricciones-hidden').value = JSON.stringify(restricciones);
    });
});