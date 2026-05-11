from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_boleta_compra(pedido, pago, boleta):
    """Envía la boleta de confirmación de compra al usuario."""
    subject = f"Confirmación de Compra - Pedido {pedido.numero_pedido}"
    
    context = {
        'pedido': pedido,
        'pago': pago,
        'boleta': boleta,
        'usuario': pedido.usuario,
        'items': pedido.items.all(),
    }
    
    # We will use a simple HTML string to send the email
    html_message = f"""
    <h2>¡Gracias por tu compra en MediStock!</h2>
    <p>Hola {pedido.usuario.first_name or pedido.usuario.username},</p>
    <p>Hemos recibido tu pago y tu pedido <strong>{pedido.numero_pedido}</strong> ha sido confirmado.</p>
    
    <h3>Detalles de la Boleta</h3>
    <ul>
        <li><strong>Nro Boleta:</strong> {boleta.numero_boleta}</li>
        <li><strong>Subtotal:</strong> ${pedido.subtotal}</li>
        {f"<li style='color:red;'><strong>Descuento (Vendedor):</strong> -${pedido.descuento}</li>" if pedido.descuento > 0 else ""}
        <li><strong>Costo de Envío:</strong> ${pedido.costo_envio}</li>
        <li><strong>Total Pagado:</strong> ${boleta.monto_total}</li>
        <li><strong>Fecha:</strong> {pago.completado_en.strftime('%d/%m/%Y %H:%M') if pago.completado_en else ''}</li>
    </ul>
    
    <p>Tu pedido será preparado para despacho según el método seleccionado.</p>
    <p>Te notificaremos cuando haya cambios en el estado de tu pedido.</p>
    <br>
    <p>Saludos,</p>
    <p>El equipo de MediStock</p>
    """
    
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = pedido.usuario.email
    
    if to_email:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message, fail_silently=True)

def enviar_notificacion_estado(pedido, estado_anterior):
    """Envía una notificación al usuario cuando el estado del pedido cambia."""
    subject = f"Actualización de Pedido {pedido.numero_pedido}"
    
    estado_display = pedido.get_estado_display()
    
    html_message = f"""
    <h2>Actualización de tu pedido en MediStock</h2>
    <p>Hola {pedido.usuario.first_name or pedido.usuario.username},</p>
    <p>Te informamos que el estado de tu pedido <strong>{pedido.numero_pedido}</strong> ha cambiado.</p>
    
    <p><strong>Nuevo Estado:</strong> {estado_display}</p>
    """
    
    if pedido.estado == 'despachado' and pedido.numero_seguimiento:
        html_message += f"<p><strong>Número de Seguimiento:</strong> {pedido.numero_seguimiento}</p>"
        
    html_message += """
    <p>Puedes revisar los detalles de tu pedido en tu cuenta de MediStock.</p>
    <br>
    <p>Saludos,</p>
    <p>El equipo de MediStock</p>
    """
    
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = pedido.usuario.email
    
    if to_email:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message, fail_silently=True)
