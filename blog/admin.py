from django.contrib import admin
from django.utils import timezone
from .models import Post, Category, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'published_at', 'reading_time', 'views']
    list_filter = ['status', 'category', 'tags']
    search_fields = ['title', 'excerpt', 'body']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['reading_time', 'views', 'created_at', 'updated_at']
    fieldsets = [
        (None, {'fields': ['title', 'slug', 'status']}),
        ('Content', {'fields': ['excerpt', 'body', 'cover_image']}),
        ('Taxonomy', {'fields': ['category', 'tags']}),
        ('Stats', {'fields': ['reading_time', 'views', 'published_at', 'created_at', 'updated_at']}),
    ]
    actions = ['publish_posts']

    @admin.action(description='Publish selected posts')
    def publish_posts(self, request, queryset):
        updated = queryset.filter(status='draft').update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} post(s) published.')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
