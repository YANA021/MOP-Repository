from django.urls import path
from . import views

app_name = 'metodo'

urlpatterns = [
    path('Inicio/', views.home, name='home'),
    path('solucionador/', views.metodo_grafico, name='metodo_grafico'),
    
]