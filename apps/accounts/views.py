from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login
from rest_framework import viewsets, response, decorators, serializers, permissions

from apps.sp.views import login as sp_login
from . import models as m

import logging
log = logging.getLogger(__name__)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """Owner only and ReadOnly"""
        user = request.user
        profile = user.profile
        user_serializer = self.serializer_class(user, context={'request': request})
        user_data = user_serializer.data
        user_data['preferences'] = profile.dump_preferences()
        return response.Response(user_data)


class PreferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.Preference
        fields = ('url', 'group', 'key', 'val')


class PreferenceViewSet(viewsets.ModelViewSet):
    """Ower Only full access"""
    queryset = m.Preference.objects.none()
    serializer_class = PreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return m.Preference.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



def login_router(request):
    BUNDLE_NAME = getattr(settings, 'BUNDLE_NAME', 'FAKE')
    log.info('current BUNDLE_NAME: {}'.format(BUNDLE_NAME))
    if BUNDLE_NAME in settings.BUNDLES:
        return sp_login(request)
    else:
        return auth_login(request)
