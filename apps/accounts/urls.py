from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('theme/', views.toggle_theme, name='toggle_theme'),
    path('education/add/', views.add_education, name='add_education'),
    path('education/<int:pk>/delete/', views.delete_education, name='delete_education'),
    path('skill/add/', views.add_skill, name='add_skill'),
    path('skill/<int:pk>/delete/', views.delete_skill, name='delete_skill'),
    path('project/add/', views.add_project, name='add_project'),
    path('project/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:pk>/rate/', views.rate_project_ai, name='rate_project'),
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/follow/', views.follow_user, name='follow'),
    path('<str:username>/block/', views.block_user, name='block'),
    path('<str:username>/accept-request/', views.accept_follow_request, name='accept_request'),
    path('<str:username>/decline-request/', views.decline_follow_request, name='decline_request'),
    path('<str:username>/followers/', views.followers_list, name='followers'),
    path('<str:username>/following/', views.following_list, name='following'),
]
