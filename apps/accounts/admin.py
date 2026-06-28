from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow, Block, Education, Skill, Project


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'is_private', 'is_verified', 'date_joined']
    list_filter = ['is_private', 'is_verified', 'is_staff']
    search_fields = ['email', 'username', 'full_name']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('username', 'full_name', 'bio', 'headline', 'location', 'website', 'avatar', 'cover_photo')}),
        ('Settings', {'fields': ('is_private', 'is_verified', 'theme')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'username', 'password1', 'password2')}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'degree', 'start_year', 'end_year']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'ai_rating', 'created_at']
