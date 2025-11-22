from django.db import models
from django.conf import settings
from ckeditor_uploader.fields import RichTextUploadingField

from users.models import User

class Program(models.Model):
    PROGRAM_TYPES = (
        ('scholarship', 'Scholarship'),
        ('healthcare', 'Healthcare Assistance'),
        ('youth', 'Youth Empowerment'),
        ('housing', 'Housing Support'),
        ('other', 'Other Support'),
    )

    name = models.CharField(max_length=200)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    description = RichTextUploadingField(help_text="Detailed description of the program")
    eligibility_criteria = RichTextUploadingField(help_text="Who can apply and requirements")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    max_beneficiaries = models.IntegerField(null=True, blank=True)
    featured_image = models.ForeignKey('cms.Media', on_delete=models.SET_NULL, null=True, blank=True)
    
    # New fields for enhanced program detail page
    location = models.CharField(max_length=200, blank=True, null=True)
    application_start_date = models.DateField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    notification_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., '6 months', '1 year'")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Programs"


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
    application_deadline = models.DateField(null=True, blank=True, help_text="Deadline for applications")
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
        verbose_name_plural = "Notification Preferences"


class Beneficiary(models.Model):
    """Universal beneficiary model for all program types"""
    BENEFICIARY_TYPES = (
        ('education', 'Education/Scholarship'),
        ('health', 'Healthcare'),
        ('youth', 'Youth Empowerment'),
        ('housing', 'Housing Support'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('discontinued', 'Discontinued'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    # Core fields
    beneficiary_type = models.CharField(max_length=20, choices=BENEFICIARY_TYPES)
    application = models.OneToOneField(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiary'
    )
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, related_name='beneficiaries')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiary_records'
    )

    # Personal Information
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    state = models.CharField(max_length=100, blank=True)
    lga = models.CharField(max_length=100, blank=True, verbose_name="LGA")

    # Guardian/Emergency Contact
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_address = models.TextField(blank=True)

    # Media
    photo = models.ImageField(upload_to='beneficiaries/', null=True, blank=True)

    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    # Privacy
    show_on_website = models.BooleanField(default=True, help_text="Display this beneficiary on public pages")

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='beneficiaries_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Beneficiaries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.get_beneficiary_type_display()}"

    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def total_support_amount(self):
        return self.support_records.aggregate(
            total=models.Sum('amount')
        )['total'] or 0


class BeneficiarySupport(models.Model):
    """Track individual support/disbursements to beneficiaries"""
    SUPPORT_TYPES = (
        ('payment', 'Cash Payment'),
        ('tuition', 'Tuition Payment'),
        ('supplies', 'Supplies/Materials'),
        ('medical', 'Medical Expenses'),
        ('training', 'Training Fee'),
        ('equipment', 'Equipment'),
        ('rent', 'Rent Payment'),
        ('other', 'Other'),
    )

    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='support_records'
    )
    support_type = models.CharField(max_length=20, choices=SUPPORT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    receipt = models.FileField(upload_to='support_receipts/', null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Beneficiary Support Records"

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.get_support_type_display()} - ₦{self.amount}"


class EducationProfile(models.Model):
    """Education-specific details for scholarship beneficiaries"""
    EDUCATION_LEVELS = (
        ('primary_1', 'Primary 1'),
        ('primary_2', 'Primary 2'),
        ('primary_3', 'Primary 3'),
        ('primary_4', 'Primary 4'),
        ('primary_5', 'Primary 5'),
        ('primary_6', 'Primary 6'),
        ('jss_1', 'JSS 1'),
        ('jss_2', 'JSS 2'),
        ('jss_3', 'JSS 3'),
        ('sss_1', 'SSS 1'),
        ('sss_2', 'SSS 2'),
        ('sss_3', 'SSS 3'),
        ('nd_1', 'ND 1'),
        ('nd_2', 'ND 2'),
        ('hnd_1', 'HND 1'),
        ('hnd_2', 'HND 2'),
        ('year_1', '100 Level'),
        ('year_2', '200 Level'),
        ('year_3', '300 Level'),
        ('year_4', '400 Level'),
        ('year_5', '500 Level'),
        ('year_6', '600 Level'),
        ('postgraduate', 'Postgraduate'),
    )

    INSTITUTION_TYPES = (
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('polytechnic', 'Polytechnic'),
        ('university', 'University'),
        ('college', 'College of Education'),
        ('vocational', 'Vocational Institute'),
    )

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='education_profile'
    )

    # School Information
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES)
    school_name = models.CharField(max_length=300)
    school_address = models.TextField(blank=True)
    current_class = models.CharField(max_length=20, choices=EDUCATION_LEVELS)
    course_of_study = models.CharField(max_length=200, blank=True, help_text="For higher institutions")

    # Scholarship Details
    scholarship_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tuition_covered = models.BooleanField(default=False)
    books_covered = models.BooleanField(default=False)
    accommodation_covered = models.BooleanField(default=False)

    # Academic Performance
    last_result = models.CharField(max_length=100, blank=True, help_text="e.g., 'First Class', '3.5 GPA', 'A average'")
    academic_standing = models.CharField(max_length=100, blank=True)

    # Contact
    teacher_name = models.CharField(max_length=200, blank=True)
    teacher_phone = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = "Education Profile"
        verbose_name_plural = "Education Profiles"

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.school_name}"


class HealthProfile(models.Model):
    """Health-specific details for healthcare beneficiaries"""
    TREATMENT_STATUS = (
        ('ongoing', 'Ongoing Treatment'),
        ('completed', 'Treatment Completed'),
        ('follow_up', 'Follow-up Care'),
    )

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='health_profile'
    )

    # Medical Information
    medical_condition = models.CharField(max_length=300)
    condition_description = models.TextField(blank=True)
    treatment_type = models.CharField(max_length=200)
    treatment_status = models.CharField(max_length=20, choices=TREATMENT_STATUS, default='ongoing')

    # Healthcare Provider
    hospital_name = models.CharField(max_length=300)
    hospital_address = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    doctor_phone = models.CharField(max_length=15, blank=True)

    # Treatment Timeline
    treatment_start_date = models.DateField()
    treatment_end_date = models.DateField(null=True, blank=True)

    # Costs
    total_medical_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_covered = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Outcome
    outcome_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Health Profile"
        verbose_name_plural = "Health Profiles"

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.medical_condition}"

    @property
    def coverage_percentage(self):
        if self.total_medical_cost > 0:
            return (self.amount_covered / self.total_medical_cost) * 100
        return 0


class YouthProfile(models.Model):
    """Youth empowerment-specific details"""
    TRAINING_TYPES = (
        ('vocational', 'Vocational Training'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('tech', 'Technology/IT'),
        ('agriculture', 'Agriculture'),
        ('fashion', 'Fashion & Design'),
        ('catering', 'Catering & Hospitality'),
        ('automotive', 'Automotive'),
        ('construction', 'Construction'),
        ('healthcare', 'Healthcare Training'),
        ('other', 'Other'),
    )

    EMPLOYMENT_STATUS = (
        ('unemployed', 'Unemployed'),
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('in_training', 'In Training'),
    )

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='youth_profile'
    )

    # Training Information
    skill_type = models.CharField(max_length=30, choices=TRAINING_TYPES)
    specific_skill = models.CharField(max_length=200, help_text="e.g., 'Web Development', 'Tailoring'")
    training_provider = models.CharField(max_length=300)
    training_location = models.TextField(blank=True)
    training_duration = models.CharField(max_length=100, help_text="e.g., '6 months', '1 year'")
    training_start_date = models.DateField()
    training_end_date = models.DateField(null=True, blank=True)

    # Certification
    certification_obtained = models.BooleanField(default=False)
    certificate_name = models.CharField(max_length=200, blank=True)

    # Outcome
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='in_training')
    business_started = models.BooleanField(default=False)
    business_name = models.CharField(max_length=200, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)

    # Support
    startup_grant_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    equipment_provided = models.TextField(blank=True, help_text="List of equipment/tools provided")

    class Meta:
        verbose_name = "Youth Empowerment Profile"
        verbose_name_plural = "Youth Empowerment Profiles"

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.specific_skill}"


class HousingProfile(models.Model):
    """Housing support-specific details"""
    SUPPORT_TYPES = (
        ('rent', 'Rent Assistance'),
        ('renovation', 'House Renovation'),
        ('building', 'House Building'),
        ('materials', 'Building Materials'),
        ('relocation', 'Relocation Support'),
    )

    PROJECT_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='housing_profile'
    )

    # Support Type
    support_type = models.CharField(max_length=20, choices=SUPPORT_TYPES)
    support_description = models.TextField()

    # Property Information
    property_address = models.TextField()
    property_type = models.CharField(max_length=100, blank=True, help_text="e.g., '2-bedroom flat', 'bungalow'")

    # For rent assistance
    landlord_name = models.CharField(max_length=200, blank=True)
    landlord_phone = models.CharField(max_length=15, blank=True)
    rent_amount_monthly = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rent_duration_months = models.IntegerField(default=0, help_text="Number of months covered")

    # Costs
    total_project_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_covered = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Status
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='pending')
    completion_date = models.DateField(null=True, blank=True)

    # Family Info
    family_size = models.IntegerField(default=1)
    number_of_children = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Housing Profile"
        verbose_name_plural = "Housing Profiles"

    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.get_support_type_display()}"

    @property
    def total_rent_covered(self):
        return self.rent_amount_monthly * self.rent_duration_months