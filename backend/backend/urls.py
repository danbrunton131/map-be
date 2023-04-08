"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
        https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include

from django.views.generic import TemplateView

from map_backend.views import Load, LoadView, ImportView, Import

urlpatterns = [
    path('admin/importer/', ImportView.as_view()),
    path('admin/importer/Import', Import.as_view()),
    path('admin/loader/', LoadView.as_view()),
    path('admin/loader/Load', Load.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include('map_backend.urls')),
]
