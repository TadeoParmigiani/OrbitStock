from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name='login'),
    path('logout', views.logoutView, name='logout'),
    path('list', views.userList, name='userList'),
    path('new', views.userCreate, name='userCreate'),
    path('edit/', views.userUpdate, name='userUpdate'),
    path('delete/', views.userDelete, name='userDelete'),
]