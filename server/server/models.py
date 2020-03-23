from django.db import models

# Create your models here.

class Score(models.Model):
    score1 = models.CharField(max_length=30)
    score2 = models.CharField(max_length=30)
    score3 = models.CharField(max_length=30)
    result = models.CharField(max_length=30)