from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from core.models import SiteSettings, SliderImage, GalleryImage

def home_view(request):
    # Check all images, not just active ones
    all_slider_images = SliderImage.objects.all()
    all_gallery_images = GalleryImage.objects.all()
    
    # Get active images
    slider_images = SliderImage.objects.filter(is_active=True).order_by('order')
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')
    
    print("\n=== Debug Information ===")
    print(f"Total Slider Images (including inactive): {all_slider_images.count()}")
    print(f"Active Slider Images: {slider_images.count()}")
    print(f"Total Gallery Images (including inactive): {all_gallery_images.count()}")
    print(f"Active Gallery Images: {gallery_images.count()}")
    
    if all_slider_images.exists():
        print("\nSlider Images Details:")
        for img in all_slider_images:
            print(f"- Title: {img.title}")
            print(f"- Active: {img.is_active}")
            print(f"- URL: {img.image.url}")
            print("---")
    
    context = {
        'slider_images': slider_images,
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.objects.first(),
        'debug': True,
        'DEBUG': settings.DEBUG,
        'all_slider_count': all_slider_images.count(),
        'all_gallery_count': all_gallery_images.count(),
    }
    
    return render(request, 'pages/landing.html', context)


def about_view(request):
    return render(request, 'pages/about.html')


def contact_view(request):
    return render(request, 'pages/contact.html')

@staff_member_required
def dashboard_view(request):
    context = {
        'settings': SiteSettings.get_settings(),
        'total_users': User.objects.count(),
        'total_applications': Application.objects.count()
    }
    return render(request, 'core/dashboard.html', context)



def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)