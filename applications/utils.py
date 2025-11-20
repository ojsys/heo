from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def send_welcome_email(user, verification_token=None):
    """Send welcome email to newly registered user"""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    if verification_token:
        verification_url = f"{site_url}/verify-email/{verification_token.token}/"
    else:
        verification_url = f"{site_url}/login/"

    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': getattr(settings, 'SITE_NAME', 'HEO Eziokwu Foundation'),
    }

    subject = f'Welcome to {getattr(settings, "SITE_NAME", "HEO Eziokwu Foundation")}'
    html_message = render_to_string('users/emails/welcome.html', context)

    send_mail(
        subject=subject,
        message=f"Welcome to HEO Eziokwu Foundation! Please verify your email at {verification_url}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_verification_email(user, verification_token):
    """Send email verification link"""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    verification_url = f"{site_url}/verify-email/{verification_token.token}/"

    context = {
        'user': user,
        'verification_url': verification_url,
    }

    subject = 'Verify Your Email Address'
    html_message = render_to_string('users/emails/verify_email.html', context)

    send_mail(
        subject=subject,
        message=f"Please verify your email at {verification_url}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_application_submitted(application):
    """Send confirmation email when application is submitted"""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    context = {
        'application': application,
        'dashboard_url': f"{site_url}/appl/my-applications/",
    }

    subject = f'Application Received: {application.program.name}'
    html_message = render_to_string('applications/emails/application_submitted.html', context)

    send_mail(
        subject=subject,
        message=f"Your application for {application.program.name} has been received. Application ID: #{application.id}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[application.applicant.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_new_application_to_admin(application):
    """Notify admin of new application submission"""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@heoeziokwufoundation.org')

    context = {
        'application': application,
        'admin_url': f"{site_url}/admin/applications/application/{application.id}/change/",
    }

    subject = f'New Application: {application.program.name} - #{application.id}'
    html_message = render_to_string('applications/emails/new_application_admin.html', context)

    send_mail(
        subject=subject,
        message=f"New application received for {application.program.name} from {application.applicant.email}. Application ID: #{application.id}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[admin_email],
        html_message=html_message,
        fail_silently=True,
    )


def send_beneficiary_welcome(beneficiary):
    """Send welcome email to new beneficiary"""
    if not beneficiary.email:
        return

    context = {
        'beneficiary': beneficiary,
    }

    subject = f'Welcome to {beneficiary.program.name} - HEO Eziokwu Foundation'
    html_message = render_to_string('applications/emails/beneficiary_welcome.html', context)

    send_mail(
        subject=subject,
        message=f"Congratulations! You have been accepted as a beneficiary of the {beneficiary.program.name} program.",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[beneficiary.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_support_notification(support):
    """Notify beneficiary of support disbursement"""
    beneficiary = support.beneficiary
    if not beneficiary.email:
        return

    context = {
        'support': support,
    }

    subject = f'Support Disbursement: {support.get_support_type_display()}'
    html_message = render_to_string('applications/emails/support_notification.html', context)

    send_mail(
        subject=subject,
        message=f"Support has been disbursed on your behalf. Type: {support.get_support_type_display()}, Amount: ₦{support.amount}",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@heoeziokwufoundation.org'),
        recipient_list=[beneficiary.email],
        html_message=html_message,
        fail_silently=True,
    )

def send_application_status_update(status_update):
    """
    Send email notification about application status update
    
    status_update can be either:
    - An ApplicationStatus object
    - An Application object (when called from review)
    """
    # Determine if we're dealing with an ApplicationStatus or Application object
    if hasattr(status_update, 'application'):
        # It's an ApplicationStatus object
        application = status_update.application
        status = status_update.status
        notes = status_update.notes
    else:
        # It's an Application object
        application = status_update
        status = application.status
        notes = "Your application has been reviewed."
    
    applicant = application.applicant
    
    # Check if the user has enabled email notifications for status changes
    try:
        preferences = applicant.notification_preference
        if not preferences.email_on_status_change:
            return  # User has disabled notifications for status changes
    except:
        # If preferences don't exist, proceed with sending email
        pass
    
    # Get the site URL from settings, with a fallback
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    
    context = {
        'user': applicant,
        'application': application,
        'status': status,
        'notes': notes,
        'dashboard_url': f"{site_url}/applications/dashboard/",
    }
    
    # Render email content
    subject = f'Update on your application for {application.program.name}'
    html_message = render_to_string('applications/emails/status_update.html', context)
    plain_message = render_to_string('applications/emails/status_update_plain.html', context)
    
    # Send the email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[applicant.email],
        html_message=html_message,
        fail_silently=True,
    )