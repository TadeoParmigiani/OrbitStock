from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    color = models.CharField(max_length=10, default='blue')
    is_template = models.BooleanField(default=False)

    def __str__(self):
        return self.title
