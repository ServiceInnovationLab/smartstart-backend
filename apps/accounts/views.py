from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
from django.contrib.auth.views import login as auth_login
from apps.sp.views import login as sp_login


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
    auth_method = getattr(settings, 'AUTH_METHOD', 'fake')
    if auth_method == 'fake':
        return auth_login(request)
    elif auth_method == 'sp':
        return sp_login(request)
