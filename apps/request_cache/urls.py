from django.conf.urls import url
from apps.request_cache import views


urlpatterns = [
    url(r'^service-locations/parenting-support/?$', views.lbs_parenting_support, name='lbs_parenting_support'),
    url(r'^service-locations/early-education/?$', views.lbs_early_education, name='lbs_early_education'),
    url(r'^service-locations/breastfeeding/?$', views.lbs_breastfeeding, name='lbs_breastfeeding'),
    url(r'^service-locations/antenatal/?$', views.lbs_antenatal, name='lbs_antenatal'),
    url(r'^service-locations/mental-health/?$', views.lbs_mental_health, name='lbs_mental_health'),
    url(r'^service-locations/budgeting/?$', views.lbs_budgeting, name='lbs_budgeting'),
    url(r'^service-locations/well-child/?$', views.lbs_well_child, name='lbs_well_child'),
    url(r'^content/timeline/?$', views.content_timeline, name='content_timeline'),
]
