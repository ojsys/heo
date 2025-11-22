from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import uuid


def validate_image_file_extension(value):
    """Validate that uploaded file is a JPEG or PNG image."""
    valid_extensions = ['jpg', 'jpeg', 'png']
    ext = value.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            f'Only JPEG and PNG images are allowed. You uploaded a .{ext} file.'
        )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('applicant', 'Applicant'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    username = models.CharField(max_length=150, unique=True, null=True)
    email = models.EmailField(unique=True) 
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='applicant')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email or f"User {self.pk}"

class UserVerification(models.Model):
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_document = models.ImageField(
        upload_to='verification_documents/id/',
        null=True,
        validators=[validate_image_file_extension],
        help_text='Upload a JPEG or PNG image of your ID document'
    )
    address_proof = models.ImageField(
        upload_to='verification_documents/address/',
        null=True,
        validators=[validate_image_file_extension],
        help_text='Upload a JPEG or PNG image of your address proof'
    )
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verifications_done')
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def send_submission_notification(self):
        context = {
            'user': self.user,
            'verification': self,
            'admin_url': f"{settings.SITE_URL}/admin/users/userverification/{self.pk}/change/",
            'site_name': settings.SITE_NAME
        }
        
        html_message = render_to_string('email/admin_notification.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='New Verification Submission',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

    def send_verification_status_notification(self):
        context = {
            'user': self.user,
            'verification': self,
            'login_url': f"{settings.SITE_URL}{reverse('users:login')}",
            'site_name': settings.SITE_NAME
        }
        
        html_message = render_to_string('email/user_verification_status.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=f'Account Verification {self.status.title()}',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            fail_silently=False,
        )


class EmailVerificationToken(models.Model):
    """Token for email verification during registration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification token for {self.user.email}"

    @property
    def is_valid(self):
        """Check if token is still valid (not used and not expired)"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.save()

