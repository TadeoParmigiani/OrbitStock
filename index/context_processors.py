from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from products.models import Producto


def stock_bajo_context(request):
    stock_bajo = Producto.objects.filter(stock_inicial__lt=5)
    return {'stock_bajo': stock_bajo}