from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def story_expiry():
    return timezone.now() + timedelta(hours=24)


class Story(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/images/', blank=True, null=True)
    video = models.FileField(upload_to='stories/videos/', blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=story_expiry)
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='viewed_stories')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        return f'{self.author.username} story at {self.created_at}'

    def is_expired(self):
        return timezone.now() > self.expires_at

    def view_count(self):
        return self.viewers.count()

    @classmethod
    def active(cls):
        return cls.objects.filter(expires_at__gt=timezone.now())
