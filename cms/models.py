from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db.models import Q
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


User = get_user_model


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            status='published',
            published_at__lte=timezone.now()
        )
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('cms:category_detail', kwargs={'slug': self.slug})

    def get_children(self):
        return self.category_set.all()

    def get_ancestors(self):
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors[::-1]

class Media(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='media/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    alt_text = models.CharField(max_length=255, blank=True)

    def compress_image(self, image_file):
        img = Image.open(image_file)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Calculate compression quality
        img_io = BytesIO()
        quality = 95
        img.save(img_io, format='JPEG', quality=quality, optimize=True)
        
        # Keep reducing quality until file size is under 200KB
        while img_io.tell() > 200 * 1024 and quality > 10:
            img_io = BytesIO()
            quality -= 5
            img.save(img_io, format='JPEG', quality=quality, optimize=True)
        
        img_io.seek(0)
        return ContentFile(img_io.getvalue())

    def save(self, *args, **kwargs):
        if self.file and not self.title:
            filename = os.path.splitext(self.file.name)[0]
            self.title = filename.replace('-', ' ').replace('_', ' ').title()
            if not self.alt_text:
                self.alt_text = self.title

        # Compress image if it's an image file
        if self.file and not self.file._committed:
            try:
                file_ext = self.file.name.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                    compressed_image = self.compress_image(self.file)
                    self.file.save(
                        f"{self.file.name.rsplit('.', 1)[0]}_compressed.jpg",
                        compressed_image,
                        save=False
                    )
            except Exception as e:
                # If compression fails, continue with original file
                pass

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Media'

    def __str__(self):
        return self.title

    def get_file_url(self):
        return self.file.url if self.file else None

    def get_file_extension(self):
        return self.file.name.split('.')[-1] if self.file else None


class Page(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    content = models.TextField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    meta_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft')
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pages')
    featured_image = models.ForeignKey('Media', on_delete=models.SET_NULL, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_pages')
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='published_pages')
    is_featured = models.BooleanField(default=False)
    # Remove the SearchVectorField
    # search_vector = SearchVectorField(null=True)  # Remove this line
    
    
    
    # Add template choice field
    template = models.CharField(
        max_length=100,
        choices=[
            ('default', 'Default Template'),
            ('sidebar', 'With Sidebar'),
            ('fullwidth', 'Full Width'),
            ('landing', 'Landing Page')
        ],
        default='default'
    )
    
    # Add ordering field
    order = models.IntegerField(default=0)
    
    # Add visibility options
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('members', 'Members Only')
        ],
        default='public'
    )

    objects = models.Manager()
    published = PublishedManager()

    def create_version(self, user=None, comment=''):
        content_type = ContentType.objects.get_for_model(self)
        latest_version = ContentVersion.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).order_by('-version_number').first()
        
        version_number = 1 if not latest_version else latest_version.version_number + 1
        
        version_data = {
            'title': self.title,
            'content': self.content,
            'meta_description': self.meta_description,
            'status': self.status,
            'template': self.template,
            'visibility': self.visibility
        }

        ContentVersion.objects.create(
            content_type=content_type,
            object_id=self.id,
            version_number=version_number,
            content_data=version_data,
            created_by=user,
            comment=comment
        )

    def restore_version(self, version_number):
        version = ContentVersion.objects.get(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            version_number=version_number
        )
        
        for key, value in version.content_data.items():
            setattr(self, key, value)
        self.save()

    def get_absolute_url(self):
        return reverse('cms:page_detail', kwargs={'slug': self.slug})

    def publish(self, user=None):
        self.status = 'published'
        self.published_at = timezone.now()
        self.published_by = user
        self.is_published = True
        self.save()

    def unpublish(self):
        self.status = 'draft'
        self.is_published = False
        self.save()

    def clean(self):
        if self.status == 'published' and not self.published_at:
            raise ValidationError('Published pages must have a publication date.')
        if self.visibility == 'members' and self.status == 'published':
            if not self.category:
                raise ValidationError('Members-only pages must belong to a category.')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def update_search_vector(self):
        self.search_vector = SearchVector('title', weight='A') + \
                           SearchVector('content', weight='B') + \
                           SearchVector('meta_description', weight='C')
        self.save(update_fields=['search_vector'])

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(meta_description__icontains=query)
        ).distinct()

    class Meta:
        ordering = ['order', '-published_at']
        verbose_name_plural = "Pages"        


            

class ImpactStory(models.Model):
    title = models.CharField(max_length=200)
    beneficiary_name = models.CharField(max_length=100)
    story = models.TextField()
    image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)
    program = models.ForeignKey('applications.Program', on_delete=models.SET_NULL, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True)


    def update_search_vector(self):
        self.search_vector = SearchVector('title', weight='A') + \
                           SearchVector('story', weight='B') + \
                           SearchVector('beneficiary_name', weight='C')
        self.save(update_fields=['search_vector'])

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(story__icontains=query) |
            Q(beneficiary_name__icontains=query)
        ).distinct()

    class Meta:
        verbose_name_plural = 'Impact Stories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:impact_story_detail', kwargs={'pk': self.pk})

    def clean(self):
        if not self.program:
            raise ValidationError('Impact story must be associated with a program.')
    

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    published = PublishedManager()
    class Meta:
        verbose_name_plural = 'Announcements'

    def is_active(self):
        now = timezone.now()
        if not self.is_published:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return self.publish_date <= now

    def clean(self):
        if self.expiry_date and self.expiry_date < self.publish_date:
            raise ValidationError('Expiry date must be after publish date.')

    @classmethod
    def get_active(cls):
        return cls.published.filter(
            is_published=True,
            publish_date__lte=timezone.now()
        ).exclude(
            expiry_date__lt=timezone.now()
        )

    @classmethod
    def search(cls, query):
        return cls.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).distinct()


# Tracking Content Version
class ContentVersion(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    version_number = models.PositiveIntegerField()
    content_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"Version {self.version_number} of {self.content_object}"


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    excerpt = models.TextField(max_length=500, help_text="A short description that appears in blog listings")
    content = RichTextUploadingField()
    tags = TaggableManager()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)