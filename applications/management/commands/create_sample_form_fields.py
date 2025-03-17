from django.core.management.base import BaseCommand
from applications.models import Program, FormField

class Command(BaseCommand):
    help = 'Creates sample form fields for a program'

    def add_arguments(self, parser):
        parser.add_argument('program_id', type=int, help='ID of the program to add form fields to')

    def handle(self, *args, **options):
        program_id = options['program_id']
        
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Program with ID {program_id} does not exist'))
            return
            
        # Delete existing form fields for this program
        FormField.objects.filter(program=program).delete()
        
        # Create sample form fields
        form_fields = [
            {
                'label': 'Full Name',
                'field_type': 'text',
                'is_required': True,
                'help_text': 'Enter your full legal name',
                'order': 1
            },
            {
                'label': 'Email Address',
                'field_type': 'email',
                'is_required': True,
                'help_text': 'We will use this email to contact you',
                'order': 2
            },
            {
                'label': 'Phone Number',
                'field_type': 'text',
                'is_required': True,
                'help_text': 'Enter your phone number with country code',
                'order': 3
            },
            {
                'label': 'Date of Birth',
                'field_type': 'date',
                'is_required': True,
                'help_text': '',
                'order': 4
            },
            {
                'label': 'Current Education Level',
                'field_type': 'select',
                'is_required': True,
                'options': ['High School', 'Undergraduate', 'Graduate', 'Postgraduate', 'Other'],
                'help_text': 'Select your current level of education',
                'order': 5
            },
            {
                'label': 'Why are you applying for this program?',
                'field_type': 'textarea',
                'is_required': True,
                'help_text': 'Please explain your motivation for applying (max 500 words)',
                'order': 6
            },
            {
                'label': 'How did you hear about us?',
                'field_type': 'radio',
                'is_required': True,
                'options': ['Social Media', 'Friend/Family', 'School/University', 'Online Search', 'Other'],
                'help_text': '',
                'order': 7
            },
            {
                'label': 'I agree to the terms and conditions',
                'field_type': 'checkbox',
                'is_required': True,
                'help_text': 'By checking this box, you agree to our terms and conditions',
                'order': 8
            }
        ]
        
        for field_data in form_fields:
            FormField.objects.create(program=program, **field_data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(form_fields)} form fields for {program.name}'))