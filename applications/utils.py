from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_application_status_update(application):
    subject = f'Application Status Update - {application.program.name}'
    html_message = render_to_string('emails/application_status_update.html', {
        'application': application
    })
    
    send_mail(
        subject=subject,
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.applicant.email],
        fail_silently=False
    )