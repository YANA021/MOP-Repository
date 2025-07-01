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
    
    # ÚNICA ruta para descargar el PDF (requiere pk)
    path(
        "export/<int:pk>/pdf/",
        login_required(views.export_pdf),
        name="export_pdf",
    ),

     path(
        "export/pdf-image/",
        views.export_pdf_image,
        name="export_pdf_image",
    ),
   

    
]