from django.contrib import admin
from .models import Program, FormField, Application, ApplicationDocument

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'program_type', 'start_date', 'end_date', 'is_active')
    list_filter = ('program_type', 'is_active', 'start_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'

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