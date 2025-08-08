from django.urls import path
from . import views


urlpatterns = [
    path('list', views.productList, name='productList'),
    path('create', views.productCreate, name='productCreate'),
    path('update/<int:id>/', views.productUpdate, name='productUpdate'),
    path('delete/<int:id>/', views.productDelete, name='productDelete'),
] 
