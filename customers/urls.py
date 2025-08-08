from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.clientList, name='clientList'),         # Listar clientes
    path('create/', views.clientCreate, name='clientCreate'),   # Crear cliente
    path('update/', views.clientUpdate, name='clientUpdate'),   # Editar cliente
    path('delete/', views.clientDelete, name='clientDelete'),   # Eliminar cliente
]
