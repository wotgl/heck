from __future__ import unicode_literals

from django.db import models

# Create your models here.

class VkUser(models.Model):
    vk_id = models.CharField(max_length=100)

class Community(models.Model):
    vk_id = models.CharField(max_length=100, unique=True)
    token = models.CharField(max_length=100)
    banned = models.ManyToManyField(VkUser)

    def __str__(self):
        return self.token

class Post(models.Model):
    community = models.ForeignKey(Community)
    pid = models.CharField(max_length=100, unique=True)
    comments = models.IntegerField()
    text = models.TextField(max_length=100)

class Comment(models.Model):
    cid = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    post = models.ForeignKey(Post)