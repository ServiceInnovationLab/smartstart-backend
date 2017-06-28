from django.conf.urls import url
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    url(r'^login/$', views.login_router, name='login'),
    url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
    url(r'^unsubscribe/(?P<user_id>\d+)/(?P<token>[\w.:\-_=]+)/$', views.unsubscribe, name='unsubscribe'),
    url(r'^confirm/(?P<uuid>[-\w]+)/$', views.confirm, name='confirm'),
]
