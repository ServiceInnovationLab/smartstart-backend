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
from apps.base import views as base_views
from apps.accounts import views as accounts_views
from apps.timeline import views as timeline_views


admin.site.site_title = 'SmartStart'
admin.site.site_header = 'SmartStart'

router = routers.DefaultRouter()
router.register(r'users', accounts_views.UserViewSet)
# router.register(r'profile', accounts_views.ProfileViewSet)
router.register(r'preferences', accounts_views.PreferenceViewSet)
router.register(r'emailaddresses', accounts_views.EmailAddressViewSet)
router.register(r'phase-metadata', timeline_views.PhaseMetadataViewSet)
router.register(r'sessions', accounts_views.SessionViewSet)
router.register(r'bro-form', accounts_views.BroFormViewSet)

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='api-root')),
    url(r'^make_live/(?P<site_hash>[a-z0-9]+)/$', base_views.make_live_view, name='make_live_view'),
    url(r'^realme/', include('apps.realme.urls', namespace='realme')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^api/request/', include('apps.request_cache.urls', namespace='request_cache')),
    url(r'^accounts/', include('apps.accounts.urls', namespace='accounts')),
    url(r'^timeline/', include('apps.timeline.urls', namespace='timeline')),
    url(r'', include('two_factor.urls', namespace='two_factor')),
    url(r'', include('apps.accounts.urls', namespace='rest_framework')),
]
