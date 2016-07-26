"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.views.generic import RedirectView

from rest_framework import routers
from apps.accounts import views as accounts_views

router = routers.DefaultRouter()
router.register(r'users', accounts_views.UserViewSet)

urlpatterns = [
    url(r'', include('apps.accounts.urls')),
    url(r'', include('apps.accounts.urls', namespace='rest_framework')),
    url(r'^sp/', include('apps.sp.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^$', RedirectView.as_view(pattern_name='api-root')),
]
