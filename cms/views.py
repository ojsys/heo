from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from drf_yasg import openapi
from .models import Category, Page, Media, ImpactStory, Announcement, ContentVersion, BlogPost
from .serializers import (CategorySerializer, PageSerializer, MediaSerializer,
                        ImpactStorySerializer, AnnouncementSerializer)




class PageListView(ListView):
    model = Page
    template_name = 'cms/page_list.html'
    context_object_name = 'pages'
    queryset = Page.objects.filter(is_published=True)

class PageDetailView(DetailView):
    model = Page
    template_name = 'cms/page_detail.html'
    context_object_name = 'page'

class PageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Page
    template_name = 'cms/page_form.html'
    fields = ['title', 'content', 'meta_description', 'featured_image', 'is_published']
    success_url = reverse_lazy('cms:page_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff



class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'cms/announcement_list.html'
    context_object_name = 'announcements'
    queryset = Announcement.objects.filter(is_published=True)



######################### 
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @swagger_auto_schema(
        operation_description="List all categories with pagination",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
                        'results': CategorySerializer(many=True)
                    }
                )
            ),
            400: "Invalid page number",
            401: "Authentication credentials were not provided",
            403: "Permission denied"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get a specific category by slug",
        responses={
            200: CategorySerializer,
            404: "Category not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get children categories of a specific category",
        responses={
            200: CategorySerializer(many=True),
            404: "Category not found"
        }
    )
    @action(detail=True)
    def children(self, request, slug=None):
        category = self.get_object()
        children = category.get_children()
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)

class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'meta_description']

    def get_queryset(self):
        queryset = Page.objects.all() if self.request.user.is_staff else Page.published.filter(visibility='public')
        
        # Handle search using MySQL compatible queries
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(meta_description__icontains=search_query)
            )
        
        return queryset


    @action(detail=True, methods=['post'])
    def publish(self, request, slug=None):
        page = self.get_object()
        page.publish(request.user)
        return Response({'status': 'published'})

    @swagger_auto_schema(
        operation_description="List all pages with pagination and filtering",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title, content", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status", type=openapi.TYPE_STRING, enum=['draft', 'published', 'archived'])
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': PageSerializer(many=True)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Authentication credentials were not provided",
            403: "Permission denied",
            404: "Not found"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new page",
        request_body=PageSerializer,
        responses={
            201: PageSerializer,
            400: openapi.Response(
                description="Validation Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'field_name': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            401: "Authentication required",
            403: "Permission denied"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve page version history",
        responses={
            200: openapi.Response(
                description="Version history",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'version': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            'created_by': openapi.Schema(type=openapi.TYPE_STRING),
                            'comment': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            ),
            404: "Page not found"
        }
    )
    @action(detail=True)
    def versions(self, request, slug=None):
        page = self.get_object()
        versions = ContentVersion.objects.filter(
            content_type__model='page',
            object_id=page.id
        )
        return Response([{
            'version': v.version_number,
            'created_at': v.created_at,
            'created_by': v.created_by.get_full_name() if v.created_by else None,
            'comment': v.comment
        } for v in versions])


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="List media files with pagination",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': MediaSerializer(many=True)
                    }
                )
            ),
            400: "Invalid request",
            413: "File too large",
            415: "Unsupported media type"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Upload or list media files",
        request_body=MediaSerializer,
        responses={
            200: MediaSerializer(many=True),
            400: "Invalid file type or size",
            401: "Unauthorized"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class ImpactStoryViewSet(viewsets.ModelViewSet):
    queryset = ImpactStory.objects.all()
    serializer_class = ImpactStorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'story', 'beneficiary_name']

    @swagger_auto_schema(
        operation_description="List impact stories with filtering",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title, story, beneficiary_name", type=openapi.TYPE_STRING),
            openapi.Parameter('is_featured', openapi.IN_QUERY, description="Filter by featured status", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                        'results': ImpactStorySerializer(many=True)
                    }
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @action(detail=False)
    def featured(self, request):
        featured = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class ImpactStoryListView(ListView):
    model = ImpactStory
    template_name = 'cms/impact_story_list.html'
    context_object_name = 'stories'
    paginate_by = 6  # Show 6 stories per page
    
    def get_queryset(self):
        # Get all published impact stories, ordered by date (newest first)
        return ImpactStory.objects.filter(is_featured=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add featured stories to the context
        context['featured_stories'] = ImpactStory.objects.filter( 
            is_featured=True
        ).order_by('-created_at')[:3]  # Get top 3 featured stories
        
        # Add total count of impact stories
        context['total_stories'] = ImpactStory.objects.filter(is_featured=True).count()
        
        return context

class ImpactStoryDetailView(DetailView):
    model = ImpactStory
    template_name = 'cms/impact_story_detail.html'
    context_object_name = 'story'
    
    def get_queryset(self):
        # Only show published stories
        return ImpactStory.objects.filter(is_featured=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        
        # Get related stories (same category or tags if you have those fields)
        related_stories = ImpactStory.objects.filter(
            is_featured=True
        ).exclude(id=story.id).order_by('-created_at')[:3]
        
        context['related_stories'] = related_stories
        return context


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="List active announcements",
        manual_parameters=[
            openapi.Parameter(
                'active_only',
                openapi.IN_QUERY,
                description="Show only active announcements",
                type=openapi.TYPE_BOOLEAN,
                default=True
            )
        ],
        responses={
            200: AnnouncementSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new announcement",
        request_body=AnnouncementSerializer,
        responses={
            201: AnnouncementSerializer,
            400: "Invalid data",
            401: "Authentication required"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_staff:
            return Announcement.objects.all()
        return Announcement.get_active()


class BlogListView(ListView):
    model = BlogPost
    template_name = 'cms/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')

        # Handle search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        # Handle category filter
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_post'] = BlogPost.objects.filter(
            status='published',
            featured=True,
            published_at__lte=timezone.now()
        ).first()
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'cms/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related posts based on category and tags
        post = self.get_object()
        related_posts = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=post.id)

        if post.category:
            related_posts = related_posts.filter(category=post.category)

        # Increment view count
        post.views_count += 1
        post.save()

        # Get recent posts
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=post.id)[:3]

        context['related_posts'] = related_posts[:3]
        context['categories'] = Category.objects.all()
        return context


class CategoryListView(ListView):
    model = BlogPost
    template_name = 'cms/category_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            category=self.category,
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context



@staff_member_required
@csrf_exempt  # Use csrf_exempt for AJAX uploads
def admin_media_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        title = request.POST.get('title', '')
        
        if not file:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        try:
            # Create a new Media object
            media = Media(
                title=title,
                file=file,
                uploaded_by=request.user
            )
            media.save()
            
            return JsonResponse({
                'success': True,
                'id': media.id,
                'title': media.title,
                'url': media.file.url
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # For GET requests, render the upload template
    return render(request, 'admin/cms/media/upload.html')