from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.html import format_html
import csv
import io

from .models import (
    Program, FormField, Application, ApplicationDocument,
    Beneficiary, BeneficiarySupport, EducationProfile,
    HealthProfile, YouthProfile, HousingProfile,
    ApplicationStatus, NotificationPreference
)
from .signals import create_beneficiary_from_application

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 3
    fields = ('label', 'field_type', 'is_required', 'options', 'help_text', 'order')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'program_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('program_type', 'is_active', 'start_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    inlines = [FormFieldInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'program_type', 'description', 'eligibility_criteria')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'application_deadline')
        }),
        ('Settings', {
            'fields': ('is_active', 'max_beneficiaries', 'featured_image')
        }),
    )

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    ordering = ['order']

class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 1

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'program', 'status', 'submitted_at')
    list_filter = ('status', 'program', 'submitted_at')
    search_fields = ('applicant__username', 'applicant__email', 'review_notes')
    inlines = [ApplicationDocumentInline]
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.reviewed_by and obj.status in ['approved', 'rejected']:
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['approve_and_create_beneficiary', 'mark_under_review', 'mark_rejected']

    def approve_and_create_beneficiary(self, request, queryset):
        """Approve applications and create beneficiary records"""
        created_count = 0
        for application in queryset.filter(status__in=['submitted', 'under_review']):
            application.status = 'approved'
            application.reviewed_by = request.user
            application.save()

            # Create beneficiary if not exists
            if not hasattr(application, 'beneficiary'):
                create_beneficiary_from_application(
                    application,
                    beneficiary_type=None,
                    created_by=request.user
                )
                created_count += 1

        messages.success(
            request,
            f'{queryset.count()} applications approved, {created_count} beneficiaries created.'
        )
    approve_and_create_beneficiary.short_description = "Approve and create beneficiary"

    def mark_under_review(self, request, queryset):
        queryset.update(status='under_review', reviewed_by=request.user)
        messages.success(request, f'{queryset.count()} applications marked as under review.')
    mark_under_review.short_description = "Mark as under review"

    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected', reviewed_by=request.user)
        messages.success(request, f'{queryset.count()} applications rejected.')
    mark_rejected.short_description = "Mark as rejected"


# Beneficiary Profile Inlines
class EducationProfileInline(admin.StackedInline):
    model = EducationProfile
    extra = 0
    max_num = 1
    fieldsets = (
        ('School Information', {
            'fields': (
                'institution_type', 'school_name', 'school_address',
                'current_class', 'course_of_study'
            )
        }),
        ('Scholarship Details', {
            'fields': (
                'scholarship_amount', 'tuition_covered',
                'books_covered', 'accommodation_covered'
            )
        }),
        ('Academic Performance', {
            'fields': ('last_result', 'academic_standing')
        }),
        ('School Contact', {
            'fields': ('teacher_name', 'teacher_phone'),
            'classes': ['collapse']
        }),
    )


class HealthProfileInline(admin.StackedInline):
    model = HealthProfile
    extra = 0
    max_num = 1
    fieldsets = (
        ('Medical Information', {
            'fields': (
                'medical_condition', 'condition_description',
                'treatment_type', 'treatment_status'
            )
        }),
        ('Healthcare Provider', {
            'fields': (
                'hospital_name', 'hospital_address',
                'doctor_name', 'doctor_phone'
            )
        }),
        ('Treatment Timeline', {
            'fields': ('treatment_start_date', 'treatment_end_date')
        }),
        ('Costs', {
            'fields': ('total_medical_cost', 'amount_covered')
        }),
        ('Outcome', {
            'fields': ('outcome_notes',),
            'classes': ['collapse']
        }),
    )


class YouthProfileInline(admin.StackedInline):
    model = YouthProfile
    extra = 0
    max_num = 1
    fieldsets = (
        ('Training Information', {
            'fields': (
                'skill_type', 'specific_skill', 'training_provider',
                'training_location', 'training_duration',
                'training_start_date', 'training_end_date'
            )
        }),
        ('Certification', {
            'fields': ('certification_obtained', 'certificate_name')
        }),
        ('Outcome', {
            'fields': (
                'employment_status', 'business_started',
                'business_name', 'employer_name'
            )
        }),
        ('Support', {
            'fields': ('startup_grant_amount', 'equipment_provided')
        }),
    )


class HousingProfileInline(admin.StackedInline):
    model = HousingProfile
    extra = 0
    max_num = 1
    fieldsets = (
        ('Support Type', {
            'fields': ('support_type', 'support_description')
        }),
        ('Property Information', {
            'fields': ('property_address', 'property_type')
        }),
        ('Rent Assistance', {
            'fields': (
                'landlord_name', 'landlord_phone',
                'rent_amount_monthly', 'rent_duration_months'
            ),
            'classes': ['collapse']
        }),
        ('Costs & Status', {
            'fields': (
                'total_project_cost', 'amount_covered',
                'project_status', 'completion_date'
            )
        }),
        ('Family Information', {
            'fields': ('family_size', 'number_of_children')
        }),
    )


class BeneficiarySupportInline(admin.TabularInline):
    model = BeneficiarySupport
    extra = 1
    fields = ('support_type', 'amount', 'date', 'description', 'receipt')
    readonly_fields = ('created_at',)


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'beneficiary_type', 'program', 'status',
        'start_date', 'total_support', 'photo_preview'
    )
    list_filter = ('beneficiary_type', 'status', 'gender', 'program', 'show_on_website')
    search_fields = ('full_name', 'email', 'phone_number', 'guardian_name')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at', 'total_support_display')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'beneficiary_type', 'application', 'program', 'user',
                'status', 'show_on_website'
            )
        }),
        ('Personal Details', {
            'fields': (
                'full_name', 'date_of_birth', 'gender', 'photo',
                'phone_number', 'email', 'address', 'state', 'lga'
            )
        }),
        ('Guardian/Emergency Contact', {
            'fields': (
                'guardian_name', 'guardian_relationship',
                'guardian_phone', 'guardian_address'
            ),
            'classes': ['collapse']
        }),
        ('Support Period', {
            'fields': ('start_date', 'end_date', 'total_support_display')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ['collapse']
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

    def get_inlines(self, request, obj=None):
        """Return appropriate inline based on beneficiary type"""
        inlines = [BeneficiarySupportInline]

        if obj:
            if obj.beneficiary_type == 'education':
                inlines.insert(0, EducationProfileInline)
            elif obj.beneficiary_type == 'health':
                inlines.insert(0, HealthProfileInline)
            elif obj.beneficiary_type == 'youth':
                inlines.insert(0, YouthProfileInline)
            elif obj.beneficiary_type == 'housing':
                inlines.insert(0, HousingProfileInline)

        return inlines

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;"/>',
                obj.photo.url
            )
        return "-"
    photo_preview.short_description = "Photo"

    def total_support(self, obj):
        return f"₦{obj.total_support_amount:,.2f}"
    total_support.short_description = "Total Support"

    def total_support_display(self, obj):
        return f"₦{obj.total_support_amount:,.2f}"
    total_support_display.short_description = "Total Support Amount"

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    actions = ['mark_active', 'mark_completed', 'mark_suspended', 'export_to_csv']

    def mark_active(self, request, queryset):
        queryset.update(status='active')
        messages.success(request, f'{queryset.count()} beneficiaries marked as active.')
    mark_active.short_description = "Mark as active"

    def mark_completed(self, request, queryset):
        queryset.update(status='completed', end_date=timezone.now().date())
        messages.success(request, f'{queryset.count()} beneficiaries marked as completed.')
    mark_completed.short_description = "Mark as completed"

    def mark_suspended(self, request, queryset):
        queryset.update(status='suspended')
        messages.success(request, f'{queryset.count()} beneficiaries marked as suspended.')
    mark_suspended.short_description = "Mark as suspended"

    def export_to_csv(self, request, queryset):
        """Export selected beneficiaries to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="beneficiaries.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Full Name', 'Type', 'Program', 'Status', 'Gender',
            'Phone', 'Email', 'Start Date', 'Total Support'
        ])

        for b in queryset:
            writer.writerow([
                b.full_name,
                b.get_beneficiary_type_display(),
                b.program.name if b.program else '',
                b.get_status_display(),
                b.get_gender_display(),
                b.phone_number,
                b.email,
                b.start_date,
                b.total_support_amount
            ])

        return response
    export_to_csv.short_description = "Export to CSV"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='beneficiary_dashboard'),
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='beneficiary_bulk_upload'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Dashboard with statistics"""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Beneficiary Dashboard',
            'total_beneficiaries': Beneficiary.objects.count(),
            'active_beneficiaries': Beneficiary.objects.filter(status='active').count(),
            'by_type': Beneficiary.objects.values('beneficiary_type').annotate(count=Count('id')),
            'total_disbursed': BeneficiarySupport.objects.aggregate(total=Sum('amount'))['total'] or 0,
            'recent_beneficiaries': Beneficiary.objects.order_by('-created_at')[:10],
        }
        return render(request, 'admin/applications/beneficiary/dashboard.html', context)

    def bulk_upload_view(self, request):
        """Bulk upload beneficiaries from CSV"""
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']

            try:
                decoded_file = csv_file.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(decoded_file))

                created_count = 0
                errors = []

                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Get program
                        program = None
                        if row.get('program'):
                            program = Program.objects.filter(name__icontains=row['program']).first()

                        beneficiary = Beneficiary.objects.create(
                            beneficiary_type=row.get('type', 'education'),
                            program=program,
                            full_name=row.get('full_name', ''),
                            gender=row.get('gender', 'male').lower(),
                            phone_number=row.get('phone', ''),
                            email=row.get('email', ''),
                            address=row.get('address', ''),
                            guardian_name=row.get('guardian_name', ''),
                            guardian_phone=row.get('guardian_phone', ''),
                            status='active',
                            start_date=row.get('start_date') or timezone.now().date(),
                            created_by=request.user,
                        )
                        created_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

                if created_count:
                    messages.success(request, f'Successfully created {created_count} beneficiaries.')
                if errors:
                    messages.warning(request, f'Errors: {"; ".join(errors[:5])}')

                return redirect('admin:applications_beneficiary_changelist')

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Bulk Upload Beneficiaries',
        }
        return render(request, 'admin/applications/beneficiary/bulk_upload.html', context)


@admin.register(BeneficiarySupport)
class BeneficiarySupportAdmin(admin.ModelAdmin):
    list_display = ('beneficiary', 'support_type', 'amount', 'date', 'created_by')
    list_filter = ('support_type', 'date', 'beneficiary__beneficiary_type')
    search_fields = ('beneficiary__full_name', 'description')
    date_hierarchy = 'date'
    autocomplete_fields = ['beneficiary']

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('application', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('application__applicant__email', 'notes')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_on_status_change', 'email_on_review', 'email_on_document_request')
    list_filter = ('email_on_status_change', 'email_on_review')
    search_fields = ('user__email',)