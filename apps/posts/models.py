import re
from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'#{self.name}'


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name='posts')
    hidden_from = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='hidden_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._extract_hashtags()

    def _extract_hashtags(self):
        tags = re.findall(r'#(\w+)', self.content)
        self.hashtags.clear()
        for tag in set(tags):
            ht, _ = Hashtag.objects.get_or_create(name=tag.lower())
            self.hashtags.add(ht)

    def get_like_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()

    def is_bookmarked_by(self, user):
        return self.bookmarks.filter(user=user).exists()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class Bookmark(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarked_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post.id}: {self.content[:40]}'

    def is_reply(self):
        return self.parent is not None
