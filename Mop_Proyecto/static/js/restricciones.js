document.addEventListener('DOMContentLoaded', () => {
    const restricciones = [];
    const lista = document.getElementById('lista-restricciones');
    const hidden = document.getElementById('restricciones-hidden');

    function render() {
        lista.innerHTML = '';
        restricciones.forEach((r, i) => {
            const li = document.createElement('li');
            li.className = 'flex justify-between items-center border rounded px-3 py-2';
            li.innerHTML = `<span>${r.x1}x₁ + ${r.x2}x₂ ${r.op} ${r.val}</span>` +
                `<button type="button" class="text-red-600 remove" data-index="${i}">➖</button>`;
            lista.appendChild(li);
        });
        hidden.value = JSON.stringify(restricciones);
    }

    document.getElementById('agregar-restriccion').addEventListener('click', () => {
        const x1 = parseFloat(document.getElementById('coef-x1').value) || 0;
        const x2 = parseFloat(document.getElementById('coef-x2').value) || 0;
        const op = document.getElementById('operador').value;
        const val = parseFloat(document.getElementById('valor-restriccion').value) || 0;
        restricciones.push({ x1, x2, op, val });
        render();
    });

    lista.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove')) {
            const index = parseInt(e.target.getAttribute('data-index'), 10);
            restricciones.splice(index, 1);
            render();
        }
    });
});