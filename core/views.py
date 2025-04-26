from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from core.models import SiteSettings, SliderImage, GalleryImage, TeamMember, Achievement, WhatWeDo
from cms.models import ImpactStory
from .forms import ContactForm
from django.core.mail import send_mail


def home_view(request):
    # Check all images, not just active ones
    all_slider_images = SliderImage.objects.all()
    all_gallery_images = GalleryImage.objects.all()
    
    # Get active images
    slider_images = SliderImage.objects.filter(is_active=True).order_by('order')
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('order')
    
        
    # if all_slider_images.exists():
    #     print("\nSlider Images Details:")
    #     for img in all_slider_images:
    #         print(f"- Title: {img.title}")
    #         print(f"- Active: {img.is_active}")
    #         print(f"- URL: {img.image.url}")
    #         print("---")
    
    # Contact Form
    form = ContactForm()

    context = {
        'slider_images': slider_images,
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.objects.first(),
        'debug': True,
        'DEBUG': settings.DEBUG,
        'all_slider_count': all_slider_images.count(),
        'all_gallery_count': all_gallery_images.count(),
        'form': form,
    }
    context['featured_stories'] = ImpactStory.objects.filter( 
        is_featured=True
    ).order_by('-created_at')[:3]
    
    # Handle form submission
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} ({email})\n\n{message}',
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('core:home')
    
    return render(request, 'pages/landing1.html', context)


def about_view(request):
    context = {
        'team_members': TeamMember.objects.all(),  # If you have a TeamMember model
        'what_we_do_items': WhatWeDo.objects.filter(is_active=True),
    }
    return render(request, 'pages/about.html', context)


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


def gallery_view(request):
    gallery_images = GalleryImage.objects.filter(is_active=True).order_by('category', 'order')
    context = {
        'gallery_images': gallery_images,
        'site_settings': SiteSettings.objects.first()
    }
    return render(request, 'pages/gallery.html', context)


def random_gallery_view(request):
    all_gallery_images = GalleryImage.objects.filter(is_active=True)
    random_ids = sample(list(all_gallery_images.values_list('id', flat=True)), 6)
    gallery_images = all_gallery_images.filter(id__in=random_ids)
    
    html = render_to_string('includes/gallery_items.html', {
        'gallery_images': gallery_images
    })
    
    return JsonResponse({'html': html})


def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)


########## Contact View

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Send email
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} ({email})\n\n{message}',
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'site_settings': SiteSettings.objects.first()
    }
    return render(request, 'pages/contact.html', context)


# View to load more gallery images using AJAX
def load_more_gallery(request):
    page = int(request.GET.get('page', 1))
    per_page = 6  # Number of images to load per request
    offset = page * per_page
    
    # Get the next batch of images
    next_images = GalleryImage.objects.filter(is_active=True).order_by('category', 'order')[offset:offset+per_page]
    
    # Check if there are more images after this batch
    has_more = GalleryImage.objects.filter(is_active=True).count() > (offset + per_page)
    
    # Render the HTML for the new images
    html = render_to_string('pages/includes/gallery_items.html', {
        'gallery_images': next_images
    })
    
    return JsonResponse({
        'html': html,
        'has_more': has_more
    })