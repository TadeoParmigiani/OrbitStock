from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.backupList, name='backupList'),
    path('create/', views.create_backup, name='create_backup'),
    path('restore/', views.restore_backup, name='restore_backup'),
    path('download/<int:backup_id>/', views.download_backup, name='download_backup'),
    path('delete/', views.delete_backup, name='delete_backup'),
]