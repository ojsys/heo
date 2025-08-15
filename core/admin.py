from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.html import format_html
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime
import csv
import io
from .models import SiteSettings, SliderImage, GalleryImage, TeamMember, Achievement, WhatWeDo, Student


@admin.register(WhatWeDo)
class WhatWeDoAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Settings', {
            'fields': ('site_name', 'logo', 'favicon', 'primary_color', 'secondary_color')
        }),
        ('Hero Section', {
            'fields': ('hero_title', 'hero_subtitle', 'hero_image')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'contact_address')
        }),
        ('About Page', {
            'fields': ('about_image', 'about_title', 'about_subtitle', 'mission_statement', 'vision_statement')
        }),
        ('What We Do Section', {
            'fields': ('what_we_do_title', 'what_we_do_subtitle')
        }),
        ('Statistics', {
            'fields': ('successful_applications', 'partner_institutions', 
                      'countries_served', 'student_satisfaction')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'caption')

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'position')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    list_editable = ('order',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'school_name', 'current_class', 'scholarship_status', 'scholarship_amount', 'created_at')
    list_filter = ('current_class', 'scholarship_status', 'gender', 'program', 'created_at')
    search_fields = ('full_name', 'school_name', 'guardian_name', 'guardian_phone')
    list_editable = ('scholarship_status',)
    readonly_fields = ('age', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    change_list_template = 'admin/core/student/change_list.html'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'date_of_birth', 'age', 'gender', 'photo', 'phone_number', 'email')
        }),
        ('Educational Information', {
            'fields': ('school_name', 'school_address', 'current_class')
        }),
        ('Scholarship Information', {
            'fields': ('program', 'scholarship_amount', 'scholarship_start_date', 'scholarship_end_date', 'scholarship_status')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_relationship', 'guardian_phone', 'guardian_address')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on new records
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('program', 'created_by')
    
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_suspended']
    
    def mark_as_active(self, request, queryset):
        count = queryset.update(scholarship_status='active')
        self.message_user(request, f'{count} students marked as active.')
    mark_as_active.short_description = "Mark selected students as active"
    
    def mark_as_completed(self, request, queryset):
        count = queryset.update(scholarship_status='completed')
        self.message_user(request, f'{count} students marked as completed.')
    mark_as_completed.short_description = "Mark selected students as completed"
    
    def mark_as_suspended(self, request, queryset):
        count = queryset.update(scholarship_status='suspended')
        self.message_user(request, f'{count} students marked as suspended.')
    mark_as_suspended.short_description = "Mark selected students as suspended"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.bulk_upload_view, name='core_student_bulk_upload'),
            path('download-template/', self.download_template_view, name='core_student_download_template'),
        ]
        return custom_urls + urls
    
    def bulk_upload_view(self, request):
        if request.method == 'GET':
            return render(request, 'admin/core/student/bulk_upload.html')
        
        elif request.method == 'POST':
            return self.process_bulk_upload(request)
    
    def download_template_view(self, request):
        """Download CSV template with proper headers and sample data"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_upload_template.csv"'
        
        writer = csv.writer(response)
        
        # Write header row
        headers = [
            'full_name', 'date_of_birth', 'gender', 'phone_number', 'email',
            'school_name', 'school_address', 'current_class', 'program',
            'scholarship_amount', 'scholarship_start_date', 'scholarship_end_date',
            'scholarship_status', 'guardian_name', 'guardian_relationship',
            'guardian_phone', 'guardian_address', 'notes'
        ]
        writer.writerow(headers)
        
        # Write sample data row with instructions
        sample_data = [
            'John Doe',  # full_name
            '2010-05-15',  # date_of_birth (YYYY-MM-DD)
            'male',  # gender (male/female)
            '+234-xxx-xxx-xxxx',  # phone_number
            'john.doe@email.com',  # email
            'Sample Primary School',  # school_name
            '123 School Street, Lagos, Nigeria',  # school_address
            'primary_5',  # current_class (see choices in model)
            '',  # program (optional, leave empty if none)
            '50000.00',  # scholarship_amount
            '2024-01-15',  # scholarship_start_date (YYYY-MM-DD)
            '2024-12-31',  # scholarship_end_date (optional, YYYY-MM-DD)
            'active',  # scholarship_status (active/completed/suspended/discontinued)
            'Jane Doe',  # guardian_name
            'Mother',  # guardian_relationship
            '+234-xxx-xxx-xxxx',  # guardian_phone
            '456 Home Street, Lagos, Nigeria',  # guardian_address
            'Additional notes about the student'  # notes (optional)
        ]
        writer.writerow(sample_data)
        
        return response
    
    def process_bulk_upload(self, request):
        """Process the uploaded CSV file and create student records"""
        if 'csv_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No file uploaded. Please select a CSV file.',
                'errors': []
            })
        
        csv_file = request.FILES['csv_file']
        
        # Validate file type
        if not csv_file.name.endswith(('.csv', '.xlsx', '.xls')):
            return JsonResponse({
                'success': False,
                'message': 'Invalid file type. Please upload a CSV or Excel file.',
                'errors': []
            })
        
        try:
            # Read file content
            if csv_file.name.endswith('.csv'):
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
            else:
                # Handle Excel files
                try:
                    import pandas as pd
                    df = pd.read_excel(csv_file)
                    # Convert DataFrame to CSV format for processing
                    csv_string = df.to_csv(index=False)
                    io_string = io.StringIO(csv_string)
                    reader = csv.DictReader(io_string)
                except ImportError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Excel files require pandas library. Please use CSV format or install pandas.',
                        'errors': []
                    })
            
            created_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Clean and validate data
                        student_data = self.clean_row_data(row)
                        
                        # Create student instance
                        student = Student(**student_data)
                        student.created_by = request.user
                        student.full_clean()  # Validate model
                        student.save()
                        
                        created_count += 1
                        
                    except ValidationError as e:
                        error_msg = f"Validation error: {', '.join(e.messages)}"
                        errors.append(f"Row {row_num}: {error_msg}")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                # If there are too many errors, rollback transaction
                if len(errors) > created_count:
                    transaction.set_rollback(True)
                    return JsonResponse({
                        'success': False,
                        'message': f'Too many errors encountered. No students were imported.',
                        'errors': errors[:20]  # Limit error display
                    })
            
            if created_count > 0:
                message = f'Successfully imported {created_count} students.'
                if errors:
                    message += f' {len(errors)} rows had errors and were skipped.'
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'errors': errors[:10] if errors else []  # Show first 10 errors
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No students were imported. Please check your file format and data.',
                    'errors': errors[:10]
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'File processing error: {str(e)}',
                'errors': []
            })
    
    def clean_row_data(self, row):
        """Clean and validate row data from CSV"""
        from applications.models import Program
        
        cleaned_data = {}
        
        # Required fields
        cleaned_data['full_name'] = row.get('full_name', '').strip()
        
        # Date fields
        date_fields = ['date_of_birth', 'scholarship_start_date', 'scholarship_end_date']
        for field in date_fields:
            date_str = row.get(field, '').strip()
            if date_str:
                try:
                    # Try different date formats
                    for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            cleaned_data[field] = datetime.strptime(date_str, date_format).date()
                            break
                        except ValueError:
                            continue
                    else:
                        if field == 'date_of_birth' or field == 'scholarship_start_date':
                            raise ValueError(f"Invalid date format for {field}: {date_str}. Use YYYY-MM-DD format.")
                except ValueError as e:
                    raise ValidationError(str(e))
        
        # Choice fields with validation
        gender = row.get('gender', '').strip().lower()
        if gender:
            valid_genders = dict(Student.GENDER_CHOICES)
            if gender not in valid_genders:
                raise ValidationError(f"Invalid gender: {gender}. Must be one of: {', '.join(valid_genders.keys())}")
            cleaned_data['gender'] = gender
        
        current_class = row.get('current_class', '').strip()
        if current_class:
            valid_classes = dict(Student.EDUCATION_LEVEL_CHOICES)
            if current_class not in valid_classes:
                raise ValidationError(f"Invalid class: {current_class}. Must be one of: {', '.join(valid_classes.keys())}")
            cleaned_data['current_class'] = current_class
        
        scholarship_status = row.get('scholarship_status', '').strip().lower()
        if scholarship_status:
            valid_statuses = dict(Student.SCHOLARSHIP_STATUS_CHOICES)
            if scholarship_status not in valid_statuses:
                scholarship_status = 'active'  # Default to active
            cleaned_data['scholarship_status'] = scholarship_status
        
        # Numeric fields
        scholarship_amount = row.get('scholarship_amount', '').strip()
        if scholarship_amount:
            try:
                cleaned_data['scholarship_amount'] = float(scholarship_amount)
            except ValueError:
                raise ValidationError(f"Invalid scholarship amount: {scholarship_amount}. Must be a number.")
        
        # Program lookup
        program_name = row.get('program', '').strip()
        if program_name:
            try:
                program = Program.objects.get(name=program_name)
                cleaned_data['program'] = program
            except Program.DoesNotExist:
                # Just skip the program if not found
                pass
        
        # Other text fields
        text_fields = [
            'phone_number', 'email', 'school_name', 'school_address',
            'guardian_name', 'guardian_relationship', 'guardian_phone', 
            'guardian_address', 'notes'
        ]
        
        for field in text_fields:
            value = row.get(field, '').strip()
            if value:
                cleaned_data[field] = value
        
        return cleaned_data


