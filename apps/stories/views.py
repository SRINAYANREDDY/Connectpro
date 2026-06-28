from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Story
from apps.accounts.models import Follow, Block


@login_required
def stories_list(request):
    user = request.user
    blocked_ids = set(Block.objects.filter(blocker=user).values_list('blocked', flat=True)) | \
                  set(Block.objects.filter(blocked=user).values_list('blocker', flat=True))

    following_ids = Follow.objects.filter(follower=user, status='accepted').values_list('following', flat=True)

    active_stories = Story.active().exclude(author__in=blocked_ids)

    # Group by author
    from collections import defaultdict
    story_groups = defaultdict(list)
    for story in active_stories.select_related('author'):
        if story.author == user or story.author_id in following_ids:
            story_groups[story.author].append(story)

    my_stories = Story.active().filter(author=user)

    return render(request, 'stories/list.html', {
        'story_groups': dict(story_groups),
        'my_stories': my_stories,
    })


@login_required
def story_view(request, pk):
    story = get_object_or_404(Story.active(), pk=pk)
    user = request.user

    if story.author.has_blocked(user) or user.has_blocked(story.author):
        return redirect('stories:list')

    story.viewers.add(user)

    author_stories = Story.active().filter(author=story.author).order_by('created_at')
    story_list = list(author_stories)
    current_index = next((i for i, s in enumerate(story_list) if s.pk == story.pk), 0)
    next_story = story_list[current_index + 1] if current_index + 1 < len(story_list) else None
    prev_story = story_list[current_index - 1] if current_index > 0 else None

    return render(request, 'stories/story_view.html', {
        'story': story,
        'next_story': next_story,
        'prev_story': prev_story,
        'is_own': story.author == user,
        'viewers': story.viewers.all() if story.author == user else None,
    })


@login_required
def create_story(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        caption = request.POST.get('caption', '')
        if image or video:
            Story.objects.create(author=request.user, image=image, video=video, caption=caption)
            return redirect('stories:list')
    return render(request, 'stories/create.html')


@login_required
@require_POST
def delete_story(request, pk):
    story = get_object_or_404(Story, pk=pk, author=request.user)
    story.delete()
    return JsonResponse({'status': 'deleted'})
