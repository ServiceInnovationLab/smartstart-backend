from django.conf import settings
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.views import login as auth_login
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework import viewsets, response, decorators, serializers, permissions, status

from apps.realme.views import login as realme_login
from apps.accounts.models import UserProxy, BroForm
from apps.accounts.authentication import AnonymousSessionAuthentication
from utils import set_exchange_cookie
from . import models as m

import json
import logging
log = logging.getLogger(__name__)

SESSION_API_NAMESPACE = 'bro'
BRO_FORM_SESSION_KEY = 'bro-form'


class SessionViewSet(viewsets.ViewSet):

    # just a placeholder to remove error
    queryset = Session.objects.none()

    http_method_names = ['get', 'put']
    permission_classes = [permissions.AllowAny]
    authentication_classes = [AnonymousSessionAuthentication]

    def list(self, request):
        # we don't list anything
        data = request.session.get(SESSION_API_NAMESPACE, {})
        return response.Response(data)

    def retrieve(self, request, pk=None):
        session = request.session.get(SESSION_API_NAMESPACE, {})
        data = session.get(pk, {})
        return response.Response(data)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        session = request.session.get(SESSION_API_NAMESPACE, {})
        session[pk] = request.data
        request.session[SESSION_API_NAMESPACE] = session

        return response.Response(request.data)


class BroFormViewSet(viewsets.ViewSet):
    """
    This ViewSet handles saving the BRO (Birth Registration Online) form data,
    both for anonymous users by storing it in the Django session, and for
    authenticated users by storing it in the database. Form data is saved as
    arbitrary JSON, and we bend the usage of ViewSets a bit by using a constant
    pk of 'data' for the item level retrieve and update end points. The list end
    point returns nothing. The end points are:

    - ``/api/bro-form/``: GET list, returns empty JSON.
    - ``/api/bro-form/data/``: GET and PUT here to fetch and save BRO form data.
    """
    queryset = m.BroForm.objects.none()
    http_method_names = ['get', 'put']
    permission_classes = [permissions.AllowAny]
    authentication_classes = [AnonymousSessionAuthentication]

    def list(self, request):
        """
        Dummy list end point, returns empty JSON.
        """
        return response.Response({})

    def retrieve(self, request, pk=None):
        """
        Fetch BRO form data for the current session. This data comes from the
        session if the user is anonymous, and the database if authenticated.
        Ignore pk, it should always have a dummy value of 'data' since we're
        using a session key or the user id for separation of data concerns.
        Make a GET request to the ``/api/bro-form/data/`` end point.
        """
        if request.user.is_authenticated():
            bro = m.BroForm.objects.filter(user=request.user).first()
            data = json.loads(bro.form_data or '{}') if bro else {}
        else:
            data = request.session.get(BRO_FORM_SESSION_KEY, {})
        return response.Response(data)

    def update(self, request, *args, **kwargs):
        """
        Save BRO form data for the current session. This data saves to the
        session if the user is anonymous, and the database if authenticated.
        Ignore pk, it should always have a dummy value of 'data' since we're
        using a session key or the user id for separation of data concerns.
        Make a PUT request to the ``/api/bro-form/data/`` end point, with the
        form data in the request body as JSON.
        """
        # Save BRO to the database if authenticated.
        if request.user.is_authenticated():
            (bro, _) = BroForm.objects.get_or_create(user=request.user)
            bro.form_data = json.dumps(request.data)
            bro.save()
        request.session[BRO_FORM_SESSION_KEY] = request.data
        return response.Response(request.data)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProxy
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Return a list of users.

    For permission issue, we only return current logged in user in the list.
    An extra endpoint is added to return user profile at `/api/users/me/`

    """
    queryset = UserProxy.objects.none()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProxy.objects.filter(id=self.request.user.id)

    @decorators.list_route(methods=['get'])
    def me(self, request):
        """Owner only and ReadOnly"""
        user = UserProxy.objects.get(id=request.user.id)
        user_serializer = self.serializer_class(user, context={'request': request})
        user_data = user_serializer.data
        user_data['preferences'] = user.dump_preferences()
        return response.Response(user_data)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.Profile
        fields = ('url', 'subscribed', 'due_date')


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Return a list of profiles.
    """
    queryset = m.Profile.objects.none()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']

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

    def create(self, validated_data):
        obj, created = self.Meta.model.objects.get_or_create(**validated_data)
        if obj.has_email_changed:  # TODO: check created? not sure.
            obj.send_confirm_email()
        return obj


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


def login_router(request):
    BUNDLE_NAME = getattr(settings, 'BUNDLE_NAME', 'FAKE')
    log.info('current BUNDLE_NAME: {}'.format(BUNDLE_NAME))
    if BUNDLE_NAME in settings.BUNDLES:
        return realme_login(request)
    else:
        return auth_login(request)


def unsubscribe(request, token):

    message = ''
    try:
        # Valid for 7 days, move to settings when necessary.
        TimestampSigner().unsign(token, max_age=60 * 60 * 24 * 7)
    except SignatureExpired:
        # note: this must be before BadSignature
        # otherwise the code will always catch BadSignature exception.
        # since SignatureExpired is subclass of BadSignature
        message = 'unsubscribe_token_expired'
    except BadSignature:
        message = 'unsubscribe_token_invalid'
    except Exception:
        message = 'unsubscribe_token_unknown_error'

    if message:
        # set cookie and redirect to homepage to display error
        set_exchange_cookie(message)
        return redirect('/')
    else:
        # it can be different from current user
        user_id = token.split(':')[0]
        target_user = get_object_or_404(
            UserProxy,
            id=user_id,
            is_active=True
        )
        target_user.unsubscribe()
        return redirect('/unsubscribed.html')


def confirm(request, uuid):
    obj = get_object_or_404(m.EmailAddress, pk=uuid)
    obj.confirm()
    return redirect('/signup-confirmed.html')
