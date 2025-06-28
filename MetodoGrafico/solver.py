import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog

def resolver_problema_lineal(objetivo, coef_x1, coef_x2, restricciones, limites=None):
   
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
    
    if x1_min is not None:
        restr.append((1, 0, ">=", x1_min))
    if x1_max is not None:
        restr.append((1, 0, "<=", x1_max))
    if x2_min is not None:
        restr.append((0, 1, ">=", x2_min))
    if x2_max is not None:
        restr.append((0, 1, "<=", x2_max))
    
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
        return {
            'status': 'inviable',
            'grafica': crear_grafica_vacia()
        }
    
    # Calcular valores en los vértices
    valores = [coef_x1*x + coef_x2*y for x, y in vertices_factibles]
    opt_val = min(valores) if objetivo == "min" else max(valores)
    soluciones = [v for v, z in zip(vertices_factibles, valores) if abs(z - opt_val) < 1e-6]
    
    # Determinar el estado del problema
    if resultado and resultado.status == 3:
        estado = "no acotada"
        soluciones = []
        opt_val = float('nan')
    elif len(soluciones) > 1:
        estado = "multiple"
    else:
        estado = "optimo"
    
    # Crear gráfica
    fig = crear_grafica(restr, vertices_factibles, soluciones, coef_x1, coef_x2, opt_val)
    
    return {
        'status': estado,
        'x': soluciones[0][0] if soluciones else float('nan'),
        'y': soluciones[0][1] if soluciones else float('nan'),
        'z': opt_val,
        'vertices': [{'x': x, 'y': y, 'z': coef_x1*x + coef_x2*y} for x, y in vertices_factibles],
        'grafica': fig.to_html(full_html=False, include_plotlyjs='cdn')
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

def crear_grafica(restricciones, vertices, soluciones, coef_x1, coef_x2, opt_val):
    """Crea la gráfica del problema."""
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
    for a, b, op, c in restricciones:
        if b == 0:  # Recta vertical
            x_line = np.full_like(x, c/a)
            y_line = np.linspace(y_min, y_max, 100)
        else:
            x_line = x
            y_line = (c - a*x) / b
        
        fig.add_trace(go.Scatter(
            x=x_line, y=y_line, mode='lines', 
            name=f"{a}x₁ + {b}x₂ {op} {c}"
        ))
    
    # Dibujar región factible (convex hull de los vértices)
    if vertices:
        # Ordenar vértices en sentido horario para el polígono
        centro = np.mean(vertices, axis=0)
        angulos = [np.arctan2(y-centro[1], x-centro[0]) for x, y in vertices]
        vertices_ordenados = [v for _, v in sorted(zip(angulos, vertices))]
        
        xs = [v[0] for v in vertices_ordenados] + [vertices_ordenados[0][0]]
        ys = [v[1] for v in vertices_ordenados] + [vertices_ordenados[0][1]]
        
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill='toself', 
            fillcolor='rgba(0,100,80,0.2)', 
            name='Región factible'
        ))
    
    # Dibujar solución óptima
    if soluciones:
        x_opt, y_opt = soluciones[0]
        fig.add_trace(go.Scatter(
            x=[x_opt], y=[y_opt], mode='markers',
            marker=dict(size=10, color='red'),
            name=f'Solución óptima ({x_opt:.1f}, {y_opt:.1f})'
        ))
    
    # Dibujar función objetivo
    if not np.isnan(opt_val) and coef_x2 != 0:
        y_obj = (opt_val - coef_x1*x) / coef_x2
        fig.add_trace(go.Scatter(
            x=x, y=y_obj, mode='lines', 
            line=dict(dash='dash'),
            name=f'Función objetivo (Z={opt_val:.1f})'
        ))
    
    # Configurar el gráfico
    fig.update_layout(
        xaxis=dict(title='x₁', range=[x_min, x_max]),
        yaxis=dict(title='x₂', range=[y_min, y_max]),
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
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

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