from django.db import models


# Create your models here.

class WebApp(models.Model):
    name = models.CharField(max_length=30)
    profit = models.FloatField()


class LocalTweet(models.Model):
    text = models.CharField(max_length=140, null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
