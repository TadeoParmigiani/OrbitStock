from django.urls import path
from . import views

urlpatterns = [
    path('list', views.categoryList, name='categoryList'),
    path('crear', views.categoryCreate, name='categoryCreate'),
    path('editar', views.categoryUpdate, name='categoryUpdate'),
    path('eliminar', views.categoryDelete, name='categoryDelete'),
]