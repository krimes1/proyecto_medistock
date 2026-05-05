from django.urls import path
app_name = 'cuentas'
urlpatterns = [
    path('login/', lambda r: __import__('django.http', fromlist=['HttpResponse']).HttpResponse('Login - Proximamente'), name='login'),
]
