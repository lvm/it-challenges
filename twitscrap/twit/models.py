from __future__ import unicode_literals

from django.db import models

class TwitterUser(models.Model):
    username = models.CharField(max_length=255, unique=True)
    followers = models.IntegerField()
    description = models.CharField(max_length=255)
    avatar = models.URLField()

    def __unicode__(self):
        return unicode(self.username)

    class Meta:
        ordering = ('followers',)
