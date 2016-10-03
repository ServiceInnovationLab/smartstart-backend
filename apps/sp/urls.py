from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^metadata/$', views.metadata, name='sp_metadata'),
    url(r'^login/$', views.login, name='sp_login'),
    url(r'^acs/$', views.assertion_consumer_service, name='sp_acs'),
    url(r'^seamless/(?P<target_sp>\w+)/$', views.seamless, name='seamless'),
    # url(r'^logout/$', views.logout, name='sp_logout'),
    # url(r'^ls/$', views.logout_service, name='sp_ls'),
    # url(r'^ls/post/$', views.logout_service_post, name='sp_ls_post'),
]
