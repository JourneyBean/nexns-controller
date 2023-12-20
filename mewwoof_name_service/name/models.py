from django.db import models
from django.contrib.auth.models import User


class Domain(models.Model):
    user = models.ForeignKey(User, related_name='domains', on_delete=models.CASCADE)
    domain = models.CharField(max_length=300)
    desc = models.CharField(max_length=1000)
    mname = models.CharField(max_length=300)
    rname = models.CharField(max_length=300)
    serial = models.CharField(max_length=10)
    refresh = models.IntegerField()
    retry = models.IntegerField()
    expire = models.IntegerField()
    ttl = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Zone(models.Model):
    domain = models.ForeignKey(Domain, related_name='zones', on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    rules = models.JSONField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Record(models.Model):
    zone = models.ForeignKey(Zone, related_name='records', on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    desc = models.CharField(max_length=1000)
    ttl = models.IntegerField()
    type = models.CharField(max_length=20)
    data = models.CharField(max_length=65536)
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
