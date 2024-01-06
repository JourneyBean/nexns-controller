import getpass

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Add a user to database."

    def handle(self, *args, **options):
        username = input("Please enter username: ")
        is_superuser = input("Is superuser? [y/n]: ")
        email = input("Please input email: ")
        password = getpass.getpass("Please input password: ")

        user = User()
        user.username = username
        user.email = email
        user.set_password(password)
        user.is_superuser = is_superuser.lower() == "y"

        user.save()

        if user.is_superuser:
            print(f"Successfully created superuser {user.username}.")
        else:
            print(f"Successfully created user {user.username}.")
