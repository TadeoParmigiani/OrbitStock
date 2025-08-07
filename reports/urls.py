from django.urls import path
from . import views

urlpatterns = [
    path('reportes/<str:tipo>/', views.reports_list, name='reportsList'),
    path('create/', views.create_report, name='create_report'),
    path('download/<int:report_id>/', views.download_report, name='download_report'),
    path('preview/<int:report_id>/', views.preview_report, name='preview_report'),
    path('delete/', views.delete_report, name='delete_report'),
]