from django.urls import path
from core import dashboard_views as views
from core import vendedor_views as vend

app_name = 'dashboards'

urlpatterns = [
    # Ejecutivo de Cuentas
    path('ejecutivo/', views.dashboard_ejecutivo, name='ejecutivo'),
    path('ejecutivo/stock/<int:bodega_id>/', views.stock_bodega, name='stock_bodega'),
    path('ejecutivo/aprobar/<int:pedido_id>/', views.aprobar_pedido, name='aprobar_pedido'),
    path('ejecutivo/revisar-stock/', views.revisar_stock, name='revisar_stock'),
    path('ejecutivo/actualizar-stock/<int:item_id>/', views.actualizar_stock, name='actualizar_stock'),
    path('ejecutivo/reporte-stock/descargar/', views.descargar_reporte_stock, name='descargar_reporte_stock'),
    path('ejecutivo/reporte-stock/enviar/', views.enviar_reporte_stock, name='enviar_reporte_stock'),
    path('ejecutivo/pedidos-aprobados/', views.pedidos_aprobados, name='pedidos_aprobados'),

    # Operador Logístico
    path('logistica/', views.dashboard_logistica, name='logistica'),
    path('logistica/preparar/<int:pedido_id>/', views.preparar_pedido, name='preparar_pedido'),
    path('logistica/despachar/<int:pedido_id>/', views.despachar_pedido, name='despachar_pedido'),

    # Analista de Finanzas
    path('analista/', views.dashboard_analista, name='analista'),
    path('analista/revisar/<int:pago_id>/', views.revisar_transferencia, name='revisar_transferencia'),
    path('analista/confirmar/<int:pago_id>/', views.confirmar_transferencia, name='confirmar_transferencia'),

    # Administrador
    path('administrador/', views.dashboard_administrador, name='administrador'),
    path('administrador/reporte/<str:tipo>/descargar/', views.descargar_reporte, name='descargar_reporte'),
    path('administrador/reporte/<str:tipo>/enviar/', views.enviar_reporte, name='enviar_reporte'),
    path('administrador/alianzas/', views.lista_alianzas, name='lista_alianzas'),
    path('administrador/alianzas/crear/', views.crear_alianza, name='crear_alianza'),
    path('administrador/alianzas/<int:alianza_id>/editar/', views.editar_alianza, name='editar_alianza'),
    path('administrador/alianzas/<int:alianza_id>/eliminar/', views.eliminar_alianza, name='eliminar_alianza'),

    # Vendedor
    path('vendedor/', views.dashboard_vendedor, name='vendedor'),

    # Cotizaciones
    path('vendedor/cotizaciones/', vend.lista_cotizaciones, name='lista_cotizaciones'),
    path('vendedor/cotizaciones/crear/', vend.crear_cotizacion, name='crear_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/', vend.detalle_cotizacion, name='detalle_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/editar/', vend.editar_cotizacion, name='editar_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/agregar-item/', vend.agregar_item_cotizacion, name='agregar_item_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/eliminar-item/<int:item_id>/', vend.eliminar_item_cotizacion, name='eliminar_item_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/estado/<str:nuevo_estado>/', vend.cambiar_estado_cotizacion, name='cambiar_estado_cotizacion'),
    path('vendedor/cotizaciones/<int:cot_id>/pdf/', vend.descargar_cotizacion_pdf, name='descargar_cotizacion_pdf'),
    path('vendedor/cotizaciones/<int:cot_id>/enviar/', vend.enviar_cotizacion_email, name='enviar_cotizacion_email'),
    path('vendedor/cotizaciones/<int:cot_id>/convertir/', vend.convertir_cotizacion_pedido, name='convertir_cotizacion_pedido'),

    # Asesoramiento
    path('vendedor/asesoramiento/', vend.lista_visitas, name='lista_visitas'),
    path('vendedor/asesoramiento/crear/', vend.crear_visita, name='crear_visita'),
    path('vendedor/asesoramiento/<int:visita_id>/editar/', vend.editar_visita, name='editar_visita'),
    path('vendedor/asesoramiento/<int:visita_id>/eliminar/', vend.eliminar_visita, name='eliminar_visita'),
]
