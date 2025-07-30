from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente

# LISTAR CLIENTES
def clientList(request):
    clientes = Cliente.objects.all()
    return render(request, 'customers.html', {'clientes': clientes})


# CREAR CLIENTE
def clientCreate(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        dni_cuit = request.POST.get('dni_cuit')
        telefono = request.POST.get('telefono')
        correo_electronico = request.POST.get('correo_electronico')
        direccion = request.POST.get('direccion')

        if nombre:
            Cliente.objects.create(
                nombre=nombre,
                dni_cuit=dni_cuit,
                telefono=telefono,
                correo_electronico=correo_electronico,
                direccion=direccion
            )
            messages.success(request, 'Cliente creado exitosamente.')
        else:
            messages.error(request, 'El nombre es obligatorio.')

    return redirect('clientList')


# EDITAR CLIENTE
def clientUpdate(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('id')
        cliente = get_object_or_404(Cliente, id=cliente_id)

        cliente.nombre = request.POST.get('nombre')
        cliente.dni_cuit = request.POST.get('dni_cuit')
        cliente.telefono = request.POST.get('telefono')
        cliente.correo_electronico = request.POST.get('correo_electronico')
        cliente.direccion = request.POST.get('direccion')
        cliente.save()

        messages.success(request, 'Cliente actualizado exitosamente.')

    return redirect('clientList')


# ELIMINAR CLIENTE
def clientDelete(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('id')
        cliente = get_object_or_404(Cliente, id=cliente_id)
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente.')

    return redirect('clientList')
