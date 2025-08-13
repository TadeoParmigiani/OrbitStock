from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.eventList, name='calendar'),
    path('events/', views.eventos_calendario, name='eventos_calendario'),
    path('new/', views.eventCreate, name='event_create'),
    path('delete/', views.eventDelete, name='event_delete'),
    path('update/', views.eventUpdate, name='event_update'),

]