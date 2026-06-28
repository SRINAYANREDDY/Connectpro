from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(recipient=request.user).select_related('sender', 'post')[:50]
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifs})

@login_required
@require_POST
def mark_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
