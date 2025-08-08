from django.urls import path
from . import views

# urlpatterns = [
#     path('list/', views.eventList, name='eventList'),     
#     path('eventos/', views.eventos_arrastrables, name='draggable_events'),  # solo eventos plantilla
#     path('eventos_calendario/', views.eventos_calendario, name='eventos_calendario'),  # eventos con fecha
#     path('new/', views.eventCreate, name='eventCreate'),        
#     path('delete/', views.eventDelete, name='eventDelete'),
# ]
urlpatterns = [
    path('list/', views.eventList, name='calendar'),
    path('events/', views.eventos_calendario, name='eventos_calendario'),
    path('new/', views.eventCreate, name='event_create'),
    path('delete/', views.eventDelete, name='event_delete'),
    path('update/', views.eventUpdate, name='event_update'),

]