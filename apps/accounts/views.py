from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login
from rest_framework import viewsets, response, decorators, serializers, permissions, status

from apps.sp.views import login as sp_login
from . import models as m

import logging
log = logging.getLogger(__name__)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Return a list of users.

    For permission issue, we only return current logged in user in the list.
    An extra endpoint is added to return user profile at `/api/users/me/`

    """
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

    def create(self, validated_data):
        obj, _ = m.Preference.objects.update_or_create(
            user=validated_data['user'],
            group=validated_data['group'],
            key=validated_data['key'],
            defaults={
                'val': validated_data['val']
            }
        )
        return obj


class PreferenceViewSet(viewsets.ModelViewSet):
    """
    Return a list of prefrences for current user.

    Only ower has access to this API.
    And, owner can post data to update or create new preferences for himself.
    Note, there is no need to pass user in data, it defaults to current user.

    Post data in single mode:

        POST /api/preferences/

        {'group': 'settings', 'key0': 'val0'}

    Post data in bulk mode:

        POST /api/preferences/

        [
            {'group': 'settings', 'key': 'key0', 'val': 'val0'},
            {'group': 'settings', 'key': 'key1', 'val': 'val1'},
        ]

    """
    queryset = m.Preference.objects.none()
    serializer_class = PreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return m.Preference.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        is_list = type(data) is list
        serializer = self.get_serializer(data=data, many=is_list)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def login_router(request):
    BUNDLE_NAME = getattr(settings, 'BUNDLE_NAME', 'FAKE')
    log.info('current BUNDLE_NAME: {}'.format(BUNDLE_NAME))
    if BUNDLE_NAME in settings.BUNDLES:
        return sp_login(request)
    else:
        return auth_login(request)
