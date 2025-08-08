from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateTimeField(null=True, blank=True)
    color = models.CharField(max_length=10, default='blue')

    def __str__(self):
        return self.title
