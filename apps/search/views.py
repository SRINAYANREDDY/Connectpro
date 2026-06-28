from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from apps.accounts.models import User, Follow, Block
from apps.posts.models import Post, Hashtag


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'users')
    user = request.user

    blocked_ids = set(Block.objects.filter(blocker=user).values_list('blocked', flat=True)) | \
                  set(Block.objects.filter(blocked=user).values_list('blocker', flat=True))

    users_results = []
    posts_results = []
    hashtag_results = []

    if query:
        if search_type in ('users', 'all'):
            users_results = User.objects.filter(
                Q(username__icontains=query) | Q(full_name__icontains=query)
            ).exclude(pk__in=blocked_ids).exclude(pk=user.pk)[:20]

        if search_type in ('posts', 'all'):
            posts_results = Post.objects.filter(
                Q(content__icontains=query)
            ).exclude(author__in=blocked_ids).exclude(hidden_from=user).select_related('author')[:20]

        if search_type in ('hashtags', 'all'):
            hashtag_results = Hashtag.objects.filter(name__icontains=query.lstrip('#'))[:10]

    return render(request, 'search/search.html', {
        'query': query,
        'search_type': search_type,
        'users_results': users_results,
        'posts_results': posts_results,
        'hashtag_results': hashtag_results,
    })


@login_required
def explore(request):
    user = request.user
    blocked_ids = set(Block.objects.filter(blocker=user).values_list('blocked', flat=True)) | \
                  set(Block.objects.filter(blocked=user).values_list('blocker', flat=True))
    following_ids = set(Follow.objects.filter(follower=user, status='accepted').values_list('following', flat=True))

    trending_hashtags = Hashtag.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:15]

    suggested_users = User.objects.exclude(
        pk__in=following_ids
    ).exclude(pk__in=blocked_ids).exclude(pk=user.pk).annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:8]

    recent_posts = Post.objects.exclude(
        author__in=blocked_ids
    ).exclude(hidden_from=user).select_related('author').prefetch_related('likes')[:12]

    post_data = [{
        'post': p,
        'liked': p.is_liked_by(user),
        'bookmarked': p.is_bookmarked_by(user),
        'comment_count': p.comments.count(),
    } for p in recent_posts]

    return render(request, 'search/explore.html', {
        'trending_hashtags': trending_hashtags,
        'suggested_users': suggested_users,
        'post_data': post_data,
    })
