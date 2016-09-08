from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import HyperlinkedModelSerializer
from apps.base.permissions import ReadOnly
from apps.timeline.models import PhaseMetadata

# Serializers define the API representation.
class PhaseMetadataSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = PhaseMetadata
        fields = ('id', 'weeks_start', 'weeks_finish')

class PhaseMetadataViewSet(ReadOnlyModelViewSet):
    queryset = PhaseMetadata.objects.all()
    serializer_class = PhaseMetadataSerializer
    permission_classes = [ReadOnly]
