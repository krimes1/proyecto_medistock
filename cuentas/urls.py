from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('login/', views.vista_login, name='login'),
    path('registro/', views.vista_registro, name='registro'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('logout/', views.vista_logout, name='logout'),
    path('perfil/', views.vista_perfil, name='perfil'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]
