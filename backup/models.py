from django.db import models
from django.conf import settings
from django.utils import timezone

class Backup(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'En proceso'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]
    
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    ruta_archivo = models.CharField(max_length=500, verbose_name="Ruta del archivo")
    tamaño_archivo = models.BigIntegerField(default=0, verbose_name="Tamaño del archivo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Creado por")
    
    total_productos = models.IntegerField(default=0, verbose_name="Total productos respaldados")
    total_categorias = models.IntegerField(default=0, verbose_name="Total categorías respaldadas")
    total_usuarios = models.IntegerField(default=0, verbose_name="Total usuarios respaldados")
    total_ventas = models.IntegerField(default=0, verbose_name="Total ventas respaldadas")
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Respaldo"
        verbose_name_plural = "Respaldos"
    
    def __str__(self):
        return f"Backup {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')} - {self.get_estado_display()}"