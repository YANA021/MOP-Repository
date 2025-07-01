import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog
from django.utils.translation import gettext_lazy as _

def validar_datos(objetivo, coef_x1, coef_x2, restricciones, limites=None):
   

    if objetivo not in ("max", "min"):
        raise ValueError("Objetivo debe ser 'max' o 'min'.")

    try:
        coef_x1 = float(coef_x1)
        coef_x2 = float(coef_x2)
    except (TypeError, ValueError) as exc:
        raise ValueError("Coeficientes de la función objetivo inválidos") from exc

    if not isinstance(restricciones, list):
        raise ValueError("Las restricciones deben ser una lista")

    lista = []
    for r in restricciones:
        try:
            a = float(r["coef_x1"])
            b = float(r["coef_x2"])
            c = float(r["valor"])
            op = r["operador"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Restricción inválida") from exc
        if op not in ("<=", ">=", "="):
            raise ValueError("Operador no soportado")
        lista.append({"coef_x1": a, "coef_x2": b, "operador": op, "valor": c})

    limites = limites or {}
    limites_limpios = {}
    for k in ("x1_min", "x1_max", "x2_min", "x2_max"):
        v = limites.get(k)
        if v is not None:
            try:
                limites_limpios[k] = float(v)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Límite {k} inválido") from exc

    return coef_x1, coef_x2, lista, limites_limpios


def resolver_problema_lineal(objetivo, coef_x1, coef_x2, restricciones, limites=None):
    """Resuelve un problema lineal de dos variables mediante el método gráfico."""

    coef_x1, coef_x2, restricciones, limites = validar_datos(
        objetivo, coef_x1, coef_x2, restricciones, limites
    )
   
    # Procesar restricciones
    restr = []
    for r in restricciones:
        a = float(r['coef_x1'])
        b = float(r['coef_x2'])
        op = r['operador']
        c = float(r['valor'])
        restr.append((a, b, op, c))
    
    # Añadir límites como restricciones
    if limites is None:
        limites = {}
    
    x1_min = limites.get('x1_min', 0)
    x1_max = limites.get('x1_max')
    x2_min = limites.get('x2_min', 0)
    x2_max = limites.get('x2_max')
    
    limit_indices = []
    if x1_min is not None:
        restr.append((1, 0, ">=", x1_min))
        limit_indices.append(len(restr) - 1)
    if x1_max is not None:
        restr.append((1, 0, "<=", x1_max))
        limit_indices.append(len(restr) - 1)
    if x2_min is not None:
        restr.append((0, 1, ">=", x2_min))
        limit_indices.append(len(restr) - 1)
    if x2_max is not None:
        restr.append((0, 1, "<=", x2_max))
        limit_indices.append(len(restr) - 1)
    
    # Preparar datos para linprog
    A_ub = []
    b_ub = []
    
    for a, b, op, c in restr:
        if op == "<=":
            A_ub.append([a, b])
            b_ub.append(c)
        elif op == ">=":
            A_ub.append([-a, -b])
            b_ub.append(-c)
        elif op == "=":
            A_ub.append([a, b])
            b_ub.append(c)
            A_ub.append([-a, -b])
            b_ub.append(-c)
    
    # Resolver con linprog
    c_vec = [coef_x1, coef_x2] if objetivo == "min" else [-coef_x1, -coef_x2]
    bounds = [(x1_min, x1_max), (x2_min, x2_max)]
    
    try:
        resultado = linprog(c_vec, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    except:
        resultado = None
    
    # Encontrar vértices factibles
    vertices = encontrar_vertices(restr)
    vertices_factibles = [v for v in vertices if cumple_restricciones(v, restr)]
    
    if not vertices_factibles:
        fig = crear_grafica_vacia()
        return {
            'status': 'inviable',
            'grafica': fig.to_html(
                full_html=False,
                include_plotlyjs='cdn',
                config={'displaylogo': False, 'responsive': True}
            ),
            'fig': fig,
            
        }
    
    # Calcular valores en los vértices
    valores = [coef_x1*x + coef_x2*y for x, y in vertices_factibles]
    opt_val = min(valores) if objetivo == "min" else max(valores)
    soluciones = [v for v, z in zip(vertices_factibles, valores) if abs(z - opt_val) < 1e-6]
    
    # Determinar el estado del problema
    if resultado and resultado.status == 3:
        estado = str(_("No acotada"))
        soluciones = []
        opt_val = float('nan')
    elif len(soluciones) > 1:
        estado = str(_("Múltiple"))
    else:
        estado = str(_("Óptimo"))
    
    # Crear gráfica
    fig = crear_grafica(
        restr, vertices_factibles, soluciones,
        coef_x1, coef_x2, opt_val, limit_indices
    )
    
    return {
        'status': estado,
        'x': soluciones[0][0] if soluciones else float('nan'),
        'y': soluciones[0][1] if soluciones else float('nan'),
        'z': opt_val,
         'soluciones': [{'x': x, 'y': y} for x, y in soluciones],
        'vertices': [{'x': x, 'y': y, 'z': coef_x1*x + coef_x2*y} for x, y in vertices_factibles],
        'grafica': fig.to_html(
            full_html=False,
            include_plotlyjs='cdn',
            config={'displaylogo': False, 'responsive': True}
        ),
        'fig': fig,
    }

def encontrar_vertices(restricciones):
    """Encuentra posibles vértices intersectando las restricciones."""
    vertices = []
    n = len(restricciones)
    
    # Intersecciones entre restricciones
    for i in range(n):
        for j in range(i+1, n):
            a1, b1, _, c1 = restricciones[i]
            a2, b2, _, c2 = restricciones[j]
            
            # Resolver sistema de ecuaciones
            A = np.array([[a1, b1], [a2, b2]])
            if np.linalg.det(A) == 0:
                continue  # Rectas paralelas
            
            x, y = np.linalg.solve(A, [c1, c2])
            vertices.append((x, y))
    
    # Intersecciones con ejes
    for a, b, _, c in restricciones:
        if a != 0:
            vertices.append((c/a, 0))
        if b != 0:
            vertices.append((0, c/b))
    
    # Origen
    vertices.append((0, 0))
    
    # Eliminar duplicados
    vertices_unicos = []
    for v in vertices:
        if not any(np.allclose(v, u) for u in vertices_unicos):
            vertices_unicos.append(v)
    
    return vertices_unicos

def cumple_restricciones(punto, restricciones):
    """Verifica si un punto cumple todas las restricciones."""
    x, y = punto
    for a, b, op, c in restricciones:
        valor = a*x + b*y
        if op == "<=" and valor > c + 1e-7:
            return False
        if op == ">=" and valor < c - 1e-7:
            return False
        if op == "=" and abs(valor - c) > 1e-7:
            return False
    return True

def crear_grafica(restricciones, vertices, soluciones, coef_x1, coef_x2, opt_val, limit_indices=None):
    """Crea la gráfica del problema."""
    if limit_indices is None:
        limit_indices = []
    fig = go.Figure()
    
    # Determinar límites del gráfico
    if vertices:
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        x_min, x_max = min(xs)-1, max(xs)+1
        y_min, y_max = min(ys)-1, max(ys)+1
    else:
        x_min, x_max = -5, 5
        y_min, y_max = -5, 5
    
    # Dibujar restricciones
    x = np.linspace(x_min, x_max, 100)
    for idx, (a, b, op, c) in enumerate(restricciones):
        if b == 0:  # Recta vertical
            x_line = np.full_like(x, c/a)
            y_line = np.linspace(y_min, y_max, 100)
        else:
            x_line = x
            y_line = (c - a*x) / b
        
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=f"{a}x₁ + {b}x₂ {op} {c}",
                showlegend=False if idx in limit_indices else True
            )
        )
    
    # Dibujar región factible (convex hull de los vértices)
    if vertices:
        # Ordenar vértices en sentido horario para el polígono
        centro = np.mean(vertices, axis=0)
        angulos = [np.arctan2(y-centro[1], x-centro[0]) for x, y in vertices]
        vertices_ordenados = [v for _, v in sorted(zip(angulos, vertices))]
        
        xs = [v[0] for v in vertices_ordenados] + [vertices_ordenados[0][0]]
        ys = [v[1] for v in vertices_ordenados] + [vertices_ordenados[0][1]]
        
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                fill='toself',
                fillcolor='rgba(0,100,80,0.2)',
                name= str(_('Región factible'))
            )
        )

         # Marcadores de los vértices factibles
        fig.add_trace(
            go.Scatter(
                x=[v[0] for v in vertices],
                y=[v[1] for v in vertices],
                mode='markers+text',
                text=[f"P{i+1}" for i in range(len(vertices))],
                textposition="top center",
                marker=dict(size=6, color='blue'),
                name= str(_('Vértices'))
            )
        )
    
    # Dibujar solución óptima
    if soluciones:
             xs = [s[0] for s in soluciones]
    ys = [s[1] for s in soluciones]
    etiqueta_optimo = str(_('Óptimo'))
    nombre = str(_('Solución óptima'))
    if len(soluciones) > 1:
            nombre += f" ({str(_('múltiples'))})"
    fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode='markers+text',
                text=[etiqueta_optimo] * len(xs),
                textposition='top center',
                marker=dict(size=10, color='red'),
                name=nombre,
            )
        )
                 
    # Dibujar función objetivo
    if not np.isnan(opt_val) and coef_x2 != 0:
        y_obj = (opt_val - coef_x1*x) / coef_x2
        fig.add_trace(go.Scatter(
            x=x, y=y_obj, mode='lines',
            line=dict(dash='dash'),
            name = f"{str(_('Función objetivo'))} (Z={opt_val:.1f})"
        ))

        # Ejes x1 y x2
    fig.add_shape(type='line', x0=x_min, y0=0, x1=x_max, y1=0,
                  line=dict(color='black', width=2))
    fig.add_shape(type='line', x0=0, y0=y_min, x1=0, y1=y_max,
                  line=dict(color='black', width=2))
    
    # Configurar el gráfico
    fig.update_layout(
        xaxis=dict(title='x₁', range=[x_min, x_max], showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title='x₂', range=[y_min, y_max], showgrid=True, gridcolor='lightgray'),
        plot_bgcolor='white',
        height=600
    )
    
    
    return fig

def crear_grafica_vacia():
    """Crea una gráfica vacía para problemas inviables."""
    fig = go.Figure()
    fig.update_layout(
        xaxis=dict(title='x₁'),
        yaxis=dict(title='x₂'),
        plot_bgcolor='white',
        height=600,
        annotations=[dict(
          x=0.5, y=0.5, text='PROBLEMA INVIABLE',
          showarrow=False, font=dict(size=20)
)]
    )
    return fig

if __name__ == "__main__":
    # Ejemplo de uso
    objetivo = "max"
    coef_x1 = 3
    coef_x2 = 2
    restricciones = [
        {"coef_x1": 2, "coef_x2": 1, "operador": "<=", "valor": 18},
        {"coef_x1": 2, "coef_x2": 3, "operador": "<=", "valor": 42},
        {"coef_x1": 3, "coef_x2": 1, "operador": "<=", "valor": 24},
    ]

    resultado = resolver_problema_lineal(objetivo, coef_x1, coef_x2, restricciones)
    print("Estado:", resultado["status"])
    print("x1:", resultado["x"])
    print("x2:", resultado["y"])
    print("z:", resultado["z"])

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(resultado["grafica"])
    print("Graph saved to output.html")