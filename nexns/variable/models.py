from django.db import models
from django.contrib.auth.models import User


class Variable(models.Model):
    user = models.ForeignKey(User, related_name='variables', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    text = models.CharField(max_length=300, blank=True)
    val = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
