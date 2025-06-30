document.addEventListener('DOMContentLoaded', () => {
    const restricciones = [];
    const lista = document.getElementById('lista-restricciones');
    const hidden = document.getElementById('restricciones-hidden');
    const agregarBtn = document.getElementById('agregar-restriccion');

    if (!lista || !hidden || !agregarBtn) return;

    // Renderiza la lista y actualiza el campo oculto
    function render() {
        lista.innerHTML = '';
        restricciones.forEach((r, i) => {
            const li = document.createElement('li');
            li.className =
                'flex justify-between items-center border rounded px-3 py-2 mb-2';
            li.innerHTML =
                `<span>${r.coef_x1}x₁ + ${r.coef_x2}x₂ ${r.operador} ${r.valor}</span>` +
                `<button type="button" class="text-red-600 remove" data-index="${i}">➖</button>`;
            lista.appendChild(li);
        });
        // Guardar la lista en el campo oculto como JSON
        hidden.value = JSON.stringify(restricciones);
    }

    // Agregar restricción
    agregarBtn.addEventListener('click', () => {
        const x1Input = document.getElementById('coef-x1');
        const x2Input = document.getElementById('coef-x2');
        const opInput = document.getElementById('operador');
        const valInput = document.getElementById('valor-restriccion');

        if (
            !x1Input.value.trim() ||
            !x2Input.value.trim() ||
            !opInput.value.trim() ||
            !valInput.value.trim()
        ) {
            alert('Por favor complete todos los campos de la restricción');
            return;
        }

        const coef_x1 = parseFloat(x1Input.value);
        const coef_x2 = parseFloat(x2Input.value);
        const operador = opInput.value;
        const valor = parseFloat(valInput.value);

        restricciones.push({ coef_x1, coef_x2, operador, valor });
        render();

        // Limpiar campos
        x1Input.value = '';
        x2Input.value = '';
        valInput.value = '';
    });

    // Eliminar restricción
    lista.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove')) {
            const index = parseInt(e.target.dataset.index, 10);
            if (!Number.isNaN(index) && index >= 0 && index < restricciones.length) {
                restricciones.splice(index, 1);
                render();
            }
        }
    });
});
