from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

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