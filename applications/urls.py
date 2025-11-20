from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('programs/', views.ProgramListView.as_view(), name='program_list'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program_detail'),
    path('programs/<int:program_id>/application/create/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('programs/<int:program_id>/apply/', views.program_apply, name='program_apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/review/', views.application_review, name='application_review'),
    path('applications/export/', views.export_applications, name='export_applications'),

    # Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    # Analytics and Notification routes
    path('applications/bulk-review/', views.bulk_application_review, name='bulk_application_review'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),

    # Public Beneficiary Showcase Pages
    path('impact/', views.ImpactDashboardView.as_view(), name='impact_dashboard'),
    path('beneficiaries/', views.BeneficiaryShowcaseView.as_view(), name='beneficiary_list'),
    path('beneficiaries/<int:pk>/', views.BeneficiaryDetailView.as_view(), name='beneficiary_detail'),
    path('education/students/', views.education_showcase, name='education_showcase'),
    path('health/beneficiaries/', views.health_showcase, name='health_showcase'),
    path('youth/trainees/', views.youth_showcase, name='youth_showcase'),
    path('housing/beneficiaries/', views.housing_showcase, name='housing_showcase'),
]