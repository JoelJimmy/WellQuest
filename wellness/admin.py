from django.contrib import admin
from .models import Goal, Task, CheckIn, Badge, UserBadge


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('category', 'text', 'xp_reward', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('text',)


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'xp_earned', 'date')
    list_filter = ('category', 'date')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('emoji', 'name', 'description', 'xp_reward')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'text')
    list_filter = ('category',)