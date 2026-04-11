"""
Data migration: seed default FormField sets for Healthcare, Youth Empowerment,
and Housing Support programs that currently have no form fields.

Runs safely multiple times — only adds fields to programs that have zero fields.
"""
from django.db import migrations


HEALTHCARE_FIELDS = [
    {
        'label': 'Medical Condition / Diagnosis',
        'field_type': 'textarea',
        'is_required': True,
        'help_text': 'Describe the medical condition or diagnosis clearly',
        'options': None,
        'order': 1,
    },
    {
        'label': 'Name of Hospital or Health Facility',
        'field_type': 'text',
        'is_required': True,
        'help_text': 'Full name of the hospital or clinic providing treatment',
        'options': None,
        'order': 2,
    },
    {
        'label': 'Type of Medical Support Needed',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the category of support you require',
        'options': ['Surgery', 'Medication / Drugs', 'Physiotherapy / Rehabilitation',
                    'Diagnostic Tests / Scans', 'General Treatment', 'Other'],
        'order': 3,
    },
    {
        'label': 'Estimated Total Cost of Treatment (NGN)',
        'field_type': 'number',
        'is_required': True,
        'help_text': 'Amount as quoted by the hospital (in Naira)',
        'options': None,
        'order': 4,
    },
    {
        'label': 'Name of Attending Doctor',
        'field_type': 'text',
        'is_required': False,
        'help_text': "Doctor's full name (if available)",
        'options': None,
        'order': 5,
    },
    {
        'label': 'How long have you had this condition?',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the duration that best describes your situation',
        'options': ['Less than 1 month', '1 – 6 months', '6 – 12 months',
                    '1 – 2 years', 'More than 2 years'],
        'order': 6,
    },
    {
        'label': 'Have you received any previous treatment for this condition?',
        'field_type': 'radio',
        'is_required': True,
        'help_text': '',
        'options': ['Yes', 'No'],
        'order': 7,
    },
    {
        'label': 'Do you have health insurance (e.g. NHIS)?',
        'field_type': 'radio',
        'is_required': True,
        'help_text': '',
        'options': ['Yes — NHIS', 'Yes — Private', 'No'],
        'order': 8,
    },
    {
        'label': 'Describe your financial situation and why you need this support',
        'field_type': 'textarea',
        'is_required': True,
        'help_text': 'Be as detailed as possible — this helps our review team assess your need',
        'options': None,
        'order': 9,
    },
]

YOUTH_FIELDS = [
    {
        'label': 'Current Employment Status',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the option that best describes your current situation',
        'options': ['Unemployed', 'Student (Full-time)', 'Student (Part-time)',
                    'Self-employed (Informal)', 'Employed (Part-time)', 'Employed (Full-time)'],
        'order': 1,
    },
    {
        'label': 'Highest Level of Education Completed',
        'field_type': 'select',
        'is_required': True,
        'help_text': '',
        'options': ['No Formal Education', 'Primary School', 'Secondary School (WAEC / NECO)',
                    'OND / NCE', 'HND / B.Sc', 'Postgraduate (M.Sc / MBA / PhD)'],
        'order': 2,
    },
    {
        'label': 'Type of Support Needed',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the type of empowerment programme you are applying for',
        'options': ['Skills Training / Vocational Programme', 'Startup / Business Capital',
                    'Mentorship & Coaching', 'Job Placement Assistance',
                    'Digital & Technology Skills', 'Other'],
        'order': 3,
    },
    {
        'label': 'Specific Skill, Trade, or Career Area of Interest',
        'field_type': 'text',
        'is_required': True,
        'help_text': 'e.g. Fashion Design, Software Development, Catering, Welding, etc.',
        'options': None,
        'order': 4,
    },
    {
        'label': 'Do you have any prior skills or work experience?',
        'field_type': 'radio',
        'is_required': True,
        'help_text': '',
        'options': ['Yes', 'No'],
        'order': 5,
    },
    {
        'label': 'If yes, briefly describe your skills or experience',
        'field_type': 'textarea',
        'is_required': False,
        'help_text': 'Leave blank if you have no prior experience',
        'options': None,
        'order': 6,
    },
    {
        'label': 'Do you currently have a business idea or plan?',
        'field_type': 'radio',
        'is_required': True,
        'help_text': '',
        'options': ['Yes', 'No', 'Still developing one'],
        'order': 7,
    },
    {
        'label': 'Why do you need this support? Describe your goals and aspirations',
        'field_type': 'textarea',
        'is_required': True,
        'help_text': 'Explain what you hope to achieve and how this programme will help you',
        'options': None,
        'order': 8,
    },
    {
        'label': 'Monthly Household Income (NGN)',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select your household income bracket',
        'options': ['No income', 'Below NGN20,000', 'NGN20,000 – NGN50,000',
                    'NGN50,000 – NGN100,000', 'Above NGN100,000'],
        'order': 9,
    },
]

HOUSING_FIELDS = [
    {
        'label': 'Type of Housing Support Needed',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the type of housing assistance you are applying for',
        'options': ['Rent Assistance', 'House Renovation / Repair',
                    'Resettlement / Relocation', 'Emergency Shelter'],
        'order': 1,
    },
    {
        'label': 'Current Housing Situation',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Select the option that best describes your current living situation',
        'options': ['Renting — unable to pay rent', 'Homeless / No fixed address',
                    'Overcrowded accommodation', 'Dilapidated or unsafe structure',
                    'Displaced / Evicted', 'Other'],
        'order': 2,
    },
    {
        'label': 'Current Address / Location',
        'field_type': 'text',
        'is_required': True,
        'help_text': 'Street address, area, and state',
        'options': None,
        'order': 3,
    },
    {
        'label': 'Monthly Rent Amount (NGN)',
        'field_type': 'number',
        'is_required': False,
        'help_text': 'Leave blank if you are not currently renting',
        'options': None,
        'order': 4,
    },
    {
        'label': 'Number of People in Your Household',
        'field_type': 'number',
        'is_required': True,
        'help_text': 'Include yourself and everyone living with you',
        'options': None,
        'order': 5,
    },
    {
        'label': 'Number of Dependants (children under 18 or elderly in your care)',
        'field_type': 'number',
        'is_required': True,
        'help_text': 'Enter 0 if none',
        'options': None,
        'order': 6,
    },
    {
        'label': 'Monthly Household Income (NGN)',
        'field_type': 'select',
        'is_required': True,
        'help_text': 'Combined income of all earning members of the household',
        'options': ['No income', 'Below NGN20,000', 'NGN20,000 – NGN50,000',
                    'NGN50,000 – NGN100,000', 'Above NGN100,000'],
        'order': 7,
    },
    {
        'label': 'How long have you been in this housing situation?',
        'field_type': 'select',
        'is_required': True,
        'help_text': '',
        'options': ['Less than 1 month', '1 – 6 months', '6 – 12 months',
                    '1 – 3 years', 'More than 3 years'],
        'order': 8,
    },
    {
        'label': "Landlord's Name and Phone Number (if renting)",
        'field_type': 'text',
        'is_required': False,
        'help_text': 'Leave blank if not applicable',
        'options': None,
        'order': 9,
    },
    {
        'label': 'Describe your housing situation and why you urgently need support',
        'field_type': 'textarea',
        'is_required': True,
        'help_text': 'Provide as much detail as possible to help our team assess your application',
        'options': None,
        'order': 10,
    },
]

FIELDS_BY_TYPE = {
    'healthcare': HEALTHCARE_FIELDS,
    'youth': YOUTH_FIELDS,
    'housing': HOUSING_FIELDS,
}


def seed_form_fields(apps, schema_editor):
    Program = apps.get_model('applications', 'Program')
    FormField = apps.get_model('applications', 'FormField')

    for program_type, field_defs in FIELDS_BY_TYPE.items():
        programs = Program.objects.filter(program_type=program_type)
        for program in programs:
            # Only seed if the program currently has no form fields
            if FormField.objects.filter(program=program).exists():
                continue
            for field_def in field_defs:
                FormField.objects.create(program=program, **field_def)


def remove_seeded_fields(apps, schema_editor):
    """Reverse: remove fields only if they still match the seeded labels exactly."""
    Program = apps.get_model('applications', 'Program')
    FormField = apps.get_model('applications', 'FormField')

    for program_type, field_defs in FIELDS_BY_TYPE.items():
        seeded_labels = [f['label'] for f in field_defs]
        programs = Program.objects.filter(program_type=program_type)
        for program in programs:
            FormField.objects.filter(program=program, label__in=seeded_labels).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0006_add_ckeditor_to_program'),
    ]

    operations = [
        migrations.RunPython(seed_form_fields, remove_seeded_fields),
    ]
