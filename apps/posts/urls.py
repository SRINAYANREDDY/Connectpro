from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create/', views.create_post, name='create'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('<int:pk>/delete/', views.delete_post, name='delete'),
    path('<int:pk>/like/', views.toggle_like, name='like'),
    path('<int:pk>/bookmark/', views.toggle_bookmark, name='bookmark'),
    path('<int:pk>/comment/', views.add_comment, name='comment'),
    path('<int:pk>/hide/', views.hide_post, name='hide'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('hashtag/<str:tag>/', views.hashtag_posts, name='hashtag'),
]
