from django.urls import path
from . import views
app_name = 'stories'
urlpatterns = [
    path('', views.stories_list, name='list'),
    path('create/', views.create_story, name='create'),
    path('<int:pk>/', views.story_view, name='view'),
    path('<int:pk>/delete/', views.delete_story, name='delete'),
]
