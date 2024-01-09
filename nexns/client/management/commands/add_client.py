import os
import base64
from django.core.management.base import BaseCommand
from nexns.client.models import Client


class Command(BaseCommand):
    help = "Add a client to database."

    def handle(self, *args, **options):
        name = input("Please enter client name (only for human): ")

        client = Client()
        client.name = name
        client.secret = base64.urlsafe_b64encode(os.urandom(32)).decode()
        client.save()
        
        print(f"Successfully created client {client.name}")
        print(f"Client UUID: {client.uuid}")
        print(f"Client Secret: {client.secret}")
