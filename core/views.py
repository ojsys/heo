from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from core.models import SiteSettings, SliderImage, GalleryImage, TeamMember, Achievement, WhatWeDo, Student
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


# Student Views
def student_list_view(request):
    """Public view to display scholarship students"""
    students = Student.objects.filter(scholarship_status='active').select_related('program')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(full_name__icontains=search_query) |
            Q(school_name__icontains=search_query) |
            Q(current_class__icontains=search_query)
        )
    
    # Filter by class
    class_filter = request.GET.get('class', '')
    if class_filter:
        students = students.filter(current_class=class_filter)
    
    # Filter by school
    school_filter = request.GET.get('school', '')
    if school_filter:
        students = students.filter(school_name__icontains=school_filter)
    
    # Get unique schools and classes for filters
    schools = Student.objects.filter(scholarship_status='active').values_list('school_name', flat=True).distinct().order_by('school_name')
    classes = Student.objects.filter(scholarship_status='active').values_list('current_class', flat=True).distinct().order_by('current_class')
    
    # Pagination
    paginator = Paginator(students, 12)  # 12 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_students': Student.objects.filter(scholarship_status='active').count(),
        'total_schools': Student.objects.filter(scholarship_status='active').values('school_name').distinct().count(),
        'total_amount': Student.objects.filter(scholarship_status='active').aggregate(total=Sum('scholarship_amount'))['total'] or 0,
    }
    
    context = {
        'students': page_obj,
        'search_query': search_query,
        'class_filter': class_filter,
        'school_filter': school_filter,
        'schools': schools,
        'classes': classes,
        'stats': stats,
        'site_settings': SiteSettings.objects.first(),
    }
    
    return render(request, 'core/student_list.html', context)


def student_detail_view(request, student_id):
    """Public view to display individual student details"""
    student = get_object_or_404(Student, id=student_id, scholarship_status='active')
    
    context = {
        'student': student,
        'site_settings': SiteSettings.objects.first(),
    }
    
    return render(request, 'core/student_detail.html', context)


@staff_member_required
def student_dashboard_view(request):
    """Admin dashboard for student statistics"""
    # Get statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(scholarship_status='active').count()
    completed_students = Student.objects.filter(scholarship_status='completed').count()
    suspended_students = Student.objects.filter(scholarship_status='suspended').count()
    
    # Total scholarship amount
    total_amount = Student.objects.filter(scholarship_status='active').aggregate(
        total=Sum('scholarship_amount')
    )['total'] or 0
    
    # Students by class
    students_by_class = Student.objects.filter(scholarship_status='active').values(
        'current_class'
    ).annotate(count=Count('id')).order_by('current_class')
    
    # Students by school
    students_by_school = Student.objects.filter(scholarship_status='active').values(
        'school_name'
    ).annotate(count=Count('id')).order_by('-count')[:10]  # Top 10 schools
    
    # Recent additions
    recent_students = Student.objects.select_related('program', 'created_by').order_by('-created_at')[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'completed_students': completed_students,
        'suspended_students': suspended_students,
        'total_amount': total_amount,
        'students_by_class': students_by_class,
        'students_by_school': students_by_school,
        'recent_students': recent_students,
        'site_settings': SiteSettings.objects.first(),
    }
    
    return render(request, 'core/student_dashboard.html', context)