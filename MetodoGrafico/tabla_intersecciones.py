import re
import pandas as pd
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from django.utils.translation import gettext_lazy as _

def tabla_intersecciones(restricciones, incluir_pasos=False):
    """Genera una tabla didáctica con los interceptos de cada restricción.

    Parameters
    ----------
    restricciones : list[str]
        Restricciones como cadenas. Ejemplo: ['x1 <= 6', 'x2 <= 4']

    Returns
    -------
    pandas.DataFrame
        Con columnas 'restriccion', 'intercepto_x1', 'intercepto_x2' y 'puntos'.
    """
    if not isinstance(restricciones, list) or not all(isinstance(r, str) for r in restricciones):
        raise ValueError("Las restricciones deben proporcionarse como lista de cadenas")

    x1, x2 = sp.symbols("x1 x2")
    local_dict = {"x1": x1, "x2": x2}
    trans = standard_transformations + (implicit_multiplication_application,)

    datos = []
    pasos = []

    def _fmt_num(num):
        num = float(num)
        num_r = round(num, 2)
        return int(num_r) if num_r.is_integer() else f"{num_r:.2f}"

    for restr in restricciones:
        # Detectar operador (<=, >=, =, <, >)
        m = re.search(r"(<=|>=|=|<|>)", restr)
        if not m:
            raise ValueError(f"Operador no encontrado en la restricción: {restr}")

        operador = m.group(1)

        # Separar y convertir a expresiones sympy
        expr_izq, expr_der = map(
            lambda s: parse_expr(s, local_dict=local_dict, transformations=trans),
            restr.split(operador),
        )
        igualdad = sp.Eq(expr_izq, expr_der)

        # Interceptos
        sol_x1 = sp.solve(igualdad.subs(x2, 0), x1)
        x1_inter = float(sol_x1[0]) if sol_x1 else float("nan")

        sol_x2 = sp.solve(igualdad.subs(x1, 0), x2)
        x2_inter = float(sol_x2[0]) if sol_x2 else float("nan")

        # Formatear restricción con subíndices y símbolo ≤ / ≥
        restr_fmt = (
            restr.replace("x1", "x₁")
            .replace("x2", "x₂")
            .replace("<=", "≤")
            .replace(">=", "≥")
        )

        puntos = f"({_fmt_num(x1_inter)}, 0) {_('y')} (0, {_fmt_num(x2_inter)})"

        datos.append(
            {
                "restriccion": restr_fmt,
                "intercepto_x1": _fmt_num(x1_inter),
                "intercepto_x2": _fmt_num(x2_inter),
                "puntos": puntos,
            }
        )

        if incluir_pasos:
            def _fmt(num):
               return _fmt_num(num)

            a = expr_izq.coeff(x1)
            b = expr_izq.coeff(x2)
            c = expr_der

            op_fmt = operador.replace("<=", "≤").replace(">=", "≥")
            pasos.extend(
                [
                    {
                        "restriccion": restr_fmt,
                        "sustitucion": "x₂ = 0",
                        "ecuacion": f"{_fmt(a)}x₁ + {_fmt(b)}(0) = {_fmt(c)} → {_fmt(a)}x₁ = {_fmt(c)}",
                        "resultado": f"x₁ = {_fmt_num(x1_inter)}",
                        "punto": f"({_fmt_num(x1_inter)}, 0)",
                        "resumen": False,
                    },
                    {
                        "restriccion": "",
                        "sustitucion": "x₁ = 0",
                        "ecuacion": f"{_fmt(a)}(0) + {_fmt(b)}x₂ = {_fmt(c)} → {_fmt(b)}x₂ = {_fmt(c)}",
                        "resultado": f"x₂ = {_fmt_num(x2_inter)}",
                        "punto": f"(0, {_fmt_num(x2_inter)})",
                        "resumen": False,
                    },
                ]
            )

    df = pd.DataFrame(
        datos,
        columns=["restriccion", "intercepto_x1", "intercepto_x2", "puntos"],
    )
    df = df.reset_index(drop=True)
    return (df, pasos) if incluir_pasos else df


if __name__ == "__main__":
    restricciones = ["3 x1 + 5 x2 <= 6", "4 x1 + 2 x2 <= 5"]
    tabla, pasos = tabla_intersecciones(restricciones, incluir_pasos=True)
    print(pasos)
    print(tabla)
