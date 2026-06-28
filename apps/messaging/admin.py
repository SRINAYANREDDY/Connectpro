from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["sender", "content", "file", "is_read", "created_at"]
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "participant_names", "created_at", "updated_at", "message_count"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [MessageInline]

    def participant_names(self, obj):
        return ", ".join(u.username for u in obj.participants.all())
    participant_names.short_description = "Participants"

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "conversation", "content_preview", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["sender__username", "content"]
    readonly_fields = ["created_at"]

    def content_preview(self, obj):
        return obj.content[:80] or "[file]"
    content_preview.short_description = "Content"
