import json
import random
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import (
    Goal, CustomGoal, CustomGoalCheckIn, Friendship,
    Task, CheckIn, Badge, UserBadge, CATEGORY_CHOICES, CATEGORY_EMOJIS
)

CATEGORY_COLORS = {
    'mental':    {'bg': '#A78BFA', 'light': '#EDE9FE', 'dark': '#6D28D9'},
    'fitness':   {'bg': '#F97316', 'light': '#FFF7ED', 'dark': '#C2410C'},
    'nutrition': {'bg': '#10B981', 'light': '#ECFDF5', 'dark': '#065F46'},
    'sleep':     {'bg': '#3B82F6', 'light': '#EFF6FF', 'dark': '#1E40AF'},
}

EMOJI_CHOICES = ['🎯','🏃','📚','💧','🧠','🌿','🎨','🎸','🏋️','🧘','🌅','💪','🥗','😴','🔥','⭐','🌈','🦋','🐢','🌱']


def get_today_status(user):
    today = date.today()
    return {c.category for c in CheckIn.objects.filter(user=user, date=today)}


def check_and_award_badges(user, completed_today):
    awarded = []
    existing = set(UserBadge.objects.filter(user=user).values_list('badge__slug', flat=True))

    def award(slug):
        if slug not in existing:
            try:
                badge = Badge.objects.get(slug=slug)
                UserBadge.objects.create(user=user, badge=badge)
                user.total_xp += badge.xp_reward
                user.save()
                awarded.append({'name': badge.name, 'emoji': badge.emoji})
                existing.add(slug)
            except Badge.DoesNotExist:
                pass

    if CheckIn.objects.filter(user=user).count() == 1:
        award('first_step')
    if len(completed_today) == 4:
        award('all_cats')
    if user.current_streak >= 3:  award('streak_3')
    if user.current_streak >= 7:  award('streak_7')
    if user.current_streak >= 30: award('streak_30')
    if user.total_xp >= 500:  award('xp_500')
    if user.total_xp >= 1000: award('xp_1000')
    if user.get_level() >= 5: award('level_5')
    return awarded


def update_streak(user):
    today = date.today()
    last  = user.last_checkin_date
    if last is None:
        user.current_streak = 1
    elif last == today:
        pass
    elif (today - last).days == 1:
        user.current_streak += 1
    else:
        user.current_streak = 1
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
    user.last_checkin_date = today
    user.save()


# ── HOME ──────────────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    user = request.user
    completed_today = get_today_status(user)
    goals  = {g.category: g.text for g in Goal.objects.filter(user=user)}
    badges = UserBadge.objects.filter(user=user).select_related('badge').order_by('-earned_at')

    categories = []
    for cat, label in CATEGORY_CHOICES:
        categories.append({
            'key': cat, 'label': label,
            'emoji': CATEGORY_EMOJIS[cat],
            'colors': CATEGORY_COLORS[cat],
            'done': cat in completed_today,
            'goal': goals.get(cat, ''),
        })

    # Custom goals — active ones only, ordered by least progress first
    today = date.today()
    custom_goals = CustomGoal.objects.filter(user=user, is_completed=False).order_by('created_at')
    checked_today_ids = set(
        CustomGoalCheckIn.objects.filter(user=user, date=today).values_list('goal_id', flat=True)
    )

    context = {
        'user': user,
        'categories': categories,
        'completed_count': len(completed_today),
        'all_done': len(completed_today) == 4,
        'badges': badges[:6],
        'level': user.get_level(),
        'level_progress': user.get_level_progress(),
        'xp_to_next': user.get_xp_to_next(),
        'custom_goals': custom_goals,
        'checked_today_ids': checked_today_ids,
    }
    return render(request, 'wellness/home.html', context)


# ── CHECKIN ───────────────────────────────────────────────────────────────────

@login_required
def checkin_view(request, category):
    if category not in dict(CATEGORY_CHOICES):
        return redirect('home')
    completed_today = get_today_status(request.user)
    if category in completed_today:
        return redirect('home')

    recent_ids = CheckIn.objects.filter(user=request.user).order_by('-completed_at')[:10].values_list('task_id', flat=True)
    tasks = Task.objects.filter(category=category, is_active=True).exclude(id__in=recent_ids)
    if not tasks.exists():
        tasks = Task.objects.filter(category=category, is_active=True)
    task = random.choice(list(tasks)) if tasks.exists() else None

    return render(request, 'wellness/checkin.html', {
        'category': category,
        'label': dict(CATEGORY_CHOICES)[category],
        'emoji': CATEGORY_EMOJIS[category],
        'colors': CATEGORY_COLORS[category],
        'task': task,
    })


@login_required
@require_POST
def complete_checkin_view(request, category):
    if category not in dict(CATEGORY_CHOICES):
        return JsonResponse({'error': 'Invalid category'}, status=400)
    if category in get_today_status(request.user):
        return JsonResponse({'error': 'Already completed today'}, status=400)

    task_id = request.POST.get('task_id')
    task    = get_object_or_404(Task, id=task_id) if task_id else None
    xp      = task.xp_reward if task else 10
    photo   = request.FILES.get('photo')

    checkin = CheckIn.objects.create(
        user=request.user, task=task, category=category,
        xp_earned=xp, date=date.today(), photo=photo
    )

    request.user.total_xp += xp
    request.user.save()
    update_streak(request.user)

    completed_today = get_today_status(request.user)
    new_badges = check_and_award_badges(request.user, completed_today)

    photo_url = checkin.photo.url if checkin.photo else None

    return JsonResponse({
        'success': True, 'xp_earned': xp,
        'total_xp': request.user.total_xp,
        'level': request.user.get_level(),
        'level_progress': request.user.get_level_progress(),
        'streak': request.user.current_streak,
        'new_badges': new_badges,
        'photo_url': photo_url,
    })


# ── GOALS ─────────────────────────────────────────────────────────────────────

@login_required
def goals_view(request):
    goals = {g.category: g for g in Goal.objects.filter(user=request.user)}
    custom_goals = CustomGoal.objects.filter(user=request.user)
    today = date.today()
    checked_today_ids = set(
        CustomGoalCheckIn.objects.filter(user=request.user, date=today).values_list('goal_id', flat=True)
    )
    categories = []
    for cat, label in CATEGORY_CHOICES:
        categories.append({
            'key': cat, 'label': label,
            'emoji': CATEGORY_EMOJIS[cat],
            'colors': CATEGORY_COLORS[cat],
            'goal': goals.get(cat),
        })
    return render(request, 'wellness/goals.html', {
        'categories': categories,
        'custom_goals': custom_goals,
        'checked_today_ids': checked_today_ids,
        'emoji_choices': EMOJI_CHOICES,
    })


@login_required
@require_POST
def update_goal_view(request, category):
    if category not in dict(CATEGORY_CHOICES):
        return JsonResponse({'error': 'Invalid category'}, status=400)
    data = json.loads(request.body)
    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Empty'}, status=400)
    goal, _ = Goal.objects.update_or_create(
        user=request.user, category=category, defaults={'text': text}
    )
    return JsonResponse({'success': True, 'text': goal.text})


# ── CUSTOM GOALS ──────────────────────────────────────────────────────────────

@login_required
@require_POST
def create_custom_goal_view(request):
    data  = json.loads(request.body)
    title = data.get('title', '').strip()
    if not title:
        return JsonResponse({'error': 'Title is required'}, status=400)
    goal = CustomGoal.objects.create(
        user=request.user,
        title=title,
        description=data.get('description', '').strip(),
        emoji=data.get('emoji', '🎯'),
        target_days=int(data.get('target_days', 30)),
    )
    return JsonResponse({'success': True, 'goal': {
        'id': goal.id, 'title': goal.title, 'emoji': goal.emoji,
        'description': goal.description, 'target_days': goal.target_days,
        'completed_days': 0, 'progress_percent': 0,
        'days_remaining': goal.target_days, 'is_completed': False,
    }})


@login_required
@require_POST
def checkin_custom_goal_view(request, goal_id):
    goal    = get_object_or_404(CustomGoal, id=goal_id, user=request.user)
    today   = date.today()
    photo   = request.FILES.get('photo') if request.FILES else None

    existing = CustomGoalCheckIn.objects.filter(goal=goal, date=today).first()
    if existing:
        return JsonResponse({
            'success': True, 'already_done': True,
            'completed_days': goal.completed_days,
            'progress_percent': goal.progress_percent,
            'is_completed': goal.is_completed,
            'total_xp': request.user.total_xp,
            'photo_url': existing.photo.url if existing.photo else None,
        })

    checkin = CustomGoalCheckIn.objects.create(
        user=request.user, goal=goal, date=today,
        note=request.POST.get('note', '') if request.POST else '',
        photo=photo,
    )
    goal.completed_days += 1
    if goal.completed_days >= goal.target_days:
        goal.is_completed = True
    goal.save()
    request.user.total_xp += 5
    request.user.save()

    return JsonResponse({
        'success': True, 'already_done': False,
        'completed_days': goal.completed_days,
        'progress_percent': goal.progress_percent,
        'is_completed': goal.is_completed,
        'total_xp': request.user.total_xp,
        'photo_url': checkin.photo.url if checkin.photo else None,
    })


@login_required
@require_POST
def delete_custom_goal_view(request, goal_id):
    goal = get_object_or_404(CustomGoal, id=goal_id, user=request.user)
    goal.delete()
    return JsonResponse({'success': True})


# ── BADGES ────────────────────────────────────────────────────────────────────

@login_required
def badges_view(request):
    all_badges = Badge.objects.all()
    earned = set(UserBadge.objects.filter(user=request.user).values_list('badge__slug', flat=True))
    return render(request, 'wellness/badges.html', {
        'badges_data': [{'badge': b, 'earned': b.slug in earned} for b in all_badges],
        'earned_count': len(earned),
        'total_count':  all_badges.count(),
    })


# ── FRIENDS ───────────────────────────────────────────────────────────────────

@login_required
def people_view(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    me   = request.user

    all_users    = User.objects.exclude(id=me.id)
    sent_map     = {uid: s for uid, s in Friendship.objects.filter(from_user=me).values_list('to_user_id', 'status')}
    received_map = {uid: s for uid, s in Friendship.objects.filter(to_user=me).values_list('from_user_id', 'status')}

    users_data = []
    for u in all_users:
        if u.id in sent_map:
            rel = 'sent_' + sent_map[u.id]
        elif u.id in received_map:
            rel = 'received_' + received_map[u.id]
        else:
            rel = 'none'
        users_data.append({'user': u, 'relationship': rel})

    pending_requests = Friendship.objects.filter(to_user=me, status='pending').select_related('from_user')
    return render(request, 'wellness/people.html', {
        'users_data': users_data,
        'pending_requests': pending_requests,
        'pending_count': pending_requests.count(),
    })


@login_required
@require_POST
def send_friend_request_view(request, user_id):
    from django.contrib.auth import get_user_model
    to_user = get_object_or_404(get_user_model(), id=user_id)
    if to_user == request.user:
        return JsonResponse({'error': 'Cannot add yourself'}, status=400)
    _, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    return JsonResponse({'success': True, 'created': created})


@login_required
@require_POST
def accept_friend_request_view(request, user_id):
    from django.contrib.auth import get_user_model
    from_user  = get_object_or_404(get_user_model(), id=user_id)
    friendship = get_object_or_404(Friendship, from_user=from_user, to_user=request.user)
    friendship.status = 'accepted'
    friendship.save()
    Friendship.objects.get_or_create(from_user=request.user, to_user=from_user, defaults={'status': 'accepted'})
    return JsonResponse({'success': True})


@login_required
@require_POST
def remove_friend_view(request, user_id):
    from django.contrib.auth import get_user_model
    other = get_object_or_404(get_user_model(), id=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=other) | Q(from_user=other, to_user=request.user)
    ).delete()
    return JsonResponse({'success': True})


@login_required
def friends_feed_view(request):
    me = request.user
    friend_ids = Friendship.objects.filter(from_user=me, status='accepted').values_list('to_user_id', flat=True)
    recent_checkins = CheckIn.objects.filter(
        user_id__in=friend_ids
    ).select_related('user', 'task').order_by('-completed_at')[:40]
    from django.contrib.auth import get_user_model
    friends = get_user_model().objects.filter(id__in=friend_ids)
    return render(request, 'wellness/friends_feed.html', {
        'recent_checkins': recent_checkins,
        'friends': friends,
        'friend_count': friends.count(),
    })
