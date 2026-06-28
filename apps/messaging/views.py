from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Conversation, Message

User = get_user_model()


@login_required
def inbox(request):
    """List all conversations the current user is part of, ordered by latest."""
    conversations = (
        request.user.conversations
        .prefetch_related("participants", "messages")
        .order_by("-updated_at")
    )

    conv_data = []
    for conv in conversations:
        other = conv.get_other_participant(request.user)
        last_msg = conv.get_last_message()
        unread = conv.get_unread_count(request.user)
        conv_data.append({
            "conv": conv,
            "other": other,
            "last_msg": last_msg,
            "unread": unread,
        })

    return render(request, "messaging/inbox.html", {
        "conv_data": conv_data,
    })


@login_required
def conversation(request, pk):
    """View full message thread and mark unread messages as read."""
    conv = get_object_or_404(
        Conversation.objects.prefetch_related("participants", "messages__sender"),
        pk=pk,
        participants=request.user,
    )

    # Mark all unread messages from others as read
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    messages = conv.messages.select_related("sender").order_by("created_at")
    other = conv.get_other_participant(request.user)

    return render(request, "messaging/conversation.html", {
        "conv": conv,
        "messages": messages,
        "other": other,
    })


@login_required
def start_conversation(request, username):
    """Get or create a direct conversation with another user."""
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        return redirect("messaging:inbox")

    # Find existing conversation between these two users
    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if existing:
        # Verify it's exactly these two participants (no group chats)
        if existing.participants.count() == 2:
            return redirect("messaging:conversation", pk=existing.pk)

    # Create new conversation
    conv = Conversation.objects.create()
    conv.participants.add(request.user, other_user)
    conv.save()

    return redirect("messaging:conversation", pk=conv.pk)


@login_required
@require_POST
def send_message(request, pk):
    """Send a text message in a conversation (non-WebSocket fallback)."""
    conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
    content = request.POST.get("content", "").strip()

    if not content:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "Message cannot be empty."}, status=400)
        return redirect("messaging:conversation", pk=pk)

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
    )

    # Touch updated_at on conversation
    conv.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": _serialize_message(msg, request.user),
        })

    return redirect("messaging:conversation", pk=pk)


@login_required
@require_POST
def upload_file_message(request, pk):
    """Upload a file attachment in a conversation."""
    conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
    file = request.FILES.get("file")

    if not file:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "No file provided."}, status=400)
        return redirect("messaging:conversation", pk=pk)

    max_size = 25 * 1024 * 1024  # 25 MB
    if file.size > max_size:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "error": "File must be under 25 MB."}, status=400)
        return redirect("messaging:conversation", pk=pk)

    content = request.POST.get("content", "").strip()

    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
        file=file,
    )
    conv.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": _serialize_message(msg, request.user),
        })

    return redirect("messaging:conversation", pk=pk)


# ── helpers ──────────────────────────────────────────────────────────────────

def _serialize_message(msg, current_user):
    """Return a JSON-serialisable dict for a Message."""
    data = {
        "id": msg.pk,
        "sender_id": msg.sender_id,
        "sender_username": msg.sender.username,
        "sender_avatar": getattr(msg.sender, "avatar_url", ""),
        "content": msg.content,
        "is_mine": msg.sender == current_user,
        "created_at": msg.created_at.strftime("%H:%M"),
        "is_file": msg.is_file_message,
    }
    if msg.is_file_message:
        data["file_url"] = msg.file.url
        data["file_name"] = msg.file_name
        data["is_image"] = msg.is_image
    return data
