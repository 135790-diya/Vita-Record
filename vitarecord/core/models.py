import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
def generate_short_id():
    return str(uuid.uuid4())[:8].upper()


class CustomUser(AbstractUser):
    PATIENT = 'patient'
    DOCTOR  = 'doctor'
    ROLE_CHOICES = [(PATIENT, 'Patient'), (DOCTOR, 'Doctor')]

    role      = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)
    unique_id = models.CharField(max_length=20, unique=True, default=generate_short_id)

    def is_doctor(self):
        return self.role == self.DOCTOR

    def is_patient(self):
        return self.role == self.PATIENT

    def __str__(self):
        return f'{self.get_full_name()} [{self.unique_id}] ({self.role})'


class MedicalRecord(models.Model):
    patient    = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='records', limit_choices_to={'role': 'patient'}
    )
    doctor     = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='consultations', limit_choices_to={'role': 'doctor'}
    )
    diagnosis    = models.TextField()
    medications  = models.TextField(
        help_text='Comma-separated list of medications'
    )
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_medication_list(self):
        return [m.strip() for m in self.medications.split(',') if m.strip()]

    def __str__(self):
        return f'Record for {self.patient} on {self.created_at.date()}'