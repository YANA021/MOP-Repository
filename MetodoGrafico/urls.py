from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('metodo-grafico/', views.metodo_grafico, name='metodo_grafico'),
    path('problema/<int:pk>/', login_required(views.ver_problema), name='ver_problema'),
]