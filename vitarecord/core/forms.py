from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, MedicalRecord


class RegisterForm(UserCreationForm):
    """Handles both patient and doctor registration with role selection."""
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role',
                  'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'medications', 'notes']
        widgets = {
            'diagnosis':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medications': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'aspirin, ibuprofen, metformin ...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
