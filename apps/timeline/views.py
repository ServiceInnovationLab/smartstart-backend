from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import HyperlinkedModelSerializer

from apps.base.permissions import ReadOnly
from apps.timeline.models import PhaseMetadata, Notification


# Serializers define the API representation.
class PhaseMetadataSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = PhaseMetadata
        fields = ('id', 'weeks_start', 'weeks_finish')


@method_decorator(ensure_csrf_cookie, name='dispatch')
class PhaseMetadataViewSet(ReadOnlyModelViewSet):
    queryset = PhaseMetadata.objects.all()
    serializer_class = PhaseMetadataSerializer
    permission_classes = [ReadOnly]


def notification_detail(request, id):
    obj = get_object_or_404(Notification, id=id)
    return HttpResponse(obj.render_email_template())
