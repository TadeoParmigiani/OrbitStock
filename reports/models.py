from django.db import models
from django.conf import settings
from django.utils import timezone

class Report(models.Model):
    TIPO_CHOICES = [
        ('ventas', 'Reporte de Ventas'),
        ('stock', 'Reporte de Stock'),
    ]
    
    FORMATO_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'En proceso'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de reporte")
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, verbose_name="Formato")
    descripcion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descripción")
    fecha_inicio = models.DateField(verbose_name="Fecha inicio")
    fecha_fin = models.DateField(verbose_name="Fecha fin")
    
    ruta_archivo = models.CharField(max_length=500, verbose_name="Ruta del archivo")
    tamaño_archivo = models.BigIntegerField(default=0, verbose_name="Tamaño del archivo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Creado por")
    
    # Estadísticas del reporte
    total_registros = models.IntegerField(default=0, verbose_name="Total registros")
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Monto total")
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
    
    def __str__(self):
        return f"{self.get_tipo_display()} {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')} - {self.get_estado_display()}"
    
    def get_periodo(self):
        return f"{self.fecha_inicio.strftime('%d/%m/%Y')} - {self.fecha_fin.strftime('%d/%m/%Y')}"