from django.contrib.auth.models import User


class SamlBackend(object):

    def authenticate(self, saml2_auth=None):
        username = saml2_auth.get_nameid()
        # TODO: save attrs to user
        # attrs = auth.get_attributes()
        user, _ = User.objects.get_or_create(username=username)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
