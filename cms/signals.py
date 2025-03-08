from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.urls import reverse
from .models import Page, Category, Announcement, ImpactStory

@receiver([post_save, post_delete], sender=Page)
def clear_page_cache(sender, instance, **kwargs):
    cache.delete(f'page_{instance.slug}')
    cache.delete('pages_list')
    if instance.category:
        cache.delete(f'category_{instance.category.slug}')

@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache.delete(f'category_{instance.slug}')
    cache.delete('categories_list')

@receiver([post_save, post_delete], sender=Announcement)
def clear_announcement_cache(sender, instance, **kwargs):
    cache.delete('active_announcements')

@receiver([post_save, post_delete], sender=ImpactStory)
def clear_impact_story_cache(sender, instance, **kwargs):
    cache.delete('featured_impact_stories')
    if instance.program:
        cache.delete(f'program_impact_stories_{instance.program.id}')