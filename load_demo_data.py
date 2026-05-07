"""Script para cargar datos de prueba en MediStock."""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth.models import User
from productos.models import Categoria, Marca, Producto
from inventario.models import Bodega, ItemStock
from datetime import date, timedelta

# --- Superusuario ---
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@medistock.cl', 'admin123')
    u.first_name = 'Admin'
    u.last_name = 'MediStock'
    u.save()
    u.perfil.rol = 'administrador'
    u.perfil.save()
    print("Superusuario creado")

# --- Categorias ---
datos_categorias = [
    ('Descartables', 'descartables', 'Guantes, jeringas, mascarillas y mas', 1),
    ('Quirurgicos', 'quirurgicos', 'Instrumental y material quirurgico', 2),
    ('Equipamiento', 'equipamiento', 'Monitores, dispositivos y equipos medicos', 3),
    ('Laboratorio', 'laboratorio', 'Insumos para analisis clinicos', 4),
    ('Proteccion Personal', 'proteccion-personal', 'EPP y elementos de seguridad', 5),
    ('Curacion', 'curacion', 'Vendas, gasas y material de curacion', 6),
]
for nombre, slug, desc, orden in datos_categorias:
    Categoria.objects.get_or_create(nombre=nombre, slug=slug, defaults={'descripcion': desc, 'orden': orden})
print(f"{Categoria.objects.count()} categorias")

# --- Marcas ---
datos_marcas = [('3M', '3m'), ('Medline', 'medline'), ('BD', 'bd'), ('Cardinal Health', 'cardinal-health'), ('MediPro', 'medipro')]
for nombre, slug in datos_marcas:
    Marca.objects.get_or_create(nombre=nombre, slug=slug)
print(f"{Marca.objects.count()} marcas")

# --- Bodegas ---
datos_bodegas = [
    ('BOD-RM1', 'Bodega Central Providencia', 'Av. Providencia 1234', 'Providencia', 'Region Metropolitana'),
    ('BOD-RM2', 'Bodega Maipu', 'Av. Pajaritos 5678', 'Maipu', 'Region Metropolitana'),
    ('BOD-RM3', 'Bodega Puente Alto', 'Av. Concha y Toro 910', 'Puente Alto', 'Region Metropolitana'),
    ('BOD-S1', 'Bodega Concepcion', 'Av. Los Carrera 456', 'Concepcion', 'Biobio'),
    ('BOD-S2', 'Bodega Temuco', 'Av. Alemania 789', 'Temuco', 'La Araucania'),
]
for codigo, nombre, dir, ciudad, region in datos_bodegas:
    Bodega.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre, 'direccion': dir, 'ciudad': ciudad, 'region': region})
print(f"{Bodega.objects.count()} bodegas")

# --- Productos ---
cat_desc = Categoria.objects.get(slug='descartables')
cat_quir = Categoria.objects.get(slug='quirurgicos')
cat_equip = Categoria.objects.get(slug='equipamiento')
cat_lab = Categoria.objects.get(slug='laboratorio')
cat_epp = Categoria.objects.get(slug='proteccion-personal')
cat_cur = Categoria.objects.get(slug='curacion')
marca_3m = Marca.objects.get(slug='3m')
marca_bd = Marca.objects.get(slug='bd')
marca_medline = Marca.objects.get(slug='medline')
marca_cardinal = Marca.objects.get(slug='cardinal-health')
marca_medipro = Marca.objects.get(slug='medipro')

datos_productos = [
    ('Guantes de Nitrilo Caja x100', 'guantes-nitrilo-x100', 'MS-D001', cat_desc, marca_medline, 12990, 'descartable', True, 'productos/guantes-nitrilo.png'),
    ('Jeringas Desechables 5ml x50', 'jeringas-5ml-x50', 'MS-D002', cat_desc, marca_bd, 8990, 'descartable', True, 'productos/jeringas.png'),
    ('Mascarillas Quirurgicas x50', 'mascarillas-quirurgicas-x50', 'MS-D003', cat_desc, marca_3m, 6990, 'descartable', True, 'productos/mascarillas.png'),
    ('Gasa Esteril 10x10 x100', 'gasa-esteril-10x10', 'MS-C001', cat_cur, marca_medline, 15990, 'descartable', True, 'productos/gasa.png'),
    ('Venda Elastica 10cm x12', 'venda-elastica-10cm', 'MS-C002', cat_cur, marca_cardinal, 9490, 'descartable', False, ''),
    ('Set de Sutura Basico', 'set-sutura-basico', 'MS-Q001', cat_quir, marca_medipro, 45990, 'quirurgico', True, 'productos/set-sutura.png'),
    ('Pinza Hemostatica Kelly', 'pinza-hemostatica-kelly', 'MS-Q002', cat_quir, marca_medipro, 32990, 'quirurgico', False, ''),
    ('Bisturi Desechable N15 x10', 'bisturi-desechable-n15', 'MS-Q003', cat_quir, marca_bd, 18990, 'quirurgico', True, ''),
    ('Oximetro de Pulso Digital', 'oximetro-pulso-digital', 'MS-E001', cat_equip, marca_medipro, 29990, 'quirurgico', True, 'productos/oximetro.png'),
    ('Tensiometro Digital de Brazo', 'tensiometro-digital-brazo', 'MS-E002', cat_equip, marca_medipro, 34990, 'quirurgico', True, 'productos/tensiometro.png'),
    ('Termometro Infrarrojo Medico', 'termometro-infrarrojo', 'MS-E003', cat_equip, marca_3m, 45000, 'quirurgico', True, 'productos/termometro.png'),
    ('Estetoscopio Profesional', 'estetoscopio-profesional', 'MS-E004', cat_equip, marca_medline, 59990, 'quirurgico', False, ''),
    ('Tubos de Ensayo x100', 'tubos-ensayo-x100', 'MS-L001', cat_lab, marca_bd, 22990, 'descartable', False, ''),
    ('Pipetas Pasteur Esteriles x500', 'pipetas-pasteur-x500', 'MS-L002', cat_lab, marca_cardinal, 18990, 'descartable', False, ''),
    ('Traje Tyvek Proteccion Total', 'traje-tyvek-proteccion', 'MS-P001', cat_epp, marca_3m, 15990, 'descartable', True, ''),
    ('Careta Facial Protectora', 'careta-facial-protectora', 'MS-P002', cat_epp, marca_3m, 7990, 'descartable', False, ''),
]

for nombre, slug, sku, cat, marca, precio, tipo, destacado, imagen in datos_productos:
    Producto.objects.get_or_create(sku=sku, defaults={
        'nombre': nombre, 'slug': slug, 'descripcion': f'{nombre}. Producto de alta calidad para uso clinico profesional.',
        'descripcion_corta': nombre, 'categoria': cat, 'marca': marca,
        'precio': precio, 'tipo_producto': tipo, 'destacado': destacado,
        'imagen': imagen if imagen else None
    })
    
    if imagen:
        Producto.objects.filter(sku=sku).update(imagen=imagen)

print(f"{Producto.objects.count()} productos")

# --- Stock ---
bod_central = Bodega.objects.get(codigo='BOD-RM1')
bod_maipu = Bodega.objects.get(codigo='BOD-RM2')
vencimiento = date.today() + timedelta(days=365)

for producto in Producto.objects.all():
    ItemStock.objects.get_or_create(
        producto=producto, bodega=bod_central, numero_lote=f"L2026-{producto.sku[-4:]}",
        defaults={'cantidad': 150, 'fecha_vencimiento': vencimiento}
    )
    ItemStock.objects.get_or_create(
        producto=producto, bodega=bod_maipu, numero_lote=f"L2026-{producto.sku[-4:]}-B",
        defaults={'cantidad': 80, 'fecha_vencimiento': vencimiento + timedelta(days=180)}
    )
print(f"{ItemStock.objects.count()} items de stock")
print("Datos de prueba cargados!")
