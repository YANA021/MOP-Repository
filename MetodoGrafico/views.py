import json
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .form import ProblemaPLForm
from .models import ProblemaPL
from .solver import resolver_problema_lineal


def home(request):
    """Renderiza la página de inicio."""
    return render(request, "home.html")

def metodo_grafico(request):
    """Muestra el formulario y procesa el método gráfico."""
    mensaje = ""
    resultado = None
    grafico = ""
    post_data = None

    if request.method == "POST":
        form = ProblemaPLForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data["objetivo"],
                    coef_x1=form.cleaned_data["coef_x1"],
                    coef_x2=form.cleaned_data["coef_x2"],
                    restricciones=form.cleaned_data["restricciones"],
                )
                mensaje = "Problema guardado correctamente."

            limites = {
                "x1_min": form.cleaned_data.get("x1_min"),
                "x1_max": form.cleaned_data.get("x1_max"),
                "x2_min": form.cleaned_data.get("x2_min"),
                "x2_max": form.cleaned_data.get("x2_max"),
            }

            resultado = resolver_problema_lineal(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                form.cleaned_data["restricciones"],
                limites=limites,
            )

            grafico = resultado.get("grafica", "")
            request.session["grafico"] = grafico
            resultado = {k: v for k, v in resultado.items() if k != "grafica"}
            post_data = request.POST.dict()
            restricciones_data = form.cleaned_data.get("restricciones", [])
            form = ProblemaPLForm()

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

    context = {"form": form, "mensaje": mensaje}
    return render(request, "nuevo_problema.html", context)


def ver_grafica(request):
    """Muestra la gráfica almacenada en la sesión."""
    grafico = request.session.pop("grafico", "")
    return render(request, "grafica.html", {"grafico": grafico})