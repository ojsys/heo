from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.validators import FileExtensionValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, UserVerification


def validate_image_file(file):
    """Validate that uploaded file is a JPEG or PNG image."""
    if file:
        # Check file extension
        valid_extensions = ['jpg', 'jpeg', 'png']
        ext = file.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise forms.ValidationError(
                'Only JPEG and PNG images are allowed. '
                f'You uploaded a .{ext} file.'
            )

        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise forms.ValidationError(
                f'File size must be less than 5MB. '
                f'Your file is {file.size / (1024 * 1024):.2f}MB.'
            )

class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Field('username', css_class='mb-3'),
            Field('password', css_class='mb-3'),
            Submit('submit', 'Log In', css_class='btn btn-primary')
        )

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''


        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            'email',
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                Column('address', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Register', css_class='btn btn-success')
        )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            'email',
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                Column('date_of_birth', css_class='form-group col-md-6 mb-3'),
            ),
            'address',
            'profile_picture',
            Submit('submit', 'Update Profile', css_class='btn btn-primary mt-3')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email


class UserVerificationForm(forms.ModelForm):
    class Meta:
        model = UserVerification
        fields = ['id_document', 'address_proof']
        widgets = {
            'id_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png'
            }),
            'address_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('id_document', css_class='mb-3'),
            Field('address_proof', css_class='mb-3'),
            Submit('submit', 'Submit Verification', css_class='btn btn-primary')
        )

        # Add help text
        self.fields['id_document'].help_text = 'Upload a clear photo of your ID (JPEG or PNG only, max 5MB)'
        self.fields['address_proof'].help_text = 'Upload a proof of address document (JPEG or PNG only, max 5MB)'

    def clean_id_document(self):
        file = self.cleaned_data.get('id_document')
        validate_image_file(file)
        return file

    def clean_address_proof(self):
        file = self.cleaned_data.get('address_proof')
        validate_image_file(file)
        return file