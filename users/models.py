from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Empleado'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

  
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser'
    )

    def __str__(self):
        return self.username
