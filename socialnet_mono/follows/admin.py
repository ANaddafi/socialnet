from django.contrib import admin
from .models import Follow

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target', 'created_at')
    search_fields = ('user__username', 'target__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'target', 'created_at')}),
    )
