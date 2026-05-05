from django.urls import path
app_name = 'carrito'
urlpatterns = [
    path('', lambda r: __import__('django.http', fromlist=['HttpResponse']).HttpResponse('Carrito - Proximamente'), name='detalle_carrito'),
]
