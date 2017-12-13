from django.conf.urls import url
from apps.timeline import views

urlpatterns = [
    url(r'^notification/(?P<id>\d+)/$', views.notification_detail, name='notification_detail'),
]
