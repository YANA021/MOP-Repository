"""Herramientas para resolver sistemas lineales de dos ecuaciones."""

from typing import List, Dict, Tuple
import re
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
import plotly.graph_objects as go


def _parse_ecuacion(ecuacion: str, x1, x2) -> sp.Eq:
    """Convierte una cadena como '3 x1 + 5 x2 = 6' en una ecuación sympy."""
    if '=' not in ecuacion:
        raise ValueError("La ecuación debe contener '='")
    izq, der = ecuacion.split('=')
    trans = standard_transformations + (implicit_multiplication_application,)
    local = {'x1': x1, 'x2': x2}
    expr_izq = parse_expr(izq, local_dict=local, transformations=trans)
    expr_der = parse_expr(der, local_dict=local, transformations=trans)
    return sp.Eq(expr_izq, expr_der)


def _coeficientes(eq: sp.Eq, x1, x2) -> Tuple[float, float, float]:
    expr = sp.expand(eq.lhs - eq.rhs)
    a = expr.coeff(x1)
    b = expr.coeff(x2)
    c = -expr.subs({x1: 0, x2: 0})
    return float(a), float(b), float(c)


def _fmt(num: float) -> str:
    n = round(float(num), 4)
    return str(int(n)) if n.is_integer() else f"{n:.4f}"


def _graficar(a1, b1, c1, a2, b2, c2, solucion) -> str:
    x = np.linspace(-10, 10, 400)
    fig = go.Figure()

    if b1 != 0:
        y1 = (c1 - a1 * x) / b1
        fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', name='Ecuación 1'))
    else:
        x_line = np.full_like(x, c1 / a1)
        fig.add_trace(go.Scatter(x=x_line, y=x, mode='lines', name='Ecuación 1'))

    if b2 != 0:
        y2 = (c2 - a2 * x) / b2
        fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', name='Ecuación 2'))
    else:
        x_line = np.full_like(x, c2 / a2)
        fig.add_trace(go.Scatter(x=x_line, y=x, mode='lines', name='Ecuación 2'))

    if solucion is not None:
        fig.add_trace(
            go.Scatter(
                x=[solucion[0]],
                y=[solucion[1]],
                mode='markers+text',
                text=['Solución'],
                textposition='top center',
                marker=dict(size=10, color='red'),
                name='Solución',
            )
        )

    fig.update_layout(
        xaxis_title='x₁',
        yaxis_title='x₂',
        plot_bgcolor='white',
        height=500,
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displaylogo': False, 'responsive': True})


def _combinar_grafica_y_pasos(grafica: str, pasos: List[str]) -> str:
    """Concatena la gráfica generada por Plotly con el procedimiento en HTML."""
    pasos_html = (
        "<pre style='white-space: pre-wrap; margin-top:1em;'>" + "\n".join(pasos) + "</pre>"
    )
    return grafica + pasos_html


def resolver_sistema_pasos(eq1_str: str, eq2_str: str, metodo: str = 'eliminacion') -> Dict[str, object]:
    """Resuelve un sistema 2x2 y devuelve pasos y gráfica.

    El diccionario resultante incluye un campo ``html`` con la gráfica
    seguida del procedimiento formateado, de modo que el proceso aparezca
    debajo de la imagen al mostrarse.
    """
    x1, x2 = sp.symbols('x1 x2')
    eq1 = _parse_ecuacion(eq1_str, x1, x2)
    eq2 = _parse_ecuacion(eq2_str, x1, x2)

    a1, b1, c1 = _coeficientes(eq1, x1, x2)
    a2, b2, c2 = _coeficientes(eq2, x1, x2)

    pasos: List[str] = []
    pasos.append('Sistema:')
    pasos.append(f"Ecuación 1: {_fmt(a1)}x₁ + {_fmt(b1)}x₂ = {_fmt(c1)}")
    pasos.append(f"Ecuación 2: {_fmt(a2)}x₁ + {_fmt(b2)}x₂ = {_fmt(c2)}")

    if metodo == 'sustitucion':
        pasos.append('Método: Sustitución')
        if abs(b1) > 0:
            expr = sp.solve(eq1, x2)[0]
            pasos.append(f"Paso 1: Despejamos x₂ de E1 → x₂ = {sp.simplify(expr)}")
            pasos.append('Paso 2: Sustituimos en E2')
            val_x1 = sp.solve(eq2.subs(x2, expr), x1)[0]
        else:
            expr = sp.solve(eq1, x1)[0]
            pasos.append(f"Paso 1: Despejamos x₁ de E1 → x₁ = {sp.simplify(expr)}")
            pasos.append('Paso 2: Sustituimos en E2')
            val_x1 = sp.solve(eq2.subs(x1, expr), x1)[0]
        pasos.append(f"Paso 3: x₁ = {_fmt(val_x1)}")
        val_x2 = sp.solve(eq1.subs(x1, val_x1), x2)[0]
        pasos.append(f"Paso 4: Sustituimos x₁ en E1 → x₂ = {_fmt(val_x2)}")
    else:
        pasos.append('Método: Eliminación')
        pasos.append(
            f"Paso 1: Multiplicamos E1 por {_fmt(b2)} → {_fmt(a1*b2)}x₁ + {_fmt(b1*b2)}x₂ = {_fmt(c1*b2)}"
        )
        pasos.append(
            f"Paso 2: Multiplicamos E2 por {_fmt(b1)} → {_fmt(a2*b1)}x₁ + {_fmt(b2*b1)}x₂ = {_fmt(c2*b1)}"
        )
        coef = a2*b1 - a1*b2
        const = c2*b1 - c1*b2
        pasos.append(
            f"Paso 3: Restamos E2 - E1 → ({_fmt(a2*b1)}x₁ - {_fmt(a1*b2)}x₁) = {_fmt(const)} → {_fmt(coef)}x₁ = {_fmt(const)}"
        )
        val_x1 = const / coef
        pasos.append(f"Paso 4: x₁ = {_fmt(val_x1)}")
        val_x2 = sp.solve(eq1.subs(x1, val_x1), x2)[0]
        pasos.append(f"Paso 5: Sustituimos x₁ = {_fmt(val_x1)} en E1 → x₂ = {_fmt(val_x2)}")

    pasos.append('')
    pasos.append('Resultado:')
    pasos.append(f"x₁ = {_fmt(val_x1)}")
    pasos.append(f"x₂ = {_fmt(val_x2)}")
    pasos.append(f"Punto de intersección: ({_fmt(val_x1)}, {_fmt(val_x2)})")

    grafica = _graficar(a1, b1, c1, a2, b2, c2, (float(val_x1), float(val_x2)))

    html = _combinar_grafica_y_pasos(grafica, pasos)

    return {
        'pasos': pasos,
        'resultado': {'x1': float(val_x1), 'x2': float(val_x2)},
        'grafica': grafica,
        'html': html,
    }

def pasos_vertices(restricciones: List[str], metodo: str = 'eliminacion') -> List[Dict[str, object]]:

    pares = []
    for i in range(len(restricciones)):
        for j in range(i + 1, len(restricciones)):
            eq1 = re.sub(r'(<=|>=|<|>)', '=', restricciones[i])
            eq2 = re.sub(r'(<=|>=|<|>)', '=', restricciones[j])
            try:
                res = resolver_sistema_pasos(eq1, eq2, metodo=metodo)
                pares.append({
                    'restriccion1': restricciones[i],
                    'restriccion2': restricciones[j],
                    'latex1': restriccion_a_latex(restricciones[i]),    #llama y reemplaza caracteres
                    'latex2': restriccion_a_latex(restricciones[j]),
                    'pasos': res['pasos'],
                    'punto': res['resultado'],
                })
            except Exception:
                continue

    return pares

# funcion para reemplazar signos y pueda ser convertido a latex en la template
def restriccion_a_latex(expr: str) -> str:
    expr = expr.replace('<=', r'\leq')
    expr = expr.replace('>=', r'\geq')
    expr = expr.replace('<', r'<')
    expr = expr.replace('>', r'>')
    expr = expr.replace('=', r'=')
    expr = re.sub(r'\b([xX])(\d+)', r'x_{\2}', expr)    #reemplaza x1,x2 a x_{1},x_{2}
    return expr


if __name__ == '__main__':
    res = resolver_sistema_pasos('3 x1 + 5 x2 = 6', '4 x1 + 2 x2 = 5')
    for p in res['pasos']:
        print(p)

    print('\nGuardando gráfica con pasos en "salida.html"...')
    with open('salida.html', 'w', encoding='utf-8') as f:
        f.write(res['html'])
    print('Archivo generado: salida.html')