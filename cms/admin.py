from django.contrib import admin
from .models import Page, Media, ImpactStory, Announcement, BlogPost, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('title',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ImpactStory)
class ImpactStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'beneficiary_name', 'program', 'is_featured')
    list_filter = ('is_featured', 'program', 'created_at')
    search_fields = ('title', 'beneficiary_name', 'story')

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'publish_date', 'expiry_date')
    list_filter = ('is_published', 'publish_date')
    search_fields = ('title', 'content')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'featured')
    list_filter = ('status', 'category', 'created_at', 'featured')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_editable = ('status', 'featured')
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category', 'featured_image', 'excerpt', 'content')
        }),
        ('Tags', {
            'fields': ('tags',),
        }),
        ('Publication', {
            'fields': ('status', 'published_at', 'featured'),
        }),
    )