import json
<<<<<<< HEAD
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
=======
import numpy as np

from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # noqa: F401
>>>>>>> origin/main

from .form import ProblemaPLForm
from .models import ProblemaPL, HistoryEntry
from .solver import resolver_problema_lineal

def to_native(obj):
   
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    return obj


def _convert_structure(data):
    
    if isinstance(data, dict):
        return {k: _convert_structure(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_convert_structure(v) for v in data]
    return to_native(data)

def home(request):
    """Renderiza la página de inicio."""
    return render(request, "home.html")


def metodo_grafico(request):
    """
    Muestra el formulario, resuelve el problema con el método gráfico,
    guarda el ProblemaPL (esto si está autenticado) y registra la entrada en HistoryEntry.
    """
    mensaje = ""

    # ------------------------------------------------------------------
    # 1) PETICIÓN POST: procesar formulario
    # ------------------------------------------------------------------
    if request.method == "POST":
        form = ProblemaPLForm(request.POST)
        vertices = []

        if form.is_valid():
<<<<<<< HEAD
            # Guardar el problema PL si el usuario está autenticado
=======
            # 1.1  Convertir 'restricciones' (texto JSON) en lista de Python
            restr_raw = form.cleaned_data.get("restricciones", "[]")
            if isinstance(restr_raw, str):
                try:
                    restricciones = json.loads(restr_raw)
                except json.JSONDecodeError:
                    restricciones = []
            else:
                restricciones = restr_raw

            # 1.2  Guardar problema en la BD si el usuario está autenticado
>>>>>>> origin/main
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data["objetivo"],
                    coef_x1=form.cleaned_data["coef_x1"],
                    coef_x2=form.cleaned_data["coef_x2"],
                    restricciones=restricciones,
                )
                mensaje = "Problema guardado correctamente."

<<<<<<< HEAD
            else:  
                mensaje = "Inicia sesión para guardar el problema en tu historial."

            # Preparamos límites si los hay
=======
            # 1.3  Preparar límites opcionales
>>>>>>> origin/main
            limites = {
                "x1_min": form.cleaned_data.get("x1_min"),
                "x1_max": form.cleaned_data.get("x1_max"),
                "x2_min": form.cleaned_data.get("x2_min"),
                "x2_max": form.cleaned_data.get("x2_max"),
            }

<<<<<<< HEAD
            # Resolver el problema
            salida = resolver_problema_lineal(
=======
            # 1.4  Resolver con el método gráfico
            resultado = resolver_problema_lineal(
>>>>>>> origin/main
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                restricciones,
                limites=limites,
            )

<<<<<<< HEAD
            # La función devuelve un dict con clave 'grafica' y el resto de resultados
            grafico = salida.get("grafica", "")
            # Extraemos sólo los valores de resultado
            resultado = {k: v for k, v in salida.items() if k != "grafica"}

            # Si hay usuario, creamos un registro de historial
            if request.user.is_authenticated and grafico:
                # Construimos descripción del problema
                desc = (
                    f"Objetivo: {dict(form.OBJETIVO_CHOICES)[form.cleaned_data['objetivo']]}; "
                    f"Z = {form.cleaned_data['coef_x1']}x1 + {form.cleaned_data['coef_x2']}x2; "
                    f"Restricciones: {json.dumps(form.cleaned_data['restricciones'])}"
                )
                # Convertimos resultados a string
                res_str = "; ".join(f"{k} = {v}" for k, v in resultado.items())

                # Ajustamos la ruta relativa de la imagen en MEDIA_ROOT
                # Supongamos que 'grafica' es algo como '/media/graphs/foo.png' o 'graphs/foo.png'
                img_rel = grafico
                if grafico.startswith(settings.MEDIA_URL):
                    img_rel = grafico[len(settings.MEDIA_URL):]
                img_rel = img_rel.lstrip("/")

                HistoryEntry.objects.create(
                    user=request.user,
                    problem_description=desc,
                    result=res_str,
                    graph_image=img_rel,
                )

            # Preparamos datos para la plantilla de resultado
            post_data = request.POST.dict()
            restricciones_data = form.cleaned_data.get("restricciones", [])
            form = ProblemaPLForm()  # Limpia el formulario para nueva inserción
=======
            # 1.5  Separar la gráfica del resto del resultado
            grafico = resultado.pop("grafica", "")
>>>>>>> origin/main

            opt_val = resultado.get("z")
            for idx, v in enumerate(resultado.get("vertices", []), start=1):
                vert = {
                    "punto": f"P{idx}",
                    "x1": v["x"],
                    "x2": v["y"],
                    "z": v["z"],
                    "optimo": abs(v["z"] - opt_val) < 1e-6,
                }
        vertices.append({_k: to_native(_v) for _k, _v in vert.items()})

        objetivo_text = (
                f"Z = {form.cleaned_data['coef_x1']}x₁ + {form.cleaned_data['coef_x2']}x₂"
            )
        restricciones_fmt = [
                f"{r['coef_x1']}x₁ + {r['coef_x2']}x₂ {r['operador']} {r['valor']}"
                for r in restricciones
            ]

            # 1.6  Preparar contexto para la plantilla de resultados
        context = {
                "form": ProblemaPLForm(),  # formulario limpio para nuevos datos
                "mensaje": mensaje,
                "resultado": resultado,
                "grafico": grafico,
                "objetivo": objetivo_text,
                "restricciones": restricciones_fmt,
                "vertices": vertices,
            }
<<<<<<< HEAD
            return render(request, "resultado.html", context)

    else:
        form = ProblemaPLForm()

    return render(request, "nuevo_problema.html", {"form": form, "mensaje": mensaje})


@login_required
def historial_problemas(request):
    """Muestra el historial de problemas del usuario con filtros opcionales."""
    qs = ProblemaPL.objects.filter(user=request.user)
    todos = ProblemaPL.objects.filter(user=request.user).order_by("created_at")
    index_map = {p.id: idx + 1 for idx, p in enumerate(todos)}
    qs = todos

    orden = request.GET.get("orden", "old")
    if orden == "new":
        qs = qs.order_by("-created_at")
    else:
        qs = qs.order_by("created_at")

    obj = request.GET.get("obj")
    if obj in {"max", "min"}:
        qs = qs.filter(objetivo=obj)

    desde = request.GET.get("desde")
    if desde:
        qs = qs.filter(created_at__date__gte=desde)

    hasta = request.GET.get("hasta")
    if hasta:
        qs = qs.filter(created_at__date__lte=hasta)

        qs = list(qs)
        for problema in qs:
         problema.numero = index_map.get(problema.id)

    context = {
        "problemas": qs,
        "orden": orden,
        "obj": obj or "",
        "desde": desde or "",
        "hasta": hasta or "",
    }
    return render(request, "historial.html", context)

@login_required
def ver_problema(request, pk):
    """Muestra el resultado de un problema guardado."""
    problema = get_object_or_404(ProblemaPL, pk=pk, user=request.user)

    resultado = resolver_problema_lineal(
        problema.objetivo,
        problema.coef_x1,
        problema.coef_x2,
        problema.restricciones,
    )

    grafico = resultado.pop("grafica", "")
    vertices = []
    opt_val = resultado.get("z")
    for idx, v in enumerate(resultado.get("vertices", []), start=1):
        vert = {
            "punto": f"P{idx}",
            "x1": v["x"],
            "x2": v["y"],
            "z": v["z"],
            "optimo": abs(v["z"] - opt_val) < 1e-6,
        }
        vertices.append({_k: to_native(_v) for _k, _v in vert.items()})

    objetivo_text = f"Z = {problema.coef_x1}x₁ + {problema.coef_x2}x₂"
    restricciones_fmt = [
        f"{r['coef_x1']}x₁ + {r['coef_x2']}x₂ {r['operador']} {r['valor']}"
        for r in problema.restricciones
    ]

    context = {
        "form": ProblemaPLForm(),
        "mensaje": "",
        "resultado": resultado,
        "grafico": grafico,
        "objetivo": objetivo_text,
        "restricciones": restricciones_fmt,
        "vertices": vertices,
    }
=======
        return render(request, "resultado.html", context)
    else:
        form = ProblemaPLForm()


    form = ProblemaPLForm()
    return render(request, "nuevo_problema.html", {"form": form, "mensaje": mensaje})
>>>>>>> origin/main
