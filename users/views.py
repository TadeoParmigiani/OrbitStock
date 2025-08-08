from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from users.decorators import role_required

from .models import CustomUser


User = get_user_model()


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['username'] = user.username
            return redirect('HomeList') 
        else:
            messages.error(request, 'Credenciales incorrectas')
            return render(request, 'login.html', {})
    return render(request, 'login.html', {})



def logoutView(request):
    logout(request)
    return redirect('login')


@role_required('admin')
def userList(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'users.html', {'users': users})

@role_required('admin')
def userCreate(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password) 
                user.role = role
                user.save()
                messages.success(request, 'Usuario creado exitosamente')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {e}')
    return redirect('userList')

@role_required('admin')
def userUpdate(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')  

        if not user_id:
            messages.error(request, 'El ID del usuario es obligatorio')
            return redirect('userList')

        try:
            user = User.objects.get(id=user_id)
            user.username = username
            user.email = email

            if password:
                user.set_password(password)

            user.role = role
            user.save()
            
            messages.success(request, 'Usuario actualizado exitosamente')
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe')
        except Exception as e:
           
            messages.error(request, f'Ocurrió un error: {e}')

    return redirect('userList')


@role_required('admin')
def userDelete(request):
    if request.method == 'POST':
        user_id = request.POST['id']
        users_count = User.objects.filter(is_active=True).count()
        if users_count > 1:
            try:
                user = User.objects.get(id=user_id)
                user.is_active = False
                user.save()
                messages.success(request, 'Usuario eliminado exitosamente')
            except User.DoesNotExist:
                messages.error(request, 'El usuario no existe')
        else:
            messages.error(request, 'No se puede eliminar el único usuario activo restante')
    return redirect('userList')

