from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import login as auth_login
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework import viewsets, response, decorators, serializers, permissions, status

from apps.realme.views import login as realme_login
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
        user_data['profile'] = ProfileSerializer(user.profile, context={'request': request}).data
        return response.Response(user_data)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.Profile
        fields = ('url', 'subscribed')


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Return a list of profiles.
    """
    queryset = m.Profile.objects.none()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return m.Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PreferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.Preference
        fields = ('url', 'group', 'key', 'val')
        extra_kwargs = {
            'val': {'required': True, 'allow_blank': True},
        }

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
    Return a list of preferences for current user.

    Only ower has access to this API.
    And, owner can post data to update or create new preferences for himself.

    Note, there is no need to pass user in data, it defaults to current user.

    Post data in single mode:

        POST /api/preferences/

        {'group': 'settings', 'key': 'key0', 'val': 'val0'}

    Post data in bulk mode:

        POST /api/preferences/

        [
            {'group': 'settings', 'key': 'key0', 'val': 'val0'},
            {'group': 'settings', 'key': 'key1', 'val': 'val1'}
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


class EmailAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.EmailAddress
        fields = ('url', 'email', 'created_at')


class EmailAddressViewSet(viewsets.ModelViewSet):
    """
    Return a list of pending email address for current user.
    """
    queryset = m.EmailAddress.objects.none()
    serializer_class = EmailAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return m.EmailAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        obj = serializer.save(user=self.request.user)
        # TODO: celery task?
        obj.send_confirm_email()


def login_router(request):
    BUNDLE_NAME = getattr(settings, 'BUNDLE_NAME', 'FAKE')
    log.info('current BUNDLE_NAME: {}'.format(BUNDLE_NAME))
    if BUNDLE_NAME in settings.BUNDLES:
        return realme_login(request)
    else:
        return auth_login(request)


def unsubscribe(request, user_id, token):

    # it can be different from current user
    target_user = get_object_or_404(
        User,
        id=user_id,
        is_active=True
    )
    message = ''
    try:
        key = '{}:{}'.format(user_id, token)
        # Valid for 7 days, move to settings when necessary.
        TimestampSigner().unsign(key, max_age=60 * 60 * 24 * 7)
    except SignatureExpired:
        # note: this must be before BadSignature
        # otherwise the code will always catch BadSignature exception.
        # since SignatureExpired is subclass of BadSignature
        message = 'Unsubscribe token expired'
    except BadSignature:
        message = 'Invalid unsubscribe token'
    except Exception as e:
        message = 'Unknown unsubscribe error'

    if message:
        return render(
            request,
            'accounts/message.html',
            context={
                'title': 'Unsubscribe failed.',
                'lines': [message],
            }
        )
    else:
        m.Profile.objects.filter(user_id=user_id).update(subscribed=False)
        return render(
            request,
            'accounts/unsubscribed.html',
            context={'user': target_user}
        )


def confirm(request, uuid):
    obj = get_object_or_404(m.EmailAddress, pk=uuid)
    obj.confirm()
    lines = [
        '{} has been signed-up to SmartStart To Do list reminders.'.format(obj.email),
        'You can unsubscribe at any time from your SmartStart profile or the reminder emails.',
    ]
    return render(
        request,
        'accounts/message.html',
        context={
            'title': 'Sign-up confirmed.',
            'lines': lines,
        }
    )
