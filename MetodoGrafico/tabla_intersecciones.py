import re
import pandas as pd
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)


def tabla_intersecciones(restricciones):
    """Genera una tabla con los interceptos de cada restricción.

    Parameters
    ----------
    restricciones : list of str
        Restricciones como cadenas. Ejemplo: ['x1 <= 6', 'x2 <= 4']

    Returns
    -------
    pandas.DataFrame
        Con columnas 'restriccion', 'x1_intercepto' y 'x2_intercepto'.
    """
    if not isinstance(restricciones, list) or not all(isinstance(r, str) for r in restricciones):
        raise ValueError("Las restricciones deben proporcionarse como lista de cadenas")

    x1, x2 = sp.symbols("x1 x2")
    local_dict = {"x1": x1, "x2": x2}
    trans = standard_transformations + (implicit_multiplication_application,)

    datos = []
    for restr in restricciones:
        m = re.search(r"(<=|>=|=|<|>)", restr)
        if not m:
            raise ValueError(f"Operador no encontrado en la restricción: {restr}")
        op = m.group(1)
        lado_izq, lado_der = [s.strip() for s in restr.split(op, 1)]
        expr_izq = parse_expr(lado_izq, transformations=trans, local_dict=local_dict)
        expr_der = parse_expr(lado_der, transformations=trans, local_dict=local_dict)

        if not (expr_izq - expr_der).free_symbols.issubset({x1, x2}):
            raise ValueError("Solo se permiten las variables x1 y x2")

        igualdad = sp.Eq(expr_izq, expr_der)

        sol_x1 = sp.solve(igualdad.subs(x2, 0), x1)
        x1_inter = float(sol_x1[0]) if sol_x1 else float("nan")

        sol_x2 = sp.solve(igualdad.subs(x1, 0), x2)
        x2_inter = float(sol_x2[0]) if sol_x2 else float("nan")

        datos.append({
            "restriccion": restr,
            "x1_intercepto": x1_inter,
            "x2_intercepto": x2_inter,
        })

    return pd.DataFrame(datos)


if __name__ == "__main__":
    ejemplo = [
        "x1 <= 6",
        "x2 <= 4",
        "6 x1 + 8 x2 <= 48",
    ]
    tabla = tabla_intersecciones(ejemplo)
    print(tabla)