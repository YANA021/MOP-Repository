from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'metodo'

urlpatterns = [
    path('Inicio/', views.home, name='home'),
    path('solucionador/', views.metodo_grafico, name='metodo_grafico'),
    path('historial/', login_required(views.historial_problemas), name='historial'),
    
]