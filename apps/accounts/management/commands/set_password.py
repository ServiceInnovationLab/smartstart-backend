from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

UserModel = get_user_model()


class Command(BaseCommand):
    requires_migrations_checks = True
    requires_system_checks = False

    help = """Set a user password. This command is for scripting and deployment
purposes only; running this from a command line is inadvisable since it
will introduce plain-text passwords into the shell history."""

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username to change password for.')
        parser.add_argument('password', help='Password to set.')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        try:
            u = UserModel.objects.get(**{UserModel.USERNAME_FIELD: username})
        except UserModel.DoesNotExist:
            raise CommandError("User {} not found.".format(username))

        u.set_password(password)
        u.save()
        return "Password changed successfully for user '{}'".format(u)
