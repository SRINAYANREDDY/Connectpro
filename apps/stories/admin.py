from django.contrib import admin
from .models import Story
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['author', 'created_at', 'expires_at', 'view_count']
