from django import forms

from .models import Reel, ReelComment


class ReelUploadForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ["video", "thumbnail", "caption"]
        widgets = {
            "caption": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Write a caption...",
                "class": "form-control",
            }),
            "video": forms.FileInput(attrs={
                "accept": "video/*",
                "class": "form-control",
                "id": "reel-video-input",
            }),
            "thumbnail": forms.FileInput(attrs={
                "accept": "image/*",
                "class": "form-control",
                "id": "reel-thumbnail-input",
            }),
        }

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if video:
            max_size = 100 * 1024 * 1024  # 100 MB
            if video.size > max_size:
                raise forms.ValidationError("Video file must be under 100 MB.")
            allowed = ["video/mp4", "video/webm", "video/ogg", "video/quicktime"]
            if hasattr(video, "content_type") and video.content_type not in allowed:
                raise forms.ValidationError("Unsupported video format. Use MP4, WebM, OGG or MOV.")
        return video


class ReelCommentForm(forms.ModelForm):
    class Meta:
        model = ReelComment
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(attrs={
                "placeholder": "Add a comment...",
                "class": "comment-input",
                "autocomplete": "off",
            }),
        }
        labels = {"content": ""}
