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

    # Reportes PDF — Descargar y Enviar por correo
    path('administrador/reporte/<str:tipo>/descargar/', views.descargar_reporte, name='descargar_reporte'),
    path('administrador/reporte/<str:tipo>/enviar/', views.enviar_reporte, name='enviar_reporte'),

    # Alianzas Estratégicas CRUD
    path('administrador/alianzas/', views.lista_alianzas, name='lista_alianzas'),
    path('administrador/alianzas/crear/', views.crear_alianza, name='crear_alianza'),
    path('administrador/alianzas/<int:alianza_id>/editar/', views.editar_alianza, name='editar_alianza'),
    path('administrador/alianzas/<int:alianza_id>/eliminar/', views.eliminar_alianza, name='eliminar_alianza'),

    # Vendedor
    path('vendedor/', views.dashboard_vendedor, name='vendedor'),
]
