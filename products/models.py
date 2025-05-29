from django.db import models
from categories.models import Categoria 

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    codigo = models.CharField(max_length=50, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    # proveedor = models.CharField(max_length=100)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)
    stock_inicial = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
