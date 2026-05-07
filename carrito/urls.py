from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.detalle_carrito, name='detalle_carrito'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar'),
    path('actualizar/<int:item_id>/', views.actualizar_item, name='actualizar'),
    path('eliminar/<int:item_id>/', views.eliminar_item, name='eliminar'),
]
