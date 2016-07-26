from django.contrib.auth.models import User


class SamlBackend(object):

    def authenticate(self, saml_auth=None):
        username = saml_auth.get_nameid()
        user, _ = User.objects.get_or_create(username=username)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
