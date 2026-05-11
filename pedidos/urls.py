from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle'),
    path('<int:pedido_id>/confirmacion/', views.confirmacion_pedido, name='confirmacion'),
    path('validar-vendedor/', views.validar_codigo_vendedor, name='validar_vendedor'),
]
