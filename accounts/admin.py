from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'avatar', 'total_xp', 'current_streak', 'get_level')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-total_xp',)
    fieldsets = UserAdmin.fieldsets + (
        ('WellQuest Stats', {'fields': ('avatar', 'total_xp', 'current_streak', 'longest_streak', 'last_checkin_date')}),
    )

    def get_level(self, obj):
        return f'Level {obj.get_level()}'
    get_level.short_description = 'Level'
