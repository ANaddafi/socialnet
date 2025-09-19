from django.contrib import admin
from .models import Post, Like, Repost, Bookmark

class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ('user', 'created_at')

class RepostInline(admin.TabularInline):
    model = Repost
    extra = 0
    readonly_fields = ('user', 'created_at')

class BookmarkInline(admin.TabularInline):
    model = Bookmark
    extra = 0
    readonly_fields = ('user', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'likes_count', 'comments_count', 'reposts_count', 'shares_count')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'shares_count')
    fieldsets = (
        (None, {'fields': ('author', 'content', 'parent', 'image', 'video')}),
        ('Counts', {'fields': ('likes_count', 'comments_count', 'reposts_count', 'shares_count')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [LikeInline, RepostInline, BookmarkInline]

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'post', 'created_at')}),
    )

@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'post', 'created_at')}),
    )

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username', 'post__content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'post', 'created_at')}),
    )
