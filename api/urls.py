"""URLs de la API REST v1 de MediStock."""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('productos/', views.ProductoListAPI.as_view(), name='producto_lista'),
    path('productos/<str:codigo_producto>/', views.ProductoDetalleAPI.as_view(), name='producto_detalle'),
    path('categorias/', views.CategoriaListAPI.as_view(), name='categoria_lista'),
]
