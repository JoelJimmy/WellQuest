def pending_friend_requests(request):
    if request.user.is_authenticated:
        from wellness.models import Friendship
        count = Friendship.objects.filter(to_user=request.user, status='pending').count()
        return {'pending_count': count}
    return {'pending_count': 0}