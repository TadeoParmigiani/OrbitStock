"""
URL configuration for SistemaStock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from users import views as users_views
from index import views as index_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
     path('admin/', admin.site.urls),
     path('sales/', include('sales.urls')),
     path('backup/', include('backup.urls')),
#     path('reports/', include('reports.urls')),
     path('products/', include('products.urls')),
     path('customers/', include('customers.urls')),
     path('categories/', include('categories.urls')),
     path('users/', include('users.urls')),
     path('', users_views.login, name='login'),
     path('index', index_views.index, name='index'),
     path('calendar/', include('event_calendar.urls')),
     path('home/', include('home.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
