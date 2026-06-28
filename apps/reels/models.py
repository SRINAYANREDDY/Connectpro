from django.conf import settings
from django.db import models
from django.urls import reverse


class Reel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reels",
    )
    video = models.FileField(upload_to="reels/videos/")
    thumbnail = models.ImageField(upload_to="reels/thumbnails/", blank=True, null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="viewed_reels",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reel by {self.user} at {self.created_at:%Y-%m-%d %H:%M}"

    def get_absolute_url(self):
        return reverse("reels:view_reel", kwargs={"pk": self.pk})

    @property
    def like_count(self):
        return self.reel_likes.count()

    @property
    def comment_count(self):
        return self.reel_comments.count()

    @property
    def view_count(self):
        return self.views.count()


class ReelLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reel_likes",
    )
    reel = models.ForeignKey(
        Reel,
        on_delete=models.CASCADE,
        related_name="reel_likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "reel")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} liked {self.reel}"


class ReelComment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reel_comments",
    )
    reel = models.ForeignKey(
        Reel,
        on_delete=models.CASCADE,
        related_name="reel_comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} on {self.reel}: {self.content[:40]}"
