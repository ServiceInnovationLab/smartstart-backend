from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import HyperlinkedModelSerializer
from apps.sp.views import login as sp_login
import logging
log = logging.getLogger(__name__)


# Serializers define the API representation.
class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


def login_router(request):
    BUNDLE_NAME = getattr(settings, 'BUNDLE_NAME', 'FAKE')
    log.info('current BUNDLE_NAME: {}'.format(BUNDLE_NAME))
    if BUNDLE_NAME in settings.BUNDLES:
        return sp_login(request)
    else:
        return auth_login(request)
