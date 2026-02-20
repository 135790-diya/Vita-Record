from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model  = MedicalRecord
        fields = ['diagnosis', 'medications', 'notes']
        widgets = {
            'diagnosis':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medications': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'aspirin, ibuprofen, ...'
    }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
