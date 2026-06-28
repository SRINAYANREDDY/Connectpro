from django.conf import settings
from django.db import models
from django.urls import reverse


class Conversation(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        names = ", ".join(u.username for u in self.participants.all()[:3])
        return f"Conversation({names})"

    def get_absolute_url(self):
        return reverse("messaging:conversation", kwargs={"pk": self.pk})

    def get_last_message(self):
        return self.messages.order_by("-created_at").first()

    def get_unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def get_other_participant(self, user):
        """Return the other participant in a two-person conversation."""
        return self.participants.exclude(pk=user.pk).first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="messaging/files/%Y/%m/", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.content[:60] or '[file]'}"

    @property
    def is_file_message(self):
        return bool(self.file)

    @property
    def file_name(self):
        if self.file:
            return self.file.name.split("/")[-1]
        return ""

    @property
    def file_extension(self):
        name = self.file_name
        if "." in name:
            return name.rsplit(".", 1)[-1].lower()
        return ""

    @property
    def is_image(self):
        return self.file_extension in {"jpg", "jpeg", "png", "gif", "webp", "svg"}
