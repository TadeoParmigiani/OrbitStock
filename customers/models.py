from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=150) 
    dni_cuit = models.CharField(max_length=20, null=True, blank=True)  
    telefono = models.CharField(max_length=30, null=True, blank=True) 
    correo_electronico = models.EmailField(null=True, blank=True)  
    direccion = models.CharField(max_length=255, null=True, blank=True) 

    def __str__(self):
        return self.nombre
