from django.contrib import admin

from .models import Reel, ReelComment, ReelLike


@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ["user", "caption_preview", "created_at", "view_count", "like_count"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "caption"]
    readonly_fields = ["created_at", "views"]

    def caption_preview(self, obj):
        return obj.caption[:60] if obj.caption else "—"
    caption_preview.short_description = "Caption"

    def view_count(self, obj):
        return obj.views.count()
    view_count.short_description = "Views"

    def like_count(self, obj):
        return obj.reel_likes.count()
    like_count.short_description = "Likes"


@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "reel", "created_at"]
    list_filter = ["created_at"]


@admin.register(ReelComment)
class ReelCommentAdmin(admin.ModelAdmin):
    list_display = ["user", "reel", "content_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "content"]

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = "Content"
