from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.eventList, name='eventList'),     
    path('eventos/', views.eventos_arrastrables, name='draggable_events'),  # solo eventos plantilla
    path('eventos_calendario/', views.eventos_calendario, name='eventos_calendario'),  # eventos con fecha
    path('new/', views.eventCreate, name='eventCreate'),        
    path('delete/', views.eventDelete, name='eventDelete'),
]
