document.addEventListener('DOMContentLoaded', () => {
    const restricciones = [];
    const lista = document.getElementById('lista-restricciones');
    const hidden = document.getElementById('restricciones-hidden');
    const agregarBtn = document.getElementById('agregar-restriccion');

    if (!lista || !hidden || !agregarBtn) return;

    function render() {
        lista.innerHTML = '';
        restricciones.forEach((r, i) => {
            const li = document.createElement('li');
            li.className = 'flex justify-between items-center border rounded px-3 py-2 mb-2';
            li.innerHTML = `<span>${r.x1}x₁ + ${r.x2}x₂ ${r.op} ${r.val}</span>` +
                `<button type="button" class="text-red-600 remove" data-index="${i}">➖</button>`;
            lista.appendChild(li);
        });
        hidden.value = JSON.stringify(restricciones);
    }

    agregarBtn.addEventListener('click', () => {
        const x1Input = document.getElementById('coef-x1');
        const x2Input = document.getElementById('coef-x2');
        const opInput = document.getElementById('operador');
        const valInput = document.getElementById('valor-restriccion');
        
        if (!x1Input.value || !x2Input.value || !opInput.value || !valInput.value) {
            alert('Por favor complete todos los campos de la restricción');
            return;
        }
        
        const x1 = parseFloat(x1Input.value);
        const x2 = parseFloat(x2Input.value);
        const op = opInput.value;
        const val = parseFloat(valInput.value);
        
        restricciones.push({ x1, x2, op, val });
        render();
        
        // Clear inputs
        x1Input.value = '';
        x2Input.value = '';
        valInput.value = '';
    });

    lista.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove')) {
            const index = parseInt(e.target.getAttribute('data-index'), 10);
            if (!isNaN(index) && index >= 0 && index < restricciones.length) {
                restricciones.splice(index, 1);
                render();
            }
        }
    });
});