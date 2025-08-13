from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.salesList, name='SaleList'),
    path('create', views.sale_create, name='saleCreate'),
    path('update/<int:pk>/', views.sale_update, name='saleUpdate'),
    path('delete/<int:pk>/', views.sale_delete, name='saleDelete'),
    path('update-products/<int:sale_id>/', views.sale_update_products, name='sale_update_products'),
    path('get-products/<int:sale_id>/', views.get_sale_products, name='get_sale_products'),
]