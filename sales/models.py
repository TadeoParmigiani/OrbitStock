from django.db import models
from products.models import Producto
from customers.models import Cliente  # Cliente es otra app

class Venta(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    productos = models.ManyToManyField(Producto, through='DetalleVenta')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta #{self.venta.id}"
