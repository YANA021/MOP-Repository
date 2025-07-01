from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'metodo'

urlpatterns = [
    path('Inicio/', views.home, name='home'),
    path('solucionador/', views.metodo_grafico, name='metodo_grafico'),
    path('sistema/', views.resolver_sistema, name='resolver_sistema'),
    path('historial/', login_required(views.historial_problemas), name='historial'),
    path('problema/<int:pk>/', login_required(views.ver_problema), name='ver_problema'),
     # A)  Descarga directa de la gráfica (usa el id del problema)
    path(
        "export/<int:pk>/pdf/",
        views.export_pdf,          # ← vista que genera el PDF con PIL / ReportLab
        name="export_pdf",
    ),

    # B)  Conversión en el servidor de un PNG enviado por JS (sin pk)
    path(
        "export/pdf-image/",
        views.export_pdf_image,
        name="export_pdf_image",
    ),

    
]