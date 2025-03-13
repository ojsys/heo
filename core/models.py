from django.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='HEO Foundation')
    logo = models.ImageField(upload_to='site/', null=True, blank=True)
    favicon = models.ImageField(upload_to='site/', null=True, blank=True)
    
    about_image = models.ImageField(upload_to='site/about/', null=True, blank=True)
    about_title = models.CharField(max_length=200, default="About Us")
    about_subtitle = models.TextField(blank=True)
    mission_statement = models.TextField(blank=True)
    vision_statement = models.TextField(blank=True)

    primary_color = models.CharField(max_length=7, default='#0d6efd', help_text='Hex color code')
    secondary_color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')
    
    # Statistics
    successful_applications = models.CharField(max_length=20, blank=True)
    partner_institutions = models.CharField(max_length=20, blank=True)
    countries_served = models.CharField(max_length=20, blank=True)
    student_satisfaction = models.CharField(max_length=20, blank=True)

    # What We Do Section
    what_we_do_title = models.CharField(max_length=200, default="What We Do")
    what_we_do_subtitle = models.TextField(blank=True)

    # Hero Section
    hero_title = models.CharField(max_length=200, default='Empowering Dreams Through Education')
    hero_subtitle = models.TextField(default='HEO Foundation provides educational opportunities and support to ambitious students worldwide.')
    hero_image = models.ImageField(upload_to='site/', null=True, blank=True)
    
    # Contact Information
    contact_email = models.EmailField(default='info@heofoundation.org')
    contact_phone = models.CharField(max_length=20, default='+1 234 567 8900')
    contact_address = models.TextField(default='123 Education Street')
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True, help_text='SEO meta description')
    meta_keywords = models.CharField(max_length=255, blank=True, help_text='SEO keywords (comma-separated)')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def clean(self):
        if SiteSettings.objects.exists() and not self.pk:
            raise ValidationError('Only one Site Settings instance is allowed.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        cache.delete('site_settings')

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        settings = cache.get('site_settings')
        if not settings:
            settings = cls.objects.first()
            if not settings:
                settings = cls.objects.create()
            cache.set('site_settings', settings)
        return settings



class SliderImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='slider/')
    caption = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Slider Image'
        verbose_name_plural = 'Slider Images'

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=100, choices=[
        ('education', 'Education'),
        ('healthcare', 'Healthcare'),
        ('housing', 'Housing'),
        ('community', 'Community'),
    ])
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team/', null=True, blank=True)
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Achievement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class WhatWeDo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class name (e.g., fa-search)")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title




