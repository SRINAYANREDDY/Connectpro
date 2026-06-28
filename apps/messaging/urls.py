from django.urls import path

from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("start/<str:username>/", views.start_conversation, name="start_conversation"),
    path("<int:pk>/", views.conversation, name="conversation"),
    path("<int:pk>/send/", views.send_message, name="send_message"),
    path("<int:pk>/file/", views.upload_file_message, name="upload_file_message"),
]
