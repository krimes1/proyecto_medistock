from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('iniciar/<int:pedido_id>/', views.iniciar_pago, name='iniciar_pago'),
    path('webpay/formulario/', views.formulario_webpay, name='formulario_webpay'),
    path('webpay/retorno/', views.retorno_webpay, name='retorno_webpay'),
    path('exitoso/<int:pedido_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('fallido/<int:pedido_id>/', views.pago_fallido, name='pago_fallido'),
    path('boleta/<int:pedido_id>/', views.ver_boleta, name='ver_boleta'),
]
