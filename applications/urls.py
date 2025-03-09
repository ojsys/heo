from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('programs/', views.ProgramListView.as_view(), name='program_list'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program_detail'),
    path('programs/<int:program_id>/apply/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/review/', views.application_review, name='application_review'),
    path('applications/export/', views.export_applications, name='export_applications'),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    # Analytics and Notification routes
    path('applications/bulk-review/', views.bulk_application_review, name='bulk_application_review'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
]