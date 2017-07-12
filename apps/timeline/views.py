from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import HyperlinkedModelSerializer

from apps.base.permissions import ReadOnly
from apps.timeline.models import PhaseMetadata, Notification

# Serializers define the API representation.
class PhaseMetadataSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = PhaseMetadata
        fields = ('id', 'weeks_start', 'weeks_finish')

class PhaseMetadataViewSet(ReadOnlyModelViewSet):
    queryset = PhaseMetadata.objects.all()
    serializer_class = PhaseMetadataSerializer
    permission_classes = [ReadOnly]


def notification_detail(request, id):
    obj = get_object_or_404(Notification, id=id)
    return HttpResponse(obj.render_email_template())
