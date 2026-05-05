from django.db import models
from django.urls import reverse


class Categoria(models.Model):
    """Categorias de insumos medicos: Descartables, Quirurgicos, etc."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug URL')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True, verbose_name='Imagen')
    padre = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='hijos', verbose_name='Categoria Padre')
    activa = models.BooleanField(default=True, verbose_name='Activa')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('productos:detalle_categoria', kwargs={'slug': self.slug})


class Marca(models.Model):
    """Marcas de insumos y equipamiento medico."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug URL')
    logo = models.ImageField(upload_to='marcas/', blank=True, null=True, verbose_name='Logo')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto / Insumo Medico."""
    OPCIONES_TIPO = [
        ('descartable', 'Descartable'),
        ('quirurgico', 'Quirurgico'),
    ]

    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug URL')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU / Codigo')
    descripcion = models.TextField(verbose_name='Descripcion')
    descripcion_corta = models.CharField(max_length=300, blank=True, verbose_name='Descripcion Corta')
    tipo_producto = models.CharField(max_length=20, choices=OPCIONES_TIPO, default='descartable', verbose_name='Tipo')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos', verbose_name='Categoria')
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name='Marca')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio (CLP)')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name='Imagen Principal')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    destacado = models.BooleanField(default=False, verbose_name='Destacado')
    requiere_receta = models.BooleanField(default=False, verbose_name='Requiere Receta')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

    def get_absolute_url(self):
        return reverse('productos:detalle_producto', kwargs={'slug': self.slug})

    @property
    def stock_total(self):
        from inventario.models import ItemStock
        return ItemStock.objects.filter(producto=self, cantidad__gt=0).aggregate(total=models.Sum('cantidad'))['total'] or 0

    @property
    def en_stock(self):
        return self.stock_total > 0


class ImagenProducto(models.Model):
    """Imagenes adicionales del producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes', verbose_name='Producto')
    imagen = models.ImageField(upload_to='productos/galeria/', verbose_name='Imagen')
    texto_alt = models.CharField(max_length=200, blank=True, verbose_name='Texto Alternativo')
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imagenes de Productos'
        ordering = ['orden']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
