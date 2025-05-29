from django.shortcuts import render

from categories.models import Categoria
from django.contrib.auth.decorators import login_required


@login_required

def category(request):
    categories = Categoria.objects.all()
    return render(request, 'categories.html', {'categories': categories})