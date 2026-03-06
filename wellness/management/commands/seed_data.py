from django.core.management.base import BaseCommand
from wellness.models import Task, Badge


TASKS = [
    # Mental
    ('mental', 'Meditate for 5 minutes', 15),
    ('mental', 'Write 3 things you are grateful for', 10),
    ('mental', 'Take 10 deep breaths', 8),
    ('mental', 'Journal how you are feeling today', 12),
    ('mental', 'Do a 5-minute body scan', 10),
    # Fitness
    ('fitness', 'Walk 5,000+ steps today', 20),
    ('fitness', 'Do 15 minutes of movement', 15),
    ('fitness', 'Stretch for 10 minutes', 10),
    ('fitness', 'Complete a full workout', 25),
    ('fitness', 'Do 20 push-ups or squats', 12),
    # Nutrition
    ('nutrition', 'Drink 8 glasses of water', 15),
    ('nutrition', 'Eat a serving of vegetables', 10),
    ('nutrition', 'Skip sugary drinks today', 12),
    ('nutrition', 'Eat a balanced breakfast', 10),
    ('nutrition', 'Prepare a healthy meal at home', 18),
    # Sleep
    ('sleep', 'Be in bed by 10:30 PM', 15),
    ('sleep', 'No screens 1 hour before bed', 12),
    ('sleep', 'Sleep 7-9 hours tonight', 20),
    ('sleep', 'Take a 20-minute power nap', 8),
    ('sleep', 'Keep your bedroom cool and dark', 10),
]

BADGES = [
    ('first_step', 'First Step', 'Complete your first check-in', '👶', 10),
    ('streak_3', 'On Fire', '3-day streak', '🔥', 30),
    ('streak_7', 'Lightning Week', '7-day streak', '⚡', 100),
    ('all_cats', 'Rainbow Day', 'Check in all 4 areas in one day', '🌈', 50),
    ('level_5', 'Dedicated', 'Reach Level 5', '🏅', 75),
    ('xp_500', 'Crystal Mind', 'Earn 500 XP total', '💎', 100),
    ('streak_30', 'Unstoppable', '30-day streak', '🦁', 300),
    ('xp_1000', 'Wellness Warrior', 'Earn 1000 XP total', '🏆', 200),
]


class Command(BaseCommand):
    help = 'Seed the database with initial tasks and badges'

    def handle(self, *args, **kwargs):
        # Seed tasks
        task_count = 0
        for category, text, xp in TASKS:
            _, created = Task.objects.get_or_create(
                category=category,
                text=text,
                defaults={'xp_reward': xp}
            )
            if created:
                task_count += 1
        self.stdout.write(f'Created {task_count} tasks')

        # Seed badges
        badge_count = 0
        for slug, name, desc, emoji, xp in BADGES:
            _, created = Badge.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'emoji': emoji, 'xp_reward': xp}
            )
            if created:
                badge_count += 1
        self.stdout.write(f'Created {badge_count} badges')
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))