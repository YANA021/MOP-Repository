import json
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .form import ProblemaPLForm
from .models import ProblemaPL, HistoryEntry
from .solver import resolver_problema_lineal


def home(request):
    """Renderiza la página de inicio."""
    return render(request, "home.html")


def metodo_grafico(request):
    """
    Muestra el formulario, resuelve el problema con el método gráfico,
    guarda el ProblemaPL (si está autenticado) y registra la entrada en HistoryEntry.
    """
    mensaje = ""
    resultado = None
    grafico = ""
    post_data = None

    if request.method == "POST":
        form = ProblemaPLForm(request.POST)
        if form.is_valid():
            # Guardar el problema PL si el usuario está autenticado
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data["objetivo"],
                    coef_x1=form.cleaned_data["coef_x1"],
                    coef_x2=form.cleaned_data["coef_x2"],
                    restricciones=form.cleaned_data["restricciones"],
                )
                mensaje = "Problema guardado correctamente."

            # Preparamos límites si los hay
            limites = {
                "x1_min": form.cleaned_data.get("x1_min"),
                "x1_max": form.cleaned_data.get("x1_max"),
                "x2_min": form.cleaned_data.get("x2_min"),
                "x2_max": form.cleaned_data.get("x2_max"),
            }

            # Resolver el problema
            salida = resolver_problema_lineal(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                form.cleaned_data["restricciones"],
                limites=limites,
            )

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

            context = {
                "form": form,
                "mensaje": mensaje,
                "resultado": resultado,
                "grafico": grafico,
                "post_data": post_data,
                "restricciones_json": json.dumps(restricciones_data),
            }
            return render(request, "resultado.html", context)

    else:
        form = ProblemaPLForm()

    return render(request, "nuevo_problema.html", {"form": form, "mensaje": mensaje})


@login_required
def history_list(request):
    entries = HistoryEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'MetodoGrafico/history.html', {'entries': entries})
