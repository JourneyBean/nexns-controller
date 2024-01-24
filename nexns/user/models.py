from django.db import models
from django.contrib.auth.models import User


class UserApiKey(models.Model):
    name = models.CharField(max_length=1024, null=False, blank=False)
    user = models.ForeignKey(User, related_name='apikeys', on_delete=models.CASCADE)
    scope = models.JSONField()
    expires_at = models.DateTimeField(null=False, blank=False)
    secret = models.CharField(max_length=8192, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
