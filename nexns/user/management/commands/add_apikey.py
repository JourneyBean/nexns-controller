import os
import base64
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import UserApiKey
from ...lib.scope import ApiKeyScope


class Command(BaseCommand):
    help = "Add a temporary apikey for user."

    def handle(self, *args, **options):
        user_id = input("Please enter user id: ")
        user = User.objects.get(id=user_id)

        api_name = input("Please enter api key's name: ")

        scope = ApiKeyScope()
        scope.can_read_domains = True
        scope.can_create_domains = True
        scope.can_modify_domains = True
        scope.can_delete_domains = True
        scope.can_read_variables = True
        scope.can_create_variables = True
        scope.can_modify_variables = True
        scope.can_delete_variables = True

        apikey = UserApiKey()
        apikey.name = api_name
        apikey.user = user
        apikey.scope = scope.__dict__
        apikey.expires_at = datetime.datetime.now(tz=datetime.datetime.now().astimezone().tzinfo) + datetime.timedelta(hours=1)
        apikey.secret = base64.urlsafe_b64encode(os.urandom(32)).decode()
        apikey.save()

        print(f"Successfully created api key for user {user.email}(id={user.id})")
        print(f"API Key Secret: {apikey.secret}")
        print(f"You can use X-APIKEY header to authenticate.")
