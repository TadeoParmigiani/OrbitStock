from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Venta, DetalleVenta
from products.models import Producto
from customers.models import Cliente
from decimal import Decimal
from django.contrib import messages

@login_required
def salesList(request):
    ventas = Venta.objects.all().order_by('-fecha')
    clientes = Cliente.objects.all()
    productos = Producto.objects.all()
    return render(request, 'sales.html', {
        'ventas': ventas,
        'clientes': clientes,
        'productos': productos,
    })

@login_required
def sale_create(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        fecha = request.POST.get('fecha')
        producto_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')

        cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
        usuario = request.user

        total = Decimal(0)
        detalles = []

        # Validar stock antes de registrar la venta
        for producto_id, cantidad_str in zip(producto_ids, cantidades):
            producto = Producto.objects.get(id=producto_id)
            cantidad = int(cantidad_str)

            if producto.stock_inicial < cantidad:
                messages.error(request, f"No hay suficiente stock para el producto {producto.nombre}. Stock disponible: {producto.stock_inicial}")
                return redirect('SaleList')

            subtotal = producto.precio_venta * cantidad
            total += subtotal

            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': producto.precio_venta,
            })

        # Registrar la venta solo si todos los productos tienen stock suficiente
        venta = Venta.objects.create(cliente=cliente, usuario=usuario, total=total)

        for detalle in detalles:
            DetalleVenta.objects.create(
                venta=venta,
                producto=detalle['producto'],
                cantidad=detalle['cantidad'],
                precio_unitario=detalle['precio_unitario']
            )

            # Descontar stock
            detalle['producto'].stock_inicial -= detalle['cantidad']
            detalle['producto'].save()

    return redirect('SaleList')

@login_required
def sale_update(request, pk):
    venta = get_object_or_404(Venta, pk=pk)

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente') or request.POST.get('id_cliente')
        metodo_pago = request.POST.get('metodo_pago')

        cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
        venta.cliente = cliente
        venta.metodo_pago = metodo_pago

        # NO modificar productos ni stock aquí
        # El total debería actualizarse solo si corresponde (o mantenerlo)
        # Si no cambian productos, mantener el total que ya tiene la venta

        venta.save()

    return redirect('SaleList')


@login_required
def sale_delete(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        venta.delete()
    return redirect('SaleList')

@login_required
def sale_update_products(request, sale_id):
    venta = get_object_or_404(Venta, id=sale_id)

    try:
        productos_ids_raw = request.POST.getlist('producto[]')
        cantidades_raw = request.POST.getlist('cantidad[]')
        subtotales_raw = request.POST.getlist('subtotal[]')

        # Validación básica
        if not productos_ids_raw or not cantidades_raw or not subtotales_raw:
            messages.error(request, "Datos de productos incompletos.")
            return redirect('SaleList')

        if len(productos_ids_raw) != len(cantidades_raw) or len(productos_ids_raw) != len(subtotales_raw):
            messages.error(request, "Cantidad de datos inconsistentes.")
            return redirect('SaleList')

        try:
            productos_ids = [int(pid) for pid in productos_ids_raw]
            cantidades = [int(c) for c in cantidades_raw]
            subtotales = [Decimal(s) for s in subtotales_raw]
        except ValueError:
            messages.error(request, "Formato inválido en productos, cantidades o subtotales.")
            return redirect('SaleList')

        # 🔥 PASO 1: VALIDAR STOCK ANTES DE MODIFICAR NADA
        # Primero calculamos el stock disponible considerando lo que ya está en la venta
        detalles_actuales = list(venta.detalles.all())  # Convertir a lista para evitar problemas
        
        for i in range(len(productos_ids)):
            producto = get_object_or_404(Producto, id=productos_ids[i])
            nueva_cantidad = cantidades[i]
            
            # Buscar si este producto ya estaba en la venta anterior
            cantidad_anterior = 0
            for detalle in detalles_actuales:
                if detalle.producto_id == productos_ids[i]:
                    cantidad_anterior = detalle.cantidad
                    break
            
            # Stock disponible = stock actual + lo que teníamos reservado antes
            stock_disponible = producto.stock_inicial + cantidad_anterior
            
            if stock_disponible < nueva_cantidad:
                messages.error(request, 
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Cantidad solicitada: {nueva_cantidad}, "
                    f"Stock disponible: {stock_disponible} "
                    f"(actual: {producto.stock_inicial} + en venta anterior: {cantidad_anterior})")
                return redirect('SaleList')

        # 🔥 PASO 2: SI LLEGAMOS AQUÍ, TODO ESTÁ OK - AHORA SÍ MODIFICAMOS
        
        # Revertir stock anterior
        for detalle in detalles_actuales:
            detalle.producto.stock_inicial += detalle.cantidad
            detalle.producto.save()

        # Borrar detalles anteriores
        venta.detalles.all().delete()

        # Crear nuevos detalles
        total_venta = Decimal('0.00')

        for i in range(len(productos_ids)):
            producto = get_object_or_404(Producto, id=productos_ids[i])
            
            # Descontar nuevo stock
            producto.stock_inicial -= cantidades[i]
            producto.save()

            precio_unitario = subtotales[i] / cantidades[i] if cantidades[i] else Decimal('0.00')

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidades[i],
                precio_unitario=precio_unitario
            )

            total_venta += subtotales[i]

        venta.total = total_venta
        venta.save()

        messages.success(request, "Productos de la venta actualizados correctamente.")
        
    except Exception as e:
        messages.error(request, f"Error al actualizar venta: {e}")

    return redirect('SaleList')
