from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
import uuid
from productos.models import Producto, Categoria


def inicio(request):
    """Pagina principal de MediStock."""
    productos_destacados = Producto.objects.filter(
        activo=True, destacado=True
    ).select_related('categoria', 'marca')[:8]

    categorias = Categoria.objects.filter(
        activa=True, padre__isnull=True
    ).order_by('orden')[:6]

    contexto = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    }
    return render(request, 'core/home.html', contexto)


def nosotros(request):
    return render(request, 'core/nosotros.html')


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')

        if nombre and email and asunto and mensaje:
            codigo = f"CT-{uuid.uuid4().hex[:6].upper()}"

            # 1. Correo de confirmación al cliente
            subject_cliente = f"Hemos recibido tu consulta - {codigo}"
            mensaje_cliente = f"Hola {nombre},\n\nGracias por ponerte en contacto con MediStock, tu código de consulta es {codigo}. Te atenderemos dentro de 24h.\n\nAtentamente,\nEquipo MediStock"
            
            send_mail(
                subject_cliente,
                mensaje_cliente,
                'no-reply@medistock.cl',
                [email],
                fail_silently=True
            )

            # 2. Correo al equipo de Medistock
            subject_medistock = f"Nueva Consulta: {asunto} [{codigo}]"
            mensaje_medistock = f"Nueva consulta web:\n\nNombre: {nombre}\nEmail: {email}\nAsunto: {asunto}\nCódigo: {codigo}\n\nMensaje:\n{mensaje}"
            
            email_msg = EmailMessage(
                subject_medistock,
                mensaje_medistock,
                'no-reply@medistock.cl',
                ['contacto@medistock.cl'],
                reply_to=[email],
            )
            email_msg.send(fail_silently=True)

            messages.success(request, f"¡Gracias! Tu mensaje fue enviado. Tu código de consulta es {codigo}.")
            return redirect('core:contacto')

    return render(request, 'core/contacto.html')
