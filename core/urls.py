from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('gallery/random/', views.random_gallery_view, name='random_gallery'),
    path('contact/', views.contact_view, name='contact'),
]