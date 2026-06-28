from django.urls import path

from . import views

app_name = "reels"

urlpatterns = [
    path("", views.reels_feed, name="reels_feed"),
    path("upload/", views.upload_reel, name="upload_reel"),
    path("<int:pk>/", views.view_reel, name="view_reel"),
    path("<int:pk>/like/", views.toggle_reel_like, name="toggle_reel_like"),
    path("<int:pk>/comment/", views.add_reel_comment, name="add_reel_comment"),
    path("<int:pk>/delete/", views.delete_reel, name="delete_reel"),
]
