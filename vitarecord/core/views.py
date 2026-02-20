from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, MedicalRecord
from .forms import RegisterForm, MedicalRecordForm
from .services.ddi_service import check_interactions


# ── PUBLIC VIEWS ───────────────────────────────────────────────────────────────

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'core/landing.html')


def register(request):
    """Unified registration page for both patients and doctors."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.role       = form.cleaned_data['role']
            user.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name()}!')
            return redirect('dashboard_redirect')
    else:
        # Pre-select role if coming from landing page buttons
        initial_role = request.GET.get('role', 'patient')
        form = RegisterForm(initial={'role': initial_role})
    return render(request, 'core/register.html', {'form': form})


def user_login(request):
    
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # --- DEMO DOCTOR LOGIN ---
        if username == "doctor" and password == "123":
            user, created = CustomUser.objects.get_or_create(username="doctor")
            user.role = CustomUser.DOCTOR
            user.set_password("123")
            user.save()
            login(request, user)
            return redirect('consultation', unique_id="PT-8829-QX")

        # --- DEMO PATIENT LOGIN ---
        if username == "patient" and password == "123":
           user, created = CustomUser.objects.get_or_create(username="patient")
           user.role = CustomUser.PATIENT
           user.unique_id = "PT-8829-QX"
           user.first_name = "Alex"
           user.last_name = "Johnson"
           user.set_password("123")
           user.save()
           if not MedicalRecord.objects.filter(patient=user).exists():
              MedicalRecord.objects.create(
                    patient=user,
                    doctor=None,
                    diagnosis="Type 2 Diabetes, Hypertension",
                    medications="Warfarin (5mg), Atorvastatin (20mg), Metformin (500mg)",
                    notes="Stable ECG; continue Atorvastatin."
               )
              
        login(request, user)
        return redirect('patient_dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html', {
        'next': request.GET.get('next', '')
    })
def user_logout(request):
    logout(request)
    return redirect('landing')


# ── PROTECTED VIEWS ───────────────────────────────────────────────────────────

@login_required
def dashboard_redirect(request):
    if request.user.is_doctor():
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')


@login_required
def patient_dashboard(request):
    if not request.user.is_patient():
        return redirect('doctor_dashboard')
    records = MedicalRecord.objects.filter(patient=request.user)
    return render(request, 'core/patient_dashboard.html', {'records': records})


@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor():
        return redirect('patient_dashboard')
    recent_records = MedicalRecord.objects.filter(
        doctor=request.user).select_related('patient').order_by('-created_at')[:10]
    seen, recent_patients = set(), []
    for rec in recent_records:
        if rec.patient.id not in seen:
            rec.patient.last_visit = rec.created_at
            recent_patients.append(rec.patient)
            seen.add(rec.patient.id)
    return render(request, 'core/doctor_dashboard.html',
                  {'recent_patients': recent_patients})


# ── MODULAR HELPER (swap implementation for QR later) ─────────────────────────
def get_patient_by_id(unique_id: str):
    return CustomUser.objects.filter(unique_id=unique_id, role='patient').first()


@login_required
def search_patient(request):
    if not request.user.is_doctor():
        return redirect('patient_dashboard')
    patient_id = request.GET.get('patient_id', '').strip().upper()
    if patient_id:
        patient = get_patient_by_id(patient_id)
        if patient:
            return redirect('consultation', unique_id=patient_id)
        messages.error(request, f'No patient found with ID: {patient_id}')

    return redirect('doctor_dashboard')


@login_required
def consultation(request, unique_id):
    if not request.user.is_doctor():
        return redirect('patient_dashboard')
    patient = get_object_or_404(CustomUser, unique_id=unique_id, role='patient')
    records = MedicalRecord.objects.filter(patient=patient)
    form    = MedicalRecordForm()
    interaction_alert = None
    if request.method == 'POST':
        form   = MedicalRecordForm(request.POST)
        action = request.POST.get('action')
        if form.is_valid():
            new_meds = form.cleaned_data['medications']
            existing_meds = []
            for rec in records:
                existing_meds.extend(rec.get_medication_list())
            if action == 'check':
                interaction_alert = check_interactions(
                    existing_meds, [m.strip() for m in new_meds.split(',')])
                if not interaction_alert:
                    messages.success(request, 'No interactions found. Safe to prescribe.')
            elif action == 'save':
                record = form.save(commit=False)
                record.patient = patient
                record.doctor  = request.user
                record.save()
                messages.success(request, 'Record saved.')
                return redirect('consultation', unique_id=unique_id)
    return render(request, 'core/consultation.html', {
        'patient': patient, 'records': records,
        'form': form, 'interaction_alert': interaction_alert})
