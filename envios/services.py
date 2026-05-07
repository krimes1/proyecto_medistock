"""Servicio simulado de API de Logística/Tracking.

Simula la integración con Chilexpress/Shippo para:
- Generar números de seguimiento
- Consultar estado de envío
- Obtener historial de eventos
"""
import uuid
import random
from datetime import datetime, timedelta
from django.utils import timezone


class TrackingAPISimulado:
    """Simulación de API de tracking (estilo Chilexpress/Shippo).

    Métodos principales:
    - crear_envio()     → Genera etiqueta y número de seguimiento
    - consultar_estado() → Obtiene estado actual del envío
    - obtener_eventos()  → Historial completo de tracking
    """

    TRANSPORTISTAS = ['chilexpress', 'starken', 'bluexpress', 'correos']

    @staticmethod
    def crear_envio(pedido, transportista='chilexpress'):
        """Simula la creación de un envío en la API del transportista.

        Retorna número de seguimiento y fecha estimada de entrega.
        """
        # Generar número de seguimiento similar al real
        prefijos = {
            'chilexpress': 'CHX',
            'starken': 'STK',
            'bluexpress': 'BLX',
            'correos': 'CHL',
        }
        prefijo = prefijos.get(transportista, 'TRK')
        numero = f"{prefijo}{uuid.uuid4().hex[:10].upper()}"

        # Calcular entrega estimada
        dias = 3 if pedido.tipo_despacho == 'express' else 7
        if pedido.prioridad == 'critico':
            dias = 1
        elif pedido.prioridad == 'urgente':
            dias = 2

        entrega_estimada = (timezone.now() + timedelta(days=dias)).date()

        return {
            'numero_seguimiento': numero,
            'transportista': transportista,
            'entrega_estimada': entrega_estimada,
            'estado': 'etiqueta_creada',
            'peso_estimado': round(random.uniform(0.5, 15.0), 2),
        }

    @staticmethod
    def consultar_estado(numero_seguimiento):
        """Simula consulta de estado a la API del transportista."""
        return {
            'numero_seguimiento': numero_seguimiento,
            'estado': 'en_transito',
            'ultima_ubicacion': 'Centro de Distribución Santiago',
            'fecha_actualizacion': timezone.now().isoformat(),
        }

    @staticmethod
    def generar_eventos_demo(envio):
        """Genera eventos de tracking de demostración."""
        from envios.models import EventoSeguimiento

        ahora = timezone.now()
        eventos_data = [
            ('Etiqueta creada', 'Bodega MediStock, Santiago', ahora - timedelta(hours=48)),
            ('Recogido por transportista', 'Bodega MediStock, Santiago', ahora - timedelta(hours=36)),
            ('En tránsito', 'Centro de Distribución, Santiago', ahora - timedelta(hours=24)),
            ('En reparto', f'Ciudad destino: {envio.pedido.ciudad_envio}', ahora - timedelta(hours=6)),
        ]

        for estado, ubicacion, fecha in eventos_data:
            EventoSeguimiento.objects.get_or_create(
                envio=envio,
                estado=estado,
                ubicacion=ubicacion,
                defaults={
                    'descripcion': f'{estado} - Paquete procesado correctamente.',
                    'fecha_hora': fecha,
                }
            )
