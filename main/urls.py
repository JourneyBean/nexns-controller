"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from . import views as main_views
import mewwoof_name_service.user.views as user_views
import mewwoof_name_service.name.views as name_views

router = routers.DefaultRouter()

router.register(r'status', main_views.StatusView, basename='status')
router.register(r'user', user_views.UserView)
router.register(r'domain', name_views.DomainView)
router.register(r'zone', name_views.ZoneView)
router.register(r'record', name_views.RecordView)
router.register(r'dump', name_views.DumpView, basename='dump')

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls))
]
