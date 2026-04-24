from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False


class UsedToken(models.Model):
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    user_id = models.IntegerField(db_index=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Used Token"
        verbose_name_plural = "Used Tokens"
        indexes = [
            models.Index(fields=['user_id']),
        ]

    def __str__(self):
        return f"UsedToken(user={self.user_id}, hash={self.token_hash[:12]}...)"


class EmailThrottle(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    last_sent_at = models.DateTimeField(default=timezone.now)
    send_count = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Email Throttle"
        verbose_name_plural = "Email Throttles"

    def __str__(self):
        return f"EmailThrottle(email={self.email}, last_sent={self.last_sent_at})"
