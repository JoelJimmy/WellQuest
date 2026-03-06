from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.CharField(max_length=10, default='🧘')  # emoji avatar
    total_xp = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_checkin_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_level(self):
        thresholds = [0, 50, 120, 220, 360, 550, 800, 1100, 1500, 2000]
        level = 1
        for i, t in enumerate(thresholds):
            if self.total_xp >= t:
                level = i + 1
        return level

    def get_level_progress(self):
        thresholds = [0, 50, 120, 220, 360, 550, 800, 1100, 1500, 2000]
        level = self.get_level()
        current = thresholds[level - 1] if level - 1 < len(thresholds) else thresholds[-1]
        next_t = thresholds[level] if level < len(thresholds) else thresholds[-1] + 500
        if next_t == current:
            return 100
        return int(((self.total_xp - current) / (next_t - current)) * 100)

    def get_xp_to_next(self):
        thresholds = [0, 50, 120, 220, 360, 550, 800, 1100, 1500, 2000]
        level = self.get_level()
        next_t = thresholds[level] if level < len(thresholds) else thresholds[-1] + 500
        return max(0, next_t - self.total_xp)

    def __str__(self):
        return self.email