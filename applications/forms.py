from django import forms
from .models import Program, Application, ApplicationDocument

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
    class Meta:
        model = Application
        fields = ['form_data']
        widgets = {
            'form_data': forms.HiddenInput(),
        }

    def __init__(self, program, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.program = program
        self.fields['form_data'].initial = {}
        
        # Dynamically add fields based on program's form fields
        for field in program.form_fields.all():
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
                choices = [(k, v) for k, v in field.options.items()]
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
                self.fields[f'field_{field.id}'] = forms.MultipleChoiceField(
                    widget=forms.CheckboxSelectMultiple,
                    choices=[(k, v) for k, v in field.options.items()],
                    **field_kwargs
                )

    def clean(self):
        cleaned_data = super().clean()
        form_data = {}
        
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
    class Meta:
        model = Application
        fields = ['status', 'review_notes']
        widgets = {
            'review_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }