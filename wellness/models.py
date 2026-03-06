from django.db import models
from django.conf import settings


CATEGORY_CHOICES = [
    ('mental', 'Mental Health'),
    ('fitness', 'Physical Fitness'),
    ('nutrition', 'Nutrition & Hydration'),
    ('sleep', 'Sleep & Recovery'),
]

CATEGORY_EMOJIS = {
    'mental': '🧘',
    'fitness': '💪',
    'nutrition': '🥗',
    'sleep': '😴',
}


class Goal(models.Model):
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    text     = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'category')

    def __str__(self):
        return f"{self.user.email} - {self.category}: {self.text[:40]}"


class CustomGoal(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_goals')
    title       = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    emoji       = models.CharField(max_length=10, default='🎯')
    target_days = models.IntegerField(default=30)
    completed_days = models.IntegerField(default=0)
    is_completed   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def progress_percent(self):
        if self.target_days == 0:
            return 100
        return min(int((self.completed_days / self.target_days) * 100), 100)

    @property
    def days_remaining(self):
        return max(0, self.target_days - self.completed_days)

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class CustomGoalCheckIn(models.Model):
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_checkins')
    goal  = models.ForeignKey(CustomGoal, on_delete=models.CASCADE, related_name='checkins')
    note  = models.TextField(blank=True)
    photo = models.ImageField(upload_to='checkin_photos/', blank=True, null=True)
    date  = models.DateField()
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('goal', 'date')
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.user.email} - {self.goal.title} on {self.date}"


class Friendship(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted')]
    from_user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_sent')
    to_user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships_received')
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


class Task(models.Model):
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    text      = models.TextField()
    xp_reward = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.category}] {self.text[:50]}"


class CheckIn(models.Model):
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='checkins')
    task     = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    xp_earned    = models.IntegerField(default=0)
    photo        = models.ImageField(upload_to='checkin_photos/', blank=True, null=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    date         = models.DateField()

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.email} - {self.category} on {self.date}"


class Badge(models.Model):
    slug        = models.CharField(max_length=50, unique=True)
    name        = models.CharField(max_length=100)
    description = models.TextField()
    emoji       = models.CharField(max_length=10)
    xp_reward   = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.emoji} {self.name}"


class UserBadge(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_badges')
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.email} earned {self.badge.name}"
