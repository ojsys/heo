from django.urls import path
from . import views

app_name = 'cms'

urlpatterns = [
    path('', views.PageListView.as_view(), name='page_list'),
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('page/create/', views.PageCreateView.as_view(), name='page_create'),
    path('impact-stories/', views.ImpactStoryListView.as_view(), name='impact_story_list'),
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
]