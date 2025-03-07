from django.db import models
from users.models import User

class Program(models.Model):
    PROGRAM_TYPES = (
        ('scholarship', 'Scholarship'),
        ('healthcare', 'Healthcare Assistance'),
        ('housing', 'Housing Support'),
        ('other', 'Other Support'),
    )
    
    name = models.CharField(max_length=200)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField()
    eligibility_criteria = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    max_beneficiaries = models.IntegerField(null=True, blank=True)
    featured_image = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = Programs


class FormField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('file', 'File Upload'),
        ('select', 'Select'),
        ('radio', 'Radio Buttons'),
        ('checkbox', 'Checkbox'),
    )
    
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='form_fields')
    label = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    is_required = models.BooleanField(default=True)
    options = models.JSONField(null=True, blank=True)  # For select, radio, checkbox fields
    help_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']


class Application(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('additional_info', 'Additional Information Required'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    form_data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviewed_applications'
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ApplicationDocument(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='application_documents/')
    document_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.applicant.username} - {self.document_type}"




class ApplicationStatus(models.Model):
    application = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Application Status"

    

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_on_status_change = models.BooleanField(default=True)
    email_on_review = models.BooleanField(default=True)
    email_on_document_request = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification preferences for {self.user.email}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notification Preferences"