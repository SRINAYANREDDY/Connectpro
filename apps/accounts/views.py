import json
import anthropic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from .models import User, Follow, Block, Education, Skill, Project
from .forms import RegisterForm, LoginForm, ProfileEditForm, EducationForm, SkillForm, ProjectForm
from apps.notifications.models import Notification


def register_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to ConnectPro!')
        return redirect('posts:feed')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    form = LoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'posts:feed'))
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    viewer = request.user

    if profile_user.has_blocked(viewer):
        return render(request, 'accounts/blocked.html')

    is_own_profile = viewer == profile_user
    is_following = viewer.is_following(profile_user)
    has_pending = viewer.has_follow_request(profile_user)
    is_blocked = viewer.has_blocked(profile_user)

    can_see_posts = (
        is_own_profile or
        not profile_user.is_private or
        is_following
    )

    posts = []
    if can_see_posts:
        from apps.posts.models import Post
        posts = Post.objects.filter(author=profile_user).exclude(
            hidden_from=viewer
        ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')

    follow_requests = []
    if is_own_profile:
        follow_requests = Follow.objects.filter(following=viewer, status='pending').select_related('follower')

    followers = Follow.objects.filter(following=profile_user, status='accepted').select_related('follower')
    following = Follow.objects.filter(follower=profile_user, status='accepted').select_related('following')

    ctx = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
        'has_pending': has_pending,
        'is_blocked': is_blocked,
        'can_see_posts': can_see_posts,
        'posts': posts,
        'follow_requests': follow_requests,
        'followers': followers,
        'following': following,
        'education': profile_user.education.all(),
        'skills': profile_user.skills.all(),
        'projects': profile_user.projects.all(),
    }
    return render(request, 'accounts/profile.html', ctx)


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
@require_POST
def toggle_theme(request):
    user = request.user
    user.theme = 'dark' if user.theme == 'light' else 'light'
    user.save(update_fields=['theme'])
    return JsonResponse({'theme': user.theme})


@login_required
@require_POST
def follow_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    if request.user.has_blocked(target) or target.has_blocked(request.user):
        return JsonResponse({'error': 'Blocked'}, status=403)

    existing = Follow.objects.filter(follower=request.user, following=target).first()
    if existing:
        existing.delete()
        status = 'unfollowed'
    else:
        status = 'pending' if target.is_private else 'accepted'
        Follow.objects.create(follower=request.user, following=target, status=status)
        if status == 'accepted':
            Notification.objects.create(
                recipient=target, sender=request.user,
                notification_type='follow', message=f'{request.user.username} started following you'
            )
        else:
            Notification.objects.create(
                recipient=target, sender=request.user,
                notification_type='follow_request', message=f'{request.user.username} requested to follow you'
            )

    return JsonResponse({
        'status': status,
        'followers_count': target.get_followers_count()
    })


@login_required
@require_POST
def accept_follow_request(request, username):
    follower = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, follower=follower, following=request.user, status='pending')
    follow.status = 'accepted'
    follow.save()
    Notification.objects.create(
        recipient=follower, sender=request.user,
        notification_type='follow_accepted',
        message=f'{request.user.username} accepted your follow request'
    )
    return JsonResponse({'status': 'accepted'})


@login_required
@require_POST
def decline_follow_request(request, username):
    follower = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=follower, following=request.user, status='pending').delete()
    return JsonResponse({'status': 'declined'})


@login_required
@require_POST
def block_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot block yourself'}, status=400)
    block, created = Block.objects.get_or_create(blocker=request.user, blocked=target)
    if not created:
        block.delete()
        return JsonResponse({'status': 'unblocked'})
    Follow.objects.filter(follower=request.user, following=target).delete()
    Follow.objects.filter(follower=target, following=request.user).delete()
    return JsonResponse({'status': 'blocked'})


@login_required
def add_education(request):
    form = EducationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        edu = form.save(commit=False)
        edu.user = request.user
        edu.save()
        messages.success(request, 'Education added!')
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/add_education.html', {'form': form})


@login_required
def delete_education(request, pk):
    edu = get_object_or_404(Education, pk=pk, user=request.user)
    edu.delete()
    return redirect('accounts:profile', username=request.user.username)


@login_required
def add_skill(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            return JsonResponse({'status': 'ok', 'name': skill.name, 'id': skill.id})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def delete_skill(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    skill.delete()
    return JsonResponse({'status': 'deleted'})


@login_required
def add_project(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.user = request.user
        project.save()
        messages.success(request, 'Project added!')
        return redirect('accounts:profile', username=request.user.username)
    return render(request, 'accounts/add_project.html', {'form': form})


@login_required
@require_POST
def rate_project_ai(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = f"""Rate this software project on a scale of 1-10 and provide detailed feedback.

Project Title: {project.title}
Description: {project.description}
Technologies Used: {project.technologies}
Project URL: {project.url or 'Not provided'}

Respond in this exact JSON format:
{{"rating": <number 1-10>, "feedback": "<detailed feedback paragraph>", "strengths": ["strength1", "strength2"], "improvements": ["improvement1", "improvement2"]}}"""

        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}]
        )
        result = json.loads(message.content[0].text)
        project.ai_rating = result['rating']
        project.ai_feedback = result['feedback']
        project.save(update_fields=['ai_rating', 'ai_feedback'])
        return JsonResponse({'status': 'ok', 'rating': result['rating'], 'feedback': result['feedback'],
                             'strengths': result.get('strengths', []), 'improvements': result.get('improvements', [])})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    project.delete()
    messages.success(request, 'Project deleted.')
    return redirect('accounts:profile', username=request.user.username)


@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(following=profile_user, status='accepted').select_related('follower')
    return render(request, 'accounts/follow_list.html', {'follows': follows, 'list_type': 'Followers', 'profile_user': profile_user})


@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(follower=profile_user, status='accepted').select_related('following')
    return render(request, 'accounts/follow_list.html', {'follows': follows, 'list_type': 'Following', 'profile_user': profile_user})
