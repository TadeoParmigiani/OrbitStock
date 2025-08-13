from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.clientList, name='clientList'),         
    path('create/', views.clientCreate, name='clientCreate'),   
    path('update/', views.clientUpdate, name='clientUpdate'),   
    path('delete/', views.clientDelete, name='clientDelete'),   
]
