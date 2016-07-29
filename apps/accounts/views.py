from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from django.contrib.auth.views import login as auth_login
from apps.sp.views import login as sp_login
import logging
log = logging.getLogger(__name__)


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def login_router(request):
    IDP = getattr(settings, 'IDP', 'FAKE').upper()
    log.info('current IDP: {}'.format(IDP))
    if IDP in ('MTS', 'ITE', 'PRD'):
        return sp_login(request)
    else:
        return auth_login(request)
