from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto
from categories.models import Categoria

@login_required(login_url='login')
def productList(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    return render(request, 'products.html', {'productos': productos, 'categorias': categorias})

@login_required(login_url='login')
def productCreate(request):
    if request.method == 'POST':
        try:
            producto = Producto(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                codigo=request.POST['codigo'],
                categoria_id=request.POST['categoria'],
                precio_compra=request.POST['precio_compra'],
                precio_venta=request.POST['precio_venta'],
                stock_inicial=request.POST['stock_inicial'],
                estado=bool(request.POST.get('estado', False)),
                imagen=request.FILES.get('imagen', None),
            )
            producto.save()
            messages.success(request, 'Producto agregado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al guardar el producto: {e}')
    return redirect('productList')

@login_required(login_url='login')
def productUpdate(request, id):
    producto = get_object_or_404(Producto, pk=id)
    if request.method == 'POST':
        try:
            producto.nombre = request.POST['nombre']
            producto.descripcion = request.POST['descripcion']
            producto.codigo = request.POST['codigo']
            producto.categoria_id = request.POST['categoria']
            producto.precio_compra = request.POST['precio_compra']
            producto.precio_venta = request.POST['precio_venta']
            producto.stock_inicial = request.POST['stock_inicial']
            producto.estado = bool(request.POST.get('estado', False))
            if 'imagen' in request.FILES:
                producto.imagen = request.FILES['imagen']
            producto.save()
            messages.success(request, 'Producto actualizado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
        return redirect('productList')
    else:
        categorias = Categoria.objects.all()
        return render(request, 'editar_producto.html', {
            'producto': producto,
            'categorias': categorias
        })

@login_required(login_url='login')
def productDelete(request, id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=id)
        producto.delete()
        messages.success(request, 'Producto eliminado.')
    return redirect('productList')
