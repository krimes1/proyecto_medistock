from django.urls import path
from core import dashboard_views as views

app_name = 'dashboards'

urlpatterns = [
    # Ejecutivo de Cuentas
    path('ejecutivo/', views.dashboard_ejecutivo, name='ejecutivo'),
    path('ejecutivo/stock/<int:bodega_id>/', views.stock_bodega, name='stock_bodega'),
    path('ejecutivo/aprobar/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),

    # Operador Logístico
    path('logistica/', views.dashboard_logistica, name='logistica'),
    path('logistica/preparar/<int:pedido_id>/', views.preparar_pedido, name='preparar_pedido'),
    path('logistica/despachar/<int:pedido_id>/', views.despachar_pedido, name='despachar_pedido'),

    # Analista de Finanzas
    path('analista/', views.dashboard_analista, name='analista'),
    path('analista/confirmar/<int:pago_id>/', views.confirmar_transferencia, name='confirmar_transferencia'),

    # Administrador
    path('administrador/', views.dashboard_administrador, name='administrador'),

    # Vendedor
    path('vendedor/', views.dashboard_vendedor, name='vendedor'),
]
