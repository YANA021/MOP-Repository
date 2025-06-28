from django.urls import path
from . import views

urlpatterns = [
    path('', views.metodo_grafico, name='metodo_grafico'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
]