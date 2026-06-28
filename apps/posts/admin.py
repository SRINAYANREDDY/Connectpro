from django.contrib import admin
from .models import Post, Like, Bookmark, Comment, Hashtag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content', 'created_at']
    search_fields = ['author__username', 'content']

admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(Comment)
admin.site.register(Hashtag)
