# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.request_cache.models import RequestCache


def ckan_result_response(name):
    result = RequestCache.objects.filter(name=name).first()
    if result:
        return Response(result.get_result())
    else:
        return Response({"error": "This endpoint is not configured."})


@api_view()
def lbs_parenting_support(request):
    return ckan_result_response('lbs_parenting_support')


@api_view()
def lbs_early_education(request):
    return ckan_result_response('lbs_early_education')


@api_view()
def lbs_breastfeeding(request):
    return ckan_result_response('lbs_breastfeeding')


@api_view()
def lbs_antenatal(request):
    return ckan_result_response('lbs_antenatal')


@api_view()
def lbs_mental_health(request):
    return ckan_result_response('lbs_mental_health')


@api_view()
def lbs_budgeting(request):
    return ckan_result_response('lbs_budgeting')


@api_view()
def lbs_well_child(request):
    return ckan_result_response('lbs_well_child')


@api_view()
def content_timeline(request):
    # DIA are whitelisting this API by user agent.
    result = RequestCache.objects.filter(name='content_timeline').first()
    if result:
        return Response(result.get_result())
    else:
        return Response({"error": "This endpoint is not configured."})
