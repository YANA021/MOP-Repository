from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
    path('historial/', views.history_list, name='historial'),
]