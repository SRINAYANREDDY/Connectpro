from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Post, Like, Bookmark, Comment, Hashtag
from .forms import PostForm, CommentForm
from apps.accounts.models import Follow, Block
from apps.notifications.models import Notification


@login_required
def feed(request):
    user = request.user
    blocked_users = Block.objects.filter(blocker=user).values_list('blocked', flat=True)
    blocked_by_users = Block.objects.filter(blocked=user).values_list('blocker', flat=True)
    blocked_ids = set(blocked_users) | set(blocked_by_users)

    following_ids = Follow.objects.filter(
        follower=user, status='accepted'
    ).values_list('following', flat=True)

    posts = Post.objects.filter(
        Q(author__in=following_ids) | Q(author=user)
    ).exclude(
        author__in=blocked_ids
    ).exclude(
        hidden_from=user
    ).select_related('author').prefetch_related('likes', 'comments', 'hashtags').order_by('-created_at')

    form = PostForm()
    comment_form = CommentForm()

    post_data = []
    for post in posts:
        post_data.append({
            'post': post,
            'liked': post.is_liked_by(user),
            'bookmarked': post.is_bookmarked_by(user),
            'comment_count': post.comments.filter(parent=None).count(),
        })

    return render(request, 'posts/feed.html', {
        'post_data': post_data,
        'form': form,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:feed')
    return redirect('posts:feed')


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if post.author.has_blocked(user) or user.has_blocked(post.author):
        return redirect('posts:feed')

    if post.hidden_from.filter(pk=user.pk).exists():
        return redirect('posts:feed')

    if post.author.is_private and not user.is_following(post.author) and user != post.author:
        return render(request, 'posts/private.html', {'post': post})

    comments = post.comments.filter(parent=None).select_related('author').prefetch_related('replies__author')
    comment_form = CommentForm()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked': post.is_liked_by(user),
        'bookmarked': post.is_bookmarked_by(user),
    })


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    return JsonResponse({'status': 'deleted'})


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    like = Like.objects.filter(post=post, user=user).first()
    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=user)
        liked = True
        if post.author != user:
            Notification.objects.get_or_create(
                recipient=post.author, sender=user,
                notification_type='like', post=post,
                defaults={'message': f'{user.username} liked your post'}
            )
    return JsonResponse({'liked': liked, 'count': post.get_like_count()})


@login_required
@require_POST
def toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    bm = Bookmark.objects.filter(post=post, user=user).first()
    if bm:
        bm.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(post=post, user=user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    parent_id = request.POST.get('parent_id')
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id)
        comment.save()
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author, sender=request.user,
                notification_type='comment', post=post,
                message=f'{request.user.username} commented on your post'
            )
        return JsonResponse({
            'status': 'ok',
            'comment_id': comment.id,
            'author': comment.author.username,
            'author_avatar': comment.author.get_avatar_url(),
            'content': comment.content,
            'is_reply': comment.is_reply(),
        })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@require_POST
def hide_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.hidden_from.add(request.user)
    return JsonResponse({'status': 'hidden'})


@login_required
def bookmarks_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post__author').prefetch_related('post__likes')
    post_data = []
    for bm in bookmarks:
        post_data.append({
            'post': bm.post,
            'liked': bm.post.is_liked_by(request.user),
            'bookmarked': True,
            'comment_count': bm.post.comments.filter(parent=None).count(),
        })
    return render(request, 'posts/bookmarks.html', {'post_data': post_data})


@login_required
def hashtag_posts(request, tag):
    hashtag = get_object_or_404(Hashtag, name=tag.lower())
    posts = hashtag.posts.exclude(hidden_from=request.user).select_related('author').order_by('-created_at')
    post_data = [{'post': p, 'liked': p.is_liked_by(request.user), 'bookmarked': p.is_bookmarked_by(request.user), 'comment_count': p.comments.count()} for p in posts]
    return render(request, 'posts/hashtag.html', {'hashtag': hashtag, 'post_data': post_data})
