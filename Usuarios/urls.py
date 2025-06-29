from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inicio/', views.inicio_view, name='inicio'),
    path('signup/', views.sign_up_view, name='signup'),
]