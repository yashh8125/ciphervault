from django.db import models
from django.contrib.auth.models import User

class PasswordEntry(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    site_name   = models.CharField(max_length=255)
    site_url    = models.CharField(max_length=500, blank=True)
    username    = models.CharField(max_length=255)
    password    = models.BinaryField()        # stores AES encrypted bytes
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.site_name} ({self.username})"
