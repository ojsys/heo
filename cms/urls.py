from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views

app_name = 'cms'

schema_view = get_schema_view(
    openapi.Info(
        title="CMS API",
        default_version='v1',
        description="API documentation for the CMS system",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticatedOrReadOnly],
)

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'pages', views.PageViewSet, basename='page')
router.register(r'media', views.MediaViewSet)
router.register(r'impact-stories', views.ImpactStoryViewSet)
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', views.PageListView.as_view(), name='page_list'),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #### API Route
    path('api/', include(router.urls)),

    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('page/create/', views.PageCreateView.as_view(), name='page_create'),
    path('impact-stories/', views.ImpactStoryListView.as_view(), name='impact_story_list'),
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),

    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/category/<slug:slug>/', views.CategoryListView.as_view(), name='blog_category'),
]