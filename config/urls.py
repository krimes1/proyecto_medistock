"""Configuracion de URLs para el proyecto MediStock."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('productos/', include('productos.urls')),
    path('carrito/', include('carrito.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('cuenta/', include('cuentas.urls')),
    path('pagos/', include('pagos.urls')),
    path('envios/', include('envios.urls')),
    path('api/v1/', include('api.urls')),
    # Documentación API B2B (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('panel/', include('core.dashboard_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'MediStock - Panel de Administracion'
admin.site.site_title = 'MediStock Admin'
admin.site.index_title = 'Gestion de Insumos Medicos'
