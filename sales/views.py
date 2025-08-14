from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Venta, DetalleVenta
from products.models import Producto
from customers.models import Cliente
from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse

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

    if request.method != 'POST':
        return redirect('SaleList')

    try:
        productos_ids_raw = request.POST.getlist('producto[]')
        cantidades_raw = request.POST.getlist('cantidad[]')
        
        print("DEBUG - Datos recibidos:")
        print(f"productos_ids_raw: {productos_ids_raw}")
        print(f"cantidades_raw: {cantidades_raw}")
        
        # Validación básica
        if not productos_ids_raw or not cantidades_raw:
            messages.error(request, "Datos de productos incompletos.")
            return redirect('SaleList')

        if len(productos_ids_raw) != len(cantidades_raw):
            messages.error(request, "Cantidad de datos inconsistentes.")
            return redirect('SaleList')

        try:
            productos_ids = [int(pid) for pid in productos_ids_raw if pid.strip()]
            cantidades = [int(c) for c in cantidades_raw if c.strip()]
        except ValueError as e:
            messages.error(request, f"Formato inválido en productos o cantidades: {e}")
            return redirect('SaleList')

        # Verificar que las listas tengan el mismo tamaño después de la conversión
        if len(productos_ids) != len(cantidades):
            messages.error(request, "Error en el procesamiento de datos.")
            return redirect('SaleList')

        
        detalles_actuales = list(venta.detalles.all())
        
        for i in range(len(productos_ids)):
            try:
                producto = get_object_or_404(Producto, id=productos_ids[i])
                nueva_cantidad = cantidades[i]
                
                # Buscar cantidad anterior para este producto
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
                        f"Stock disponible: {stock_disponible}")
                    return redirect('SaleList')
                    
            except Exception as e:
                messages.error(request, f"Error validando producto {productos_ids[i]}: {e}")
                return redirect('SaleList')

        # REVERTIR STOCK ANTERIOR
        for detalle in detalles_actuales:
            try:
                detalle.producto.stock_inicial += detalle.cantidad
                detalle.producto.save()
                print(f"DEBUG - Revirtiendo stock: {detalle.producto.nombre} +{detalle.cantidad}")
            except Exception as e:
                print(f"ERROR revirtiendo stock: {e}")

        # Borrar detalles anteriores
        venta.detalles.all().delete()

        #CREAR NUEVOS DETALLES Y DESCONTAR STOCK
        total_venta = Decimal('0.00')

        for i in range(len(productos_ids)):
            try:
                producto = get_object_or_404(Producto, id=productos_ids[i])
                cantidad = cantidades[i]
                
                # Usar el precio actual del producto (podrías cambiarlo por precio histórico si lo prefieres)
                precio_unitario = producto.precio_venta
                subtotal = precio_unitario * cantidad
                
                # Crear detalle
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario
                )
                
                # Descontar stock
                producto.stock_inicial -= cantidad
                producto.save()
                
                total_venta += subtotal
                
                print(f"DEBUG - Producto procesado: {producto.nombre}, cantidad: {cantidad}, subtotal: {subtotal}")
                
            except Exception as e:
                messages.error(request, f"Error procesando producto {productos_ids[i]}: {e}")
                return redirect('SaleList')

        #ACTUALIZAR TOTAL DE LA VENTA
        venta.total = total_venta
        venta.save()
        
        print(f"DEBUG - Total venta actualizado: {total_venta}")

        messages.success(request, f"Productos actualizados correctamente. Nuevo total: ${total_venta}")
        
    except Exception as e:
        messages.error(request, f"Error inesperado al actualizar venta: {e}")
        print(f"ERROR GENERAL: {e}")

    return redirect('SaleList')


@login_required
def get_sale_products(request, sale_id):
    """Vista para obtener los productos de una venta específica vía AJAX"""
    try:
        venta = get_object_or_404(Venta, id=sale_id)
        
        # Intentar ambas formas de obtener los detalles
        try:
            
            detalles = venta.detalles.all()
            print(f"DEBUG - Usando venta.detalles.all(): {detalles.count()} detalles")
        except AttributeError:
            
            detalles = DetalleVenta.objects.filter(venta=venta)
            print(f"DEBUG - Usando filtro directo: {detalles.count()} detalles")
        
        # Debug adicional
        print(f"DEBUG - Venta ID: {sale_id}")
        print(f"DEBUG - Venta encontrada: {venta}")
        print(f"DEBUG - Total venta: {venta.total}")
        
        productos_data = []
        for detalle in detalles:
            print(f"DEBUG - Detalle: {detalle.producto.nombre}, cantidad: {detalle.cantidad}")
            productos_data.append({
                'id': detalle.producto.id,
                'nombre': detalle.producto.nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario': float(detalle.precio_unitario),
                'subtotal': float(detalle.cantidad * detalle.precio_unitario)
            })
        
        print(f"DEBUG - Productos data final: {productos_data}")
        
        return JsonResponse({
            'success': True,
            'productos': productos_data,
            'total': float(venta.total)
        })
        
    except Exception as e:
        print(f"ERROR en get_sale_products: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        })