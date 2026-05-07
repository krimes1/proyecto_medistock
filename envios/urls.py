from django.urls import path
from . import views

app_name = 'envios'

urlpatterns = [
    path('tracking/', views.tracking_publico, name='tracking'),
    path('mi-envio/<int:pedido_id>/', views.mi_envio, name='mi_envio'),
]
