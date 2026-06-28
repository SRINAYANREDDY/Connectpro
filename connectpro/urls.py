from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.posts.urls', namespace='posts')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('stories/', include('apps.stories.urls', namespace='stories')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('search/', include('apps.search.urls', namespace='search')),
    path('messages/', include('apps.messaging.urls', namespace='messaging')),
    path('reels/', include('apps.reels.urls', namespace='reels')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
