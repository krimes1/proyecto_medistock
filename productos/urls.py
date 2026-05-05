from django.urls import path
app_name = 'productos'
urlpatterns = [
    path('', lambda r: __import__('django.http', fromlist=['HttpResponse']).HttpResponse('Catalogo - Proximamente'), name='lista_productos'),
    path('categoria/<slug:slug>/', lambda r, slug: __import__('django.http', fromlist=['HttpResponse']).HttpResponse(f'Categoria: {slug}'), name='detalle_categoria'),
    path('<slug:slug>/', lambda r, slug: __import__('django.http', fromlist=['HttpResponse']).HttpResponse(f'Producto: {slug}'), name='detalle_producto'),
]
