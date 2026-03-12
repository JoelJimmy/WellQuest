from django.urls import path
from . import views

urlpatterns = [
    # core
    path('', views.home_view, name='home'),
    path('checkin/<str:category>/', views.checkin_view, name='checkin'),
    path('checkin/<str:category>/complete/', views.complete_checkin_view, name='complete_checkin'),

    # category goals (must come before custom goals to avoid conflict)
    path('goals/', views.goals_view, name='goals'),
    path('goals/update/<str:category>/', views.update_goal_view, name='update_goal'),

    # custom goals - separate prefix avoids <str:category> conflict
    path('custom-goals/create/', views.create_custom_goal_view, name='create_custom_goal'),
    path('custom-goals/<int:goal_id>/checkin/', views.checkin_custom_goal_view, name='checkin_custom_goal'),
    path('custom-goals/<int:goal_id>/delete/', views.delete_custom_goal_view, name='delete_custom_goal'),

    # badges
    path('badges/', views.badges_view, name='badges'),

    # friends
    path('people/', views.people_view, name='people'),
    path('people/<int:user_id>/add/', views.send_friend_request_view, name='send_friend_request'),
    path('people/<int:user_id>/accept/', views.accept_friend_request_view, name='accept_friend_request'),
    path('people/<int:user_id>/remove/', views.remove_friend_view, name='remove_friend'),
    path('friends/', views.friends_feed_view, name='friends_feed'),

    #nudges
    path('people/<int:user_id>/nudge/', views.nudge_friend_view, name='nudge_friend'),
]