from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/random/', views.random_gallery_view, name='random_gallery'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('gallery/load-more/', views.load_more_gallery, name='load_more_gallery'),
    
    # Student URLs
    path('students/', views.student_list_view, name='student-list'),
    path('students/<int:student_id>/', views.student_detail_view, name='student-detail'),
    path('admin/student-dashboard/', views.student_dashboard_view, name='student-dashboard'),
]