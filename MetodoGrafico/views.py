import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # noqa: F401

from .form import ProblemaPLForm
from .models import ProblemaPL
from .solver import resolver_problema_lineal


def home(request):
    """Renderiza la página de inicio."""
    return render(request, "home.html")


def metodo_grafico(request):
    """Muestra el formulario y procesa el método gráfico."""
    mensaje = ""

    # ------------------------------------------------------------------
    # 1) PETICIÓN POST: procesar formulario
    # ------------------------------------------------------------------
    if request.method == "POST":
        form = ProblemaPLForm(request.POST)

        if form.is_valid():
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
            if request.user.is_authenticated:
                ProblemaPL.objects.create(
                    user=request.user,
                    objetivo=form.cleaned_data["objetivo"],
                    coef_x1=form.cleaned_data["coef_x1"],
                    coef_x2=form.cleaned_data["coef_x2"],
                    restricciones=restricciones,
                )
                mensaje = "Problema guardado correctamente."

            # 1.3  Preparar límites opcionales
            limites = {
                "x1_min": form.cleaned_data.get("x1_min"),
                "x1_max": form.cleaned_data.get("x1_max"),
                "x2_min": form.cleaned_data.get("x2_min"),
                "x2_max": form.cleaned_data.get("x2_max"),
            }

            # 1.4  Resolver con el método gráfico
            resultado = resolver_problema_lineal(
                form.cleaned_data["objetivo"],
                form.cleaned_data["coef_x1"],
                form.cleaned_data["coef_x2"],
                restricciones,
                limites=limites,
            )

            # 1.5  Separar la gráfica del resto del resultado
            grafico = resultado.pop("grafica", "")
            request.session["grafico"] = grafico

            # 1.6  Preparar contexto para la plantilla de resultados
            context = {
                "form": ProblemaPLForm(),  # formulario limpio para nuevos datos
                "mensaje": mensaje,
                "resultado": resultado,
                "grafico": grafico,
                "post_data": request.POST.dict(),
                "restricciones_json": json.dumps(restricciones),
            }
            return render(request, "resultado.html", context)


    form = ProblemaPLForm()
    return render(request, "nuevo_problema.html", {"form": form, "mensaje": mensaje})


def ver_grafica(request):
    """Muestra la gráfica almacenada en la sesión."""
    grafico = request.session.pop("grafico", "")
    return render(request, "grafica.html", {"grafico": grafico})