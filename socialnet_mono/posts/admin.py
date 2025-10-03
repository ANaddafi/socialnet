from django.contrib import admin, messages
from django.conf import settings
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
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
    list_display = (
        'id', 'author', 'content', 'created_at', 'likes_count', 'comments_count', 'reposts_count', 'shares_count',
        'inspect_images_action_link', 'text_to_speech_action_link',
    )
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)
    readonly_fields = (
        'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'shares_count',
        'thumbnail', 
    )
    fieldsets = (
        (None, {'fields': ('author', 'content', 'parent', 'image', 'video', 'thumbnail')}),
        ('Counts', {'fields': ('likes_count', 'comments_count', 'reposts_count', 'shares_count')}),
        ('Status', {'fields': ('is_toxit', 'is_offensive', 'is_blocked_by_system')}),
        ('Metadata', {'fields': ('keywords', 'tags', 'topic', 'sentiment', 'is_nsfw', 'text_to_speech_file')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    inlines = [LikeInline, RepostInline, BookmarkInline]

    actions = ["inspect_selected_images_action", "text_to_speech_selected_action"]

    def inspect_selected_images_action(self, request, queryset):
        post_ids = list(queryset.values_list('id', flat=True))
        inspect_all_images_of_posts(post_ids)
        self.message_user(request, f"Image inspection triggered for {len(post_ids)} post(s).", messages.SUCCESS)
    inspect_selected_images_action.short_description = "Inspect images of selected posts"

    def text_to_speech_selected_action(self, request, queryset):
        post_ids = list(queryset.values_list('id', flat=True))
        call_for_text_to_speech_for_posts(post_ids)
        self.message_user(request, f"Text-to-speech triggered for {len(post_ids)} post(s).", messages.SUCCESS)
    text_to_speech_selected_action.short_description = "Text-to-speech for selected posts"

    def inspect_images_action_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Inspect Images</a>',
            self.get_inspect_images_url(obj.id)
        )
    inspect_images_action_link.short_description = "Inspect Images"
    inspect_images_action_link.allow_tags = True

    def text_to_speech_action_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Text-to-Speech</a>',
            self.get_text_to_speech_url(obj.id)
        )
    text_to_speech_action_link.short_description = "Text-to-Speech"
    text_to_speech_action_link.allow_tags = True

    def get_inspect_images_url(self, obj_id):
        return f"inspect-images/{obj_id}/"

    def get_text_to_speech_url(self, obj_id):
        return f"text-to-speech/{obj_id}/"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'inspect-images/<int:post_id>/',
                self.admin_site.admin_view(self.inspect_images_view),
                name='posts_post_inspect_images',
            ),
            path(
                'text-to-speech/<int:post_id>/',
                self.admin_site.admin_view(self.text_to_speech_view),
                name='posts_post_text_to_speech',
            ),
        ]
        return custom_urls + urls

    def inspect_images_view(self, request, post_id):
        inspect_all_images_of_posts([post_id])
        self.message_user(request, f"Image inspection triggered for post {post_id}.", messages.SUCCESS)
        return redirect(request.META.get('HTTP_REFERER', '..'))

    def text_to_speech_view(self, request, post_id):
        call_for_text_to_speech_for_posts([post_id])
        self.message_user(request, f"Text-to-speech triggered for post {post_id}.", messages.SUCCESS)
        return redirect(request.META.get('HTTP_REFERER', '..'))

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


def inspect_all_images_of_posts(post_ids):
    from faas.interface import FaasService
    faas = FaasService()
    for post in Post.objects.filter(id__in=post_ids):
        if post.image:
            payload = f'http://192.168.1.7{post.image.url}'
            faas.call_function(
                faas.function_image_inception,
                payload=payload,
                is_async=True,
                callback_hook=settings.FAAS_CALLBACK_URL,
                metadata={'unique_id': post.id}
            )
            faas.call_function(
                faas.function_nsfw_recognition,
                payload=payload,
                is_async=True,
                callback_hook=settings.FAAS_CALLBACK_URL,
                metadata={'unique_id': post.id}
            )


def call_for_text_to_speech_for_posts(post_ids):
    from faas.interface import FaasService
    faas = FaasService()
    for post in Post.objects.filter(id__in=post_ids):
        if post.content:
            payload = {"text": post.content}
            faas.call_function(
                faas.function_text_to_speech,
                payload=payload,
                is_async=True,
                callback_hook=settings.FAAS_CALLBACK_URL,
                metadata={'unique_id': post.id}
            )
