from django.contrib import admin
from .models import Program, FormField, Application, ApplicationDocument

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