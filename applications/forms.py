from django import forms
from django.forms import inlineformset_factory
from .models import Program, Application, ApplicationDocument
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML, Div

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'program_type', 'description', 'eligibility_criteria', 
                 'start_date', 'end_date', 'max_beneficiaries', 'featured_image']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'eligibility_criteria': forms.Textarea(attrs={'rows': 4}),
        }

class ApplicationForm(forms.ModelForm):
    # Add these fields explicitly to the form
    first_name = forms.CharField(max_length=100, label="First Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    email = forms.EmailField(label="Email Address")
    date_of_birth = forms.DateField(
        label="Date of Birth", 
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    phone_number = forms.CharField(max_length=20, required=False, label="Phone Number")
    address = forms.CharField(max_length=255, required=False, label="Address")
    city = forms.CharField(max_length=100, required=False, label="City")
    state = forms.CharField(max_length=100, required=False, label="State")
    zip_code = forms.CharField(max_length=20, required=False, label="Zip Code")
    country = forms.CharField(max_length=100, required=False, label="Country")
    
    class Meta:
        model = Application
        fields = []  # We're adding the fields manually above
    
    def __init__(self, *args, **kwargs):
        self.program = kwargs.pop('program', None)
        self.user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)
        
        # Make sure all required fields are properly marked
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} *"
        
        # Prefill form with user profile data if available
        if self.user:
            # Prefill fields from user object
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            
            # Prefill fields from profile if it exists
            try:
                if hasattr(self.user, 'profile'):
                    profile = self.user.profile
                    
                    # Check each profile field and prefill if available
                    profile_fields = [
                        'date_of_birth', 'phone_number', 'address', 'city', 
                        'state', 'zip_code', 'country'
                    ]
                    
                    for field in profile_fields:
                        if hasattr(profile, field) and getattr(profile, field):
                            self.fields[field].initial = getattr(profile, field)
                    
                    # Check for any additional profile fields that might be available
                    additional_fields = [
                        'gender', 'nationality', 'occupation', 'education_level',
                        'institution', 'major', 'graduation_year'
                    ]
                    
                    for field in additional_fields:
                        if field in self.fields and hasattr(profile, field) and getattr(profile, field):
                            self.fields[field].initial = getattr(profile, field)
            except Exception as e:
                # If there's an error accessing profile, just continue without prefilling
                print(f"Error accessing user profile: {str(e)}")
        
        # Set up crispy forms helper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form'
        self.helper.label_class = 'form-label'
        self.helper.field_class = 'form-control'
        
        # Create layout for personal information
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('date_of_birth', css_class='col-md-6'),
            ),
            Row(
                Column('phone_number', css_class='col-md-6'),
                Column('address', css_class='col-md-6'),
            ),
            Row(
                Column('city', css_class='col-md-4'),
                Column('state', css_class='col-md-4'),
                Column('zip_code', css_class='col-md-4'),
            ),
            Row(
                Column('country', css_class='col-md-12'),
            ),
        )

class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ['document_type', 'document']
        labels = {
            'document_type': 'Document Type',
            'document': 'Document'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('document_type', css_class='col-md-6'),
                Column('document', css_class='col-md-6'),
            )
        )
        
        # Add custom validation for program-specific requirements
        if self.program:
            # Add any program-specific field validation here
            pass
        
        # Dynamically add fields based on program's form fields
        if self.program:
            for field in self.program.form_fields.all():
                field_kwargs = {
                    'required': field.is_required,
                    'help_text': field.help_text,
                    'label': field.label
                }
                
                if field.field_type == 'text':
                    self.fields[f'field_{field.id}'] = forms.CharField(**field_kwargs)
                elif field.field_type == 'textarea':
                    self.fields[f'field_{field.id}'] = forms.CharField(
                        widget=forms.Textarea(attrs={'rows': 4}),
                        **field_kwargs
                    )
                elif field.field_type == 'number':
                    self.fields[f'field_{field.id}'] = forms.IntegerField(**field_kwargs)
                elif field.field_type == 'email':
                    self.fields[f'field_{field.id}'] = forms.EmailField(**field_kwargs)
                elif field.field_type == 'date':
                    self.fields[f'field_{field.id}'] = forms.DateField(
                        widget=forms.DateInput(attrs={'type': 'date'}),
                        **field_kwargs
                    )
                elif field.field_type in ['select', 'radio']:
                    # Handle options as a list
                    if field.options:
                        choices = [(option, option) for option in field.options]
                        if field.field_type == 'select':
                            self.fields[f'field_{field.id}'] = forms.ChoiceField(
                                choices=choices,
                                **field_kwargs
                            )
                        else:
                            self.fields[f'field_{field.id}'] = forms.ChoiceField(
                                widget=forms.RadioSelect,
                                choices=choices,
                                **field_kwargs
                            )
                elif field.field_type == 'checkbox':
                    # Handle options as a list for checkboxes
                    if field.options:
                        self.fields[f'field_{field.id}'] = forms.MultipleChoiceField(
                            widget=forms.CheckboxSelectMultiple,
                            choices=[(option, option) for option in field.options],
                            **field_kwargs
                        )
                    else:
                        # Single checkbox
                        self.fields[f'field_{field.id}'] = forms.BooleanField(**field_kwargs)

    def clean(self):
        cleaned_data = super().clean()
        form_data = {}
        
        if self.program:
            for field in self.program.form_fields.all():
                field_key = f'field_{field.id}'
                if field_key in cleaned_data:
                    form_data[field.label] = cleaned_data[field_key]
        
        cleaned_data['form_data'] = form_data
        return cleaned_data

class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ['document', 'document_type']
        widgets = {
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'document_type': forms.TextInput(attrs={'class': 'form-control'})
        }

class ApplicationReviewForm(forms.ModelForm):
    update_status = forms.BooleanField(
        required=False, 
        initial=True,
        label="Update application status",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label="Review Notes"
    )
    status = forms.ChoiceField(
        choices=[
            ('submitted', 'Submitted'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('on_hold', 'On Hold')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Application
        fields = ['review_notes']
        widgets = {
            'review_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['status'].initial = self.instance.status

ApplicationDocumentFormSet = inlineformset_factory(
    Application, 
    ApplicationDocument,
    fields=['document', 'document_type'],
    extra=1,
    can_delete=True
)