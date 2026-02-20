from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, MedicalRecord
from .forms import MedicalRecordForm
from .services.ddi_service import check_interactions


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'core/landing.html')


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
    # Get distinct patients from this doctor's records
    recent_records = MedicalRecord.objects.filter(
        doctor=request.user
    ).select_related('patient').order_by('-created_at')[:10]

    seen = set()
    recent_patients = []
    for rec in recent_records:
        if rec.patient.id not in seen:
            rec.patient.last_visit = rec.created_at
            recent_patients.append(rec.patient)
            seen.add(rec.patient.id)

    return render(request, 'core/doctor_dashboard.html', {
        'recent_patients': recent_patients
    })

@login_required
def search_patient(request):
    if not request.user.is_doctor():
        return redirect('patient_dashboard')
    patient_id = request.GET.get('patient_id', '').strip().upper()
    if patient_id:
        patient = get_patient_by_id(patient_id)
        if patient:
            return redirect('consultation', unique_id=patient_id)
        else:
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
                    existing_meds,
                    [m.strip() for m in new_meds.split(',')]
                )
                if not interaction_alert:
                    messages.success(request, 'No interactions found. Safe to prescribe.')

            elif action == 'save':
                record = form.save(commit=False)
                record.patient = patient
                record.doctor  = request.user
                record.save()
                messages.success(request, 'Medical record saved successfully.')
                return redirect('consultation', unique_id=unique_id)

    return render(request, 'core/consultation.html', {
        'patient': patient,
        'records': records,
        'form':    form,
        'interaction_alert': interaction_alert,
    })

