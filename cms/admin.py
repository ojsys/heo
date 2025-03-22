from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ('title', 'file_preview', 'uploaded_at', 'uploaded_by')
    list_filter = ('uploaded_at', 'uploaded_by')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('file_preview',)
    fieldsets = (
        (None, {
            'fields': ('title', 'file', 'alt_text', 'file_preview')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        if obj.file and obj.get_file_extension() in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 300px;" />', obj.file.url)
        elif obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.get_file_extension().upper())
        return "No file"
    
    file_preview.short_description = 'Preview'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set the uploaded_by when creating a new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('css/admin/media_upload.css',)
        }
        js = ('js/admin/media_upload.js',)
# class MediaAdmin(admin.ModelAdmin):
#     list_display = ('title', 'file_preview', 'uploaded_by', 'uploaded_at')
#     list_filter = ('uploaded_at',)
#     search_fields = ('title', 'alt_text')
#     readonly_fields = ('file_preview', 'uploaded_at')
#     fields = ('title', 'file', 'alt_text', 'file_preview', 'uploaded_at')

#     def file_preview(self, obj):
#         if obj.file and obj.file.url:
#             file_ext = obj.get_file_extension()
#             if file_ext and file_ext.lower() in ['jpg', 'jpeg', 'png', 'gif']:
#                 return format_html('<img src="{}" style="max-height: 50px;"/>', obj.file.url)
#             return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
#         return "No file"
#     file_preview.short_description = 'Preview'

#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.uploaded_by = request.user
#         super().save_model(request, obj, form, change)

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

