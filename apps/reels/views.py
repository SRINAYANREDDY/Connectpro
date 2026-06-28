import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReelCommentForm, ReelUploadForm
from .models import Reel, ReelComment, ReelLike

User = get_user_model()


@login_required
def reels_feed(request):
    """Show reels from followed users + own reels, ordered by latest."""
    # Try to get followed users from the accounts app Follow model.
    # Gracefully fall back to own reels if the relationship doesn't exist.
    try:
        following_ids = request.user.following.values_list("following_id", flat=True)
    except Exception:
        following_ids = []

    reels = Reel.objects.filter(
        user__in=list(following_ids) + [request.user.id]
    ).select_related("user").prefetch_related("reel_likes", "reel_comments").order_by("-created_at")

    liked_ids = set(
        ReelLike.objects.filter(user=request.user).values_list("reel_id", flat=True)
    )

    return render(request, "reels/reels_feed.html", {
        "reels": reels,
        "liked_ids": liked_ids,
    })


@login_required
def upload_reel(request):
    """Upload a new reel."""
    if request.method == "POST":
        form = ReelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.user = request.user
            reel.save()
            return redirect("reels:view_reel", pk=reel.pk)
    else:
        form = ReelUploadForm()

    return render(request, "reels/upload_reel.html", {"form": form})


@login_required
def view_reel(request, pk):
    """View a single reel and register the view."""
    reel = get_object_or_404(
        Reel.objects.select_related("user").prefetch_related("reel_likes", "reel_comments__user"),
        pk=pk,
    )
    reel.views.add(request.user)

    liked = ReelLike.objects.filter(user=request.user, reel=reel).exists()
    comment_form = ReelCommentForm()
    comments = reel.reel_comments.select_related("user").order_by("created_at")

    return render(request, "reels/view_reel.html", {
        "reel": reel,
        "liked": liked,
        "comment_form": comment_form,
        "comments": comments,
    })


@login_required
@require_POST
def toggle_reel_like(request, pk):
    """Toggle like on a reel. Returns JSON {liked, count}."""
    reel = get_object_or_404(Reel, pk=pk)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({"liked": liked, "count": reel.like_count})


@login_required
@require_POST
def delete_reel(request, pk):
    """Delete a reel — only the owner can do this."""
    reel = get_object_or_404(Reel, pk=pk, user=request.user)
    reel.delete()
    return redirect("reels:reels_feed")


@login_required
@require_POST
def add_reel_comment(request, pk):
    """Add a comment to a reel. Supports both AJAX and standard POST."""
    reel = get_object_or_404(Reel, pk=pk)
    form = ReelCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.reel = reel
        comment.save()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "comment": {
                    "id": comment.pk,
                    "user": comment.user.username,
                    "avatar": getattr(comment.user, "avatar_url", ""),
                    "content": comment.content,
                    "created_at": comment.created_at.strftime("%b %d, %Y %H:%M"),
                },
                "count": reel.comment_count,
            })
        return redirect("reels:view_reel", pk=pk)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return redirect("reels:view_reel", pk=pk)
