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
import nexns.user.views as user_views
import nexns.name.views as name_views
import nexns.client.views as client_views
import nexns.variable.views as variable_views

router = routers.DefaultRouter()

router.register(r'status', main_views.StatusView, basename='status')
router.register(r'current-user', user_views.CurrentUserView, basename='current_user')
router.register(r'csrf-token', user_views.CsrfTokenView, basename='csrf_token')
router.register(r'domain', name_views.DomainView)
router.register(r'zone', name_views.ZoneView)
router.register(r'rrset', name_views.RRsetView)
router.register(r'record', name_views.RecordDataView)
router.register(r'dump', name_views.DumpView, basename='dump')
router.register(r'variable', variable_views.VariableView)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/', include(router.urls)),
    path(r'api/v1/zone-update/', name_views.ZoneUpdateView.as_view(), name='zone-update'),
    path(r'api/v1/rrsets-update/', name_views.RRsetUpdateView.as_view(), name='rrsets-update'),
    path(r'api/v1/record-quick-update/', name_views.RecordQuickUpdateView.as_view({'get': 'retrieve', 'put': 'update'}), name='record-update-retrieve'),
]
