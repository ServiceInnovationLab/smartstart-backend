from django.conf.urls import url
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    url(r'^notification/(?P<id>\d+)/$', views.notification_detail, name='notification_detail'),
]
