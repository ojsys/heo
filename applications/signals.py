from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Application, ApplicationStatus, Beneficiary, BeneficiarySupport
from .utils import (
    send_application_submitted,
    send_new_application_to_admin,
    send_application_status_update,
    send_beneficiary_welcome,
    send_support_notification,
)


@receiver(pre_save, sender=Application)
def track_application_status_change(sender, instance, **kwargs):
    """Track if the application status has changed"""
    if instance.pk:
        try:
            old_instance = Application.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Application.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Application)
def application_post_save(sender, instance, created, **kwargs):
    """Handle application creation and status changes"""
    if created and instance.status == 'submitted':
        # New application submitted
        send_application_submitted(instance)
        send_new_application_to_admin(instance)
    elif not created:
        # Check if status changed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            # Status has changed
            if old_status == 'draft' and instance.status == 'submitted':
                # Application was submitted
                send_application_submitted(instance)
                send_new_application_to_admin(instance)
            else:
                # Other status changes - send update notification
                send_application_status_update(instance)


@receiver(post_save, sender=ApplicationStatus)
def application_status_update_created(sender, instance, created, **kwargs):
    """Send notification when a new ApplicationStatus is created"""
    if created:
        # Update the parent application status
        application = instance.application
        if application.status != instance.status:
            application.status = instance.status
            application.save()

        # Send notification
        send_application_status_update(instance)


@receiver(post_save, sender=Beneficiary)
def beneficiary_created(sender, instance, created, **kwargs):
    """Send welcome email when a new beneficiary is created"""
    if created:
        send_beneficiary_welcome(instance)


@receiver(post_save, sender=BeneficiarySupport)
def support_created(sender, instance, created, **kwargs):
    """Send notification when support is disbursed"""
    if created:
        send_support_notification(instance)


def create_beneficiary_from_application(application, beneficiary_type, created_by):
    """
    Helper function to create a beneficiary record from an approved application.

    Args:
        application: The approved Application instance
        beneficiary_type: One of 'education', 'health', 'youth', 'housing'
        created_by: The user creating the beneficiary record

    Returns:
        The created Beneficiary instance
    """
    # Map program types to beneficiary types
    program_type_mapping = {
        'scholarship': 'education',
        'healthcare': 'health',
        'youth': 'youth',
        'housing': 'housing',
        'other': 'education',  # Default
    }

    if not beneficiary_type:
        beneficiary_type = program_type_mapping.get(
            application.program.program_type,
            'education'
        )

    # Get applicant info
    applicant = application.applicant
    form_data = application.form_data or {}

    # Create beneficiary
    beneficiary = Beneficiary.objects.create(
        beneficiary_type=beneficiary_type,
        application=application,
        program=application.program,
        user=applicant,
        full_name=applicant.get_full_name() or form_data.get('full_name', applicant.email),
        date_of_birth=applicant.date_of_birth,
        gender=form_data.get('gender', 'male'),
        phone_number=applicant.phone_number or form_data.get('phone_number', ''),
        email=applicant.email,
        address=applicant.address or form_data.get('address', ''),
        guardian_name=form_data.get('guardian_name', ''),
        guardian_phone=form_data.get('guardian_phone', ''),
        status='active',
        start_date=timezone.now().date(),
        created_by=created_by,
    )

    return beneficiary
