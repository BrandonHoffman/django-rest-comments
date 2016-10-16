from __future__ import unicode_literals

from django.db import models

class Comment(models.Model):
    username = models.CharField(max_length=64)
    comment = models.TextField()
    url = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=45)
