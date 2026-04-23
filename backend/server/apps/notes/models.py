from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Note(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
