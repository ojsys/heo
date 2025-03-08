from rest_framework import serializers
from .models import Category, Page, Media, ImpactStory, Announcement

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'order']

class MediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = ['id', 'title', 'file', 'file_url', 'file_type', 'alt_text', 'mime_type']

    def get_file_url(self, obj):
        return obj.get_file_url()

class PageSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    featured_image = MediaSerializer(read_only=True)

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'category', 'status', 
                 'featured_image', 'template', 'visibility', 'published_at']

class ImpactStorySerializer(serializers.ModelSerializer):
    image = MediaSerializer(read_only=True)

    class Meta:
        model = ImpactStory
        fields = ['id', 'title', 'beneficiary_name', 'story', 'image', 
                 'program', 'is_featured', 'created_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'is_published', 'publish_date', 
                 'expiry_date', 'is_active']