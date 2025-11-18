from django.db import models
from django.conf import settings

class Job(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    apply_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.company}"
