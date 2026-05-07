"""Servicio simulado de WebPay Plus para procesar pagos.

Simula la integración con la API de Transbank WebPay Plus.
En producción se reemplazaría por la SDK real de Transbank.
"""
import uuid
import random
import string
from datetime import datetime
from decimal import Decimal


class WebPayPlusSimulado:
    """Simulación de la pasarela WebPay Plus de Transbank.

    Expone los mismos métodos que la SDK real:
    - crear_transaccion()
    - confirmar_transaccion()
    """
    AMBIENTE = 'INTEGRACION'
    CODIGO_COMERCIO = '597055555532'

    @staticmethod
    def crear_transaccion(numero_pedido, monto, url_retorno):
        """Simula Transaction.create() de WebPay Plus.

        Retorna un dict con token y url de redirección (simulados).
        """
        token = f"WP-{uuid.uuid4().hex[:16].upper()}"
        return {
            'token': token,
            'url': f'/pagos/webpay/formulario/?token={token}',
            'ambiente': WebPayPlusSimulado.AMBIENTE,
        }

    @staticmethod
    def confirmar_transaccion(token):
        """Simula Transaction.commit() de WebPay Plus.

        Retorna datos de la transacción como los devolvería Transbank.
        """
        # Simulamos 90% de aprobación
        aprobado = random.random() < 0.9
        codigo_auth = ''.join(random.choices(string.digits, k=6)) if aprobado else ''
        ultimos_4 = ''.join(random.choices(string.digits, k=4))

        return {
            'vci': 'TSY' if aprobado else 'TSN',
            'amount': 0,  # Se completa con el monto real
            'status': 'AUTHORIZED' if aprobado else 'FAILED',
            'buy_order': '',
            'session_id': '',
            'card_detail': {'card_number': f'XXXX-XXXX-XXXX-{ultimos_4}'},
            'accounting_date': datetime.now().strftime('%m%d'),
            'transaction_date': datetime.now().isoformat(),
            'authorization_code': codigo_auth,
            'payment_type_code': 'VN',
            'response_code': 0 if aprobado else -1,
            'installments_number': 0,
        }


def generar_boleta(pago):
    """Genera datos de boleta electrónica tras pago exitoso."""
    from pagos.models import Boleta

    monto_total = pago.monto
    monto_neto = (monto_total / Decimal('1.19')).quantize(Decimal('1'))
    monto_iva = monto_total - monto_neto

    rut_receptor = ''
    if hasattr(pago.pedido.usuario, 'perfil'):
        rut_receptor = pago.pedido.usuario.perfil.rut or ''

    boleta = Boleta.objects.create(
        pago=pago,
        numero_boleta=f"BOL-{uuid.uuid4().hex[:8].upper()}",
        rut_receptor=rut_receptor,
        monto_neto=monto_neto,
        monto_iva=monto_iva,
        monto_total=monto_total,
    )
    return boleta
