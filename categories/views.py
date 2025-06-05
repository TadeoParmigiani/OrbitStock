from django.shortcuts import render, redirect, get_object_or_404
from .models import Categoria
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def categoryList(request):
    categorias = Categoria.objects.all()
    return render(request, 'categories.html', {'categorias': categorias})

@login_required
def categoryCreate(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre)
            messages.success(request, 'Categoría creada con éxito.')
        else:
            messages.error(request, 'El nombre de la categoría no puede estar vacío.')
    return redirect('categoryList')


@login_required
def categoryUpdate(request):
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, id=request.POST.get('id'))
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            categoria.nombre = nombre
            try:
                categoria.save()
                messages.success(request, 'Categoría actualizada.')
            except Exception as e:
                messages.error(request, f'Error al guardar la categoría: {str(e)}')
        else:
            messages.error(request, 'El nombre no puede estar vacío.')
    return redirect('categoryList')

@login_required
def categoryDelete(request):
    if request.method == 'POST':
        categoria = get_object_or_404(Categoria, id=request.POST.get('id'))
        categoria.delete()
        messages.success(request, 'Categoría eliminada.')
    return redirect('categoryList')