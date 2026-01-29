# arch_design/forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Inquiry, ContactMessage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML
from crispy_forms.bootstrap import PrependedText, PrependedAppendedText

class InquiryForm(forms.ModelForm):
    """Inquiry/Quotation Form"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+8801234567890'. Up to 15 digits allowed."
    )
    
    phone = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'placeholder': '+880 1234 567890',
            'class': 'form-control'
        })
    )
    
    project_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Tell us about your project requirements, location, size, and any specific needs...',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Inquiry
        fields = [
            'name', 'email', 'phone', 'address', 
            'service_type', 'specific_service', 'budget_range',
            'project_description', 'is_urgent'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Full address with city and area'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'specific_service': forms.Select(attrs={'class': 'form-select'}),
            'budget_range': forms.Select(attrs={'class': 'form-select'}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'needs-validation'
        self.helper.attrs = {'novalidate': ''}
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6 mb-3'),
                Column('email', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('phone', css_class='col-md-6 mb-3'),
                Column('address', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('service_type', css_class='col-md-6 mb-3'),
                Column('specific_service', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column('budget_range', css_class='col-md-6 mb-3'),
                Column('project_description', css_class='col-md-6 mb-3'),
            ),
            Row(
                Column(
                    Field('is_urgent', css_class='form-check-input'),
                    css_class='col-md-12 mb-3'
                ),
            ),
            Submit('submit', 'Submit Inquiry', css_class='btn btn-primary btn-lg w-100')
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add email validation logic if needed
        return email

class ContactMessageForm(forms.ModelForm):
    """Contact Message Form"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control',
                'placeholder': 'Your message here...',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Send Message', css_class='btn-primary'))
        