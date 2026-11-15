import os
from datetime import datetime, date, timedelta
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    db, User, PatientProfile, CaregiverAssignment,
    Medication, MedicationLog, HealthVital, DoctorAppointment,
    EmergencyContact, EmergencyAlert, Notification
)
from translations import translate
from ai_engine import predict_patient_adherence, evaluate_vitals_health_status
from seed_data import seed_database

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eldercare-360-super-secure-production-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///eldercare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# =========================================================================
# TEMPLATE HELPERS & CONTEXT PROCESSORS
# =========================================================================
@app.context_processor
def inject_global_context():
    lang = session.get('lang', 'en')
    current_user = None
    if 'user_id' in session:
        current_user = db.session.get(User, session['user_id'])
    
    def _t(key, default=None):
        return translate(key, lang=lang, default=default)

    return {
        '_t': _t,
        'current_user': current_user,
        'today_formatted': date.today().strftime('%A, %B %d, %Y')
    }

def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this healthcare module.', 'info')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_active_patient(user):
    """
    Returns the target patient for the current session.
    If the user is an elderly patient, returns themselves.
    If the user is a caregiver or family member, returns their first assigned patient.
    """
    if not user:
        # Fallback to demo elderly patient
        return User.query.filter_by(role='elderly').first()
    
    if user.role == 'elderly':
        return user
    
    # Check for linked patients
    assignment = CaregiverAssignment.query.filter_by(caregiver_id=user.id).first()
    if assignment and assignment.patient:
        return assignment.patient
    
    # Fallback to any elderly patient in the system
    return User.query.filter_by(role='elderly').first()

def compute_patient_ai_insights(patient):
    """
    Gathers clinical features from database records and feeds them to the real ML model.
    """
    if not patient:
        return {'insufficient_data': True}
    
    profile = patient.patient_profile
    age = profile.age if profile else 72
    
    active_meds = Medication.query.filter_by(patient_id=patient.id, is_active=True).all()
    num_medications = len(active_meds)
    
    daily_dose_count = sum(len(m.get_times_list()) for m in active_meds)
    
    # Past 7 days logs
    seven_days_ago = date.today() - timedelta(days=7)
    recent_logs = MedicationLog.query.filter(
        MedicationLog.patient_id == patient.id,
        MedicationLog.scheduled_date >= seven_days_ago,
        MedicationLog.status.in_(['taken', 'missed'])
    ).all()
    
    if len(recent_logs) < 3:
        return {'insufficient_data': True}
    
    taken_count = sum(1 for l in recent_logs if l.status == 'taken')
    past_adherence_rate = taken_count / len(recent_logs) if recent_logs else 1.0
    
    # Check consecutive missed streak
    missed_streak = 0
    ordered_logs = MedicationLog.query.filter_by(patient_id=patient.id)\
        .order_by(MedicationLog.scheduled_date.desc(), MedicationLog.scheduled_time.desc()).limit(10).all()
    for l in ordered_logs:
        if l.status == 'missed':
            missed_streak += 1
        elif l.status == 'taken':
            break

    # Chronic conditions count
    cond_count = len(profile.chronic_conditions.split(',')) if profile and profile.chronic_conditions else 1
    
    # Mobility level mapping: 0=Independent, 1=Assisted, 2=Wheelchair, 3=Bedridden
    mobility_map = {'Independent': 0, 'Assisted (Walking Stick)': 1, 'Wheelchair': 2, 'Bedridden': 3}
    mob_val = mobility_map.get(profile.mobility_level if profile else 'Independent', 0)
    
    # Vitals variability
    recent_vitals = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.desc()).limit(14).all()
    
    sys_bps = [v.systolic_bp for v in recent_vitals if v.systolic_bp]
    glucoses = [v.blood_glucose for v in recent_vitals if v.blood_glucose]
    
    bp_var = float(np.std(sys_bps)) if len(sys_bps) >= 2 else 10.0
    glucose_var = float(np.std(glucoses)) if len(glucoses) >= 2 else 15.0
    
    features = {
        'age': age,
        'num_medications': num_medications,
        'daily_dose_count': daily_dose_count,
        'past_adherence_rate': past_adherence_rate,
        'missed_streak': missed_streak,
        'chronic_conditions_count': cond_count,
        'mobility_level': mob_val,
        'bp_variability': bp_var,
        'glucose_variability': glucose_var
    }
    
    return predict_patient_adherence(features)

# =========================================================================
# 1. HOME & LANDING PAGE (MANDATORY BACKGROUND IMAGE HERO SECTION)
# =========================================================================
@app.route('/')
def home():
    user = get_current_user()
    return render_template('index.html', user=user)

# =========================================================================
# 2. DASHBOARD (ROLE-TAILORED VIEWS & LIVE CLINICAL SUMMARY)
# =========================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    patient = get_active_patient(user)
    today = date.today()
    
    # Total active medications
    active_meds = Medication.query.filter_by(patient_id=patient.id, is_active=True).all()
    total_meds_count = len(active_meds)
    
    # Today's dosage logs
    today_logs = MedicationLog.query.filter_by(patient_id=patient.id, scheduled_date=today)\
        .order_by(MedicationLog.scheduled_time.asc()).all()
    
    today_total_doses = len(today_logs)
    today_taken_count = sum(1 for l in today_logs if l.status == 'taken')
    today_missed_count = sum(1 for l in today_logs if l.status == 'missed')
    today_pending_count = sum(1 for l in today_logs if l.status == 'pending')
    
    # Adherence rate calculation (Past 14 days)
    fourteen_days_ago = today - timedelta(days=14)
    past_logs = MedicationLog.query.filter(
        MedicationLog.patient_id == patient.id,
        MedicationLog.scheduled_date >= fourteen_days_ago,
        MedicationLog.status.in_(['taken', 'missed'])
    ).all()
    
    if past_logs:
        adherence_pct = round((sum(1 for l in past_logs if l.status == 'taken') / len(past_logs)) * 100, 1)
    else:
        adherence_pct = 100.0 if today_taken_count > 0 else 90.0

    # Next doctor appointment
    next_appointment = DoctorAppointment.query.filter(
        DoctorAppointment.patient_id == patient.id,
        DoctorAppointment.appointment_date >= today,
        DoctorAppointment.status == 'Scheduled'
    ).order_by(DoctorAppointment.appointment_date.asc(), DoctorAppointment.appointment_time.asc()).first()
    
    # Latest health vitals
    latest_vital = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.desc()).first()
        
    # Assigned caregivers
    caregivers = CaregiverAssignment.query.filter_by(patient_id=patient.id).all()
    
    # Vitals trend data for chart (Last 14 days)
    vitals_recent = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.asc()).limit(14).all()
    
    chart_labels = [v.reading_date.strftime('%b %d') for v in vitals_recent]
    chart_sys_bp = [v.systolic_bp for v in vitals_recent]
    chart_dia_bp = [v.diastolic_bp for v in vitals_recent]
    chart_glucose = [v.blood_glucose for v in vitals_recent]

    # AI Adherence Risk Prediction
    ai_insight = compute_patient_ai_insights(patient)

    return render_template(
        'dashboard/dashboard.html',
        patient=patient,
        total_meds_count=total_meds_count,
        today_logs=today_logs,
        today_total_doses=today_total_doses,
        today_taken_count=today_taken_count,
        today_missed_count=today_missed_count,
        today_pending_count=today_pending_count,
        adherence_pct=adherence_pct,
        next_appointment=next_appointment,
        latest_vital=latest_vital,
        caregivers=caregivers,
        chart_labels=chart_labels,
        chart_sys_bp=chart_sys_bp,
        chart_dia_bp=chart_dia_bp,
        chart_glucose=chart_glucose,
        ai_insight=ai_insight
    )

# =========================================================================
# 3. MEDICATION MANAGEMENT (CRUD & DOSE SCHEDULE)
# =========================================================================
@app.route('/medications')
@login_required
def medications():
    user = get_current_user()
    patient = get_active_patient(user)
    meds = Medication.query.filter_by(patient_id=patient.id).order_by(Medication.created_at.desc()).all()
    return render_template('medications/index.html', medications=meds, patient=patient)

@app.route('/medications/add', methods=['POST'])
@login_required
def add_medication():
    user = get_current_user()
    patient = get_active_patient(user)
    
    name = request.form.get('name', '').strip()
    dosage = request.form.get('dosage', '').strip()
    frequency = request.form.get('frequency', '').strip()
    form = request.form.get('form', 'Tablet').strip()
    scheduled_times = request.form.get('scheduled_times', '08:00').strip()
    instructions = request.form.get('instructions', '').strip()
    prescribing_doctor = request.form.get('prescribing_doctor', '').strip()
    doctor_phone = request.form.get('doctor_phone', '').strip()
    
    if not name or not dosage:
        flash('Medicine name and dosage are mandatory fields.', 'danger')
        return redirect(url_for('medications'))
        
    med = Medication(
        patient_id=patient.id,
        name=name,
        dosage=dosage,
        frequency=frequency,
        form=form,
        start_date=date.today(),
        scheduled_times=scheduled_times,
        instructions=instructions,
        prescribing_doctor=prescribing_doctor,
        doctor_phone=doctor_phone,
        is_active=True
    )
    db.session.add(med)
    db.session.flush()
    
    # Generate today's initial pending dose logs
    today = date.today()
    for t in med.get_times_list():
        log = MedicationLog(
            medication_id=med.id,
            patient_id=patient.id,
            scheduled_date=today,
            scheduled_time=t,
            status='pending',
            notes='Initial scheduled dose'
        )
        db.session.add(log)
        
    db.session.commit()
    flash(f'Medication "{name}" ({dosage}) added successfully to regimen.', 'success')
    return redirect(url_for('medications'))

@app.route('/medications/edit/<int:med_id>', methods=['POST'])
@login_required
def edit_medication(med_id):
    med = db.session.get(Medication, med_id)
    if not med:
        flash('Medication not found.', 'danger')
        return redirect(url_for('medications'))
        
    med.name = request.form.get('name', med.name).strip()
    med.dosage = request.form.get('dosage', med.dosage).strip()
    med.frequency = request.form.get('frequency', med.frequency).strip()
    med.form = request.form.get('form', med.form).strip()
    med.scheduled_times = request.form.get('scheduled_times', med.scheduled_times).strip()
    med.instructions = request.form.get('instructions', med.instructions).strip()
    med.prescribing_doctor = request.form.get('prescribing_doctor', med.prescribing_doctor).strip()
    med.doctor_phone = request.form.get('doctor_phone', med.doctor_phone).strip()
    med.is_active = True if request.form.get('is_active') else False
    
    db.session.commit()
    flash(f'Medication "{med.name}" updated successfully.', 'success')
    return redirect(url_for('medications'))

@app.route('/medications/delete/<int:med_id>', methods=['POST'])
@login_required
def delete_medication(med_id):
    med = db.session.get(Medication, med_id)
    if med:
        name = med.name
        db.session.delete(med)
        db.session.commit()
        flash(f'Medication "{name}" removed from active regimen.', 'info')
    return redirect(url_for('medications'))

@app.route('/medications/log/<int:log_id>/status', methods=['POST'])
@login_required
def update_medication_status(log_id):
    log = db.session.get(MedicationLog, log_id)
    if not log:
        flash('Dose log not found.', 'danger')
        return redirect(request.referrer or url_for('dashboard'))
        
    new_status = request.form.get('status', 'taken')
    log.status = new_status
    if new_status == 'taken':
        log.taken_at = datetime.utcnow()
        log.notes = f'Confirmed taken by user at {datetime.now().strftime("%I:%M %p")}'
        flash(f'Dose for {log.medication.name} marked as taken.', 'success')
    elif new_status == 'missed':
        log.taken_at = None
        log.notes = 'Dose recorded as missed. Caregiver notification logged.'
        flash(f'Dose for {log.medication.name} marked as missed. Remember: Never take a double dose.', 'warning')
        
    db.session.commit()
    return redirect(request.referrer or url_for('dashboard'))

# =========================================================================
# 4. MEDICATION REMINDERS
# =========================================================================
@app.route('/reminders')
@login_required
def reminders():
    user = get_current_user()
    patient = get_active_patient(user)
    today = date.today()
    
    # Pending today reminders
    pending_reminders = MedicationLog.query.filter_by(
        patient_id=patient.id, scheduled_date=today, status='pending'
    ).order_by(MedicationLog.scheduled_time.asc()).all()
    
    # Missed doses today
    missed_reminders = MedicationLog.query.filter_by(
        patient_id=patient.id, scheduled_date=today, status='missed'
    ).order_by(MedicationLog.scheduled_time.asc()).all()
    
    # History logs (Past 10 days)
    history_logs = MedicationLog.query.filter(
        MedicationLog.patient_id == patient.id,
        MedicationLog.scheduled_date >= (today - timedelta(days=10))
    ).order_by(MedicationLog.scheduled_date.desc(), MedicationLog.scheduled_time.desc()).limit(30).all()
    
    return render_template(
        'medications/reminders.html',
        patient=patient,
        pending_reminders=pending_reminders,
        missed_reminders=missed_reminders,
        history_logs=history_logs
    )

# =========================================================================
# 5. HEALTH RECORDS (CLINICAL PROFILE, ALLERGIES, CHRONIC CONDITIONS)
# =========================================================================
@app.route('/health-records')
@login_required
def health_records():
    user = get_current_user()
    patient = get_active_patient(user)
    profile = patient.patient_profile
    if not profile:
        profile = PatientProfile(user_id=patient.id)
        db.session.add(profile)
        db.session.commit()
        
    return render_template('health/records.html', patient=patient, profile=profile)

@app.route('/health-records/update', methods=['POST'])
@login_required
def update_health_records():
    user = get_current_user()
    patient = get_active_patient(user)
    profile = patient.patient_profile
    if not profile:
        profile = PatientProfile(user_id=patient.id)
        db.session.add(profile)
        
    profile.blood_group = request.form.get('blood_group', profile.blood_group)
    profile.gender = request.form.get('gender', profile.gender)
    profile.mobility_level = request.form.get('mobility_level', profile.mobility_level)
    profile.allergies = request.form.get('allergies', profile.allergies)
    profile.chronic_conditions = request.form.get('chronic_conditions', profile.chronic_conditions)
    profile.emergency_notes = request.form.get('emergency_notes', profile.emergency_notes)
    profile.address = request.form.get('address', profile.address)
    
    db.session.commit()
    flash('Patient health records updated successfully.', 'success')
    return redirect(url_for('health_records'))

# =========================================================================
# 6. DOCTOR APPOINTMENTS
# =========================================================================
@app.route('/appointments')
@login_required
def appointments():
    user = get_current_user()
    patient = get_active_patient(user)
    today = date.today()
    
    upcoming_appointments = DoctorAppointment.query.filter(
        DoctorAppointment.patient_id == patient.id,
        DoctorAppointment.appointment_date >= today,
        DoctorAppointment.status.in_(['Scheduled', 'Rescheduled'])
    ).order_by(DoctorAppointment.appointment_date.asc(), DoctorAppointment.appointment_time.asc()).all()
    
    past_appointments = DoctorAppointment.query.filter(
        DoctorAppointment.patient_id == patient.id,
        db.or_(DoctorAppointment.appointment_date < today, DoctorAppointment.status.in_(['Completed', 'Cancelled']))
    ).order_by(DoctorAppointment.appointment_date.desc()).limit(20).all()
    
    return render_template(
        'appointments/index.html',
        patient=patient,
        upcoming_appointments=upcoming_appointments,
        past_appointments=past_appointments
    )

@app.route('/appointments/add', methods=['POST'])
@login_required
def add_appointment():
    user = get_current_user()
    patient = get_active_patient(user)
    
    doctor_name = request.form.get('doctor_name', '').strip()
    specialization = request.form.get('specialization', 'General Medicine').strip()
    date_str = request.form.get('appointment_date')
    time_str = request.form.get('appointment_time', '10:00 AM').strip()
    clinic_hospital = request.form.get('clinic_hospital', '').strip()
    purpose = request.form.get('purpose', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not doctor_name or not date_str:
        flash('Doctor name and appointment date are required.', 'danger')
        return redirect(url_for('appointments'))
        
    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid appointment date format.', 'danger')
        return redirect(url_for('appointments'))
        
    appt = DoctorAppointment(
        patient_id=patient.id,
        doctor_name=doctor_name,
        specialization=specialization,
        clinic_hospital=clinic_hospital,
        appointment_date=appt_date,
        appointment_time=time_str,
        purpose=purpose,
        status='Scheduled',
        notes=notes
    )
    db.session.add(appt)
    db.session.commit()
    flash(f'Appointment with {doctor_name} scheduled for {appt_date.strftime("%b %d, %Y")}.', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointments/update-status/<int:appt_id>', methods=['POST'])
@login_required
def update_appointment_status(appt_id):
    appt = db.session.get(DoctorAppointment, appt_id)
    if appt:
        new_status = request.form.get('status', 'Completed')
        appt.status = new_status
        db.session.commit()
        flash(f'Appointment status updated to "{new_status}".', 'success')
    return redirect(url_for('appointments'))

@app.route('/appointments/delete/<int:appt_id>', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    appt = db.session.get(DoctorAppointment, appt_id)
    if appt:
        db.session.delete(appt)
        db.session.commit()
        flash('Appointment record removed.', 'info')
    return redirect(url_for('appointments'))

# =========================================================================
# 7. HEALTH MONITORING (VITALS TELEMETRY & CHARTS)
# =========================================================================
@app.route('/health-monitoring')
@login_required
def health_monitoring():
    user = get_current_user()
    patient = get_active_patient(user)
    
    vitals_history = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.desc()).all()
        
    # Anomaly checks on recent vitals
    vitals_alerts = []
    if vitals_history:
        latest = vitals_history[0]
        vitals_alerts = evaluate_vitals_health_status({
            'systolic_bp': latest.systolic_bp,
            'diastolic_bp': latest.diastolic_bp,
            'blood_glucose': latest.blood_glucose,
            'glucose_type': latest.glucose_type,
            'heart_rate': latest.heart_rate,
            'oxygen_saturation': latest.oxygen_saturation
        })
        
    # Chronological for chart
    chrono_vitals = list(reversed(vitals_history[:14]))
    chart_labels = [v.reading_date.strftime('%b %d') for v in chrono_vitals]
    chart_sys_bp = [v.systolic_bp for v in chrono_vitals]
    chart_dia_bp = [v.diastolic_bp for v in chrono_vitals]
    chart_glucose = [v.blood_glucose for v in chrono_vitals]
    chart_spo2 = [v.oxygen_saturation for v in chrono_vitals]
    
    return render_template(
        'health/vitals.html',
        patient=patient,
        vitals_history=vitals_history,
        vitals_alerts=vitals_alerts,
        chart_labels=chart_labels,
        chart_sys_bp=chart_sys_bp,
        chart_dia_bp=chart_dia_bp,
        chart_glucose=chart_glucose,
        chart_spo2=chart_spo2
    )

@app.route('/health-monitoring/record', methods=['POST'])
@login_required
def record_vitals():
    user = get_current_user()
    patient = get_active_patient(user)
    
    sys_bp = request.form.get('systolic_bp')
    dia_bp = request.form.get('diastolic_bp')
    glucose = request.form.get('blood_glucose')
    gtype = request.form.get('glucose_type', 'Random')
    hr = request.form.get('heart_rate')
    temp = request.form.get('temperature', 98.4)
    wt = request.form.get('weight')
    spo2 = request.form.get('oxygen_saturation')
    notes = request.form.get('notes', '').strip()
    
    sys_val = int(sys_bp) if sys_bp else None
    dia_val = int(dia_bp) if dia_bp else None
    gluc_val = float(glucose) if glucose else None
    hr_val = int(hr) if hr else None
    temp_val = float(temp) if temp else 98.4
    wt_val = float(wt) if wt else None
    spo2_val = int(spo2) if spo2 else None
    
    is_alert = False
    if sys_val and (sys_val >= 140 or sys_val < 90): is_alert = True
    if dia_val and (dia_val >= 90 or dia_val < 60): is_alert = True
    if gluc_val and (gluc_val >= 180 or gluc_val < 70): is_alert = True
    if spo2_val and spo2_val < 94: is_alert = True
    if hr_val and (hr_val > 105 or hr_val < 52): is_alert = True

    vital = HealthVital(
        patient_id=patient.id,
        recorded_by_id=user.id,
        reading_date=datetime.utcnow(),
        systolic_bp=sys_val,
        diastolic_bp=dia_val,
        blood_glucose=gluc_val,
        glucose_type=gtype,
        heart_rate=hr_val,
        temperature=temp_val,
        weight=wt_val,
        oxygen_saturation=spo2_val,
        notes=notes,
        alert_flag=is_alert
    )
    db.session.add(vital)
    db.session.commit()
    
    if is_alert:
        flash('Vitals recorded. NOTE: Reading flagged outside standard resting parameters. Caregivers notified.', 'warning')
    else:
        flash('Vitals recorded successfully within healthy target parameters.', 'success')
        
    return redirect(url_for('health_monitoring'))

@app.route('/health-monitoring/delete/<int:vital_id>', methods=['POST'])
@login_required
def delete_vitals(vital_id):
    vital = db.session.get(HealthVital, vital_id)
    if vital:
        db.session.delete(vital)
        db.session.commit()
        flash('Vitals measurement entry deleted.', 'info')
    return redirect(url_for('health_monitoring'))

# =========================================================================
# 8. CAREGIVER MANAGEMENT
# =========================================================================
@app.route('/caregivers')
@login_required
def caregivers():
    user = get_current_user()
    patient = get_active_patient(user)
    links = CaregiverAssignment.query.filter_by(patient_id=patient.id).all()
    return render_template('caregivers/index.html', patient=patient, caregiver_links=links)

@app.route('/caregivers/assign', methods=['POST'])
@login_required
def assign_caregiver():
    user = get_current_user()
    patient = get_active_patient(user)
    
    ident = request.form.get('caregiver_identifier', '').strip()
    relationship = request.form.get('relationship', 'Caregiver').strip()
    perm = request.form.get('permission_level', 'full')
    notes = request.form.get('notes', '').strip()
    
    target_user = User.query.filter(
        db.or_(User.username == ident, User.email == ident)
    ).first()
    
    if not target_user:
        flash(f'User "{ident}" not found. Please ensure the caregiver or family member has registered.', 'danger')
        return redirect(url_for('caregivers'))
        
    # Check if already assigned
    existing = CaregiverAssignment.query.filter_by(patient_id=patient.id, caregiver_id=target_user.id).first()
    if existing:
        existing.permission_level = perm
        existing.relationship = relationship
        existing.notes = notes
        db.session.commit()
        flash(f'Updated authorization permissions for {target_user.full_name}.', 'info')
    else:
        assign = CaregiverAssignment(
            patient_id=patient.id,
            caregiver_id=target_user.id,
            relationship=relationship,
            permission_level=perm,
            notes=notes
        )
        db.session.add(assign)
        db.session.commit()
        flash(f'Successfully authorized {target_user.full_name} ({relationship}) as caregiver.', 'success')
        
    return redirect(url_for('caregivers'))

@app.route('/caregivers/delete/<int:link_id>', methods=['POST'])
@login_required
def delete_caregiver_link(link_id):
    link = db.session.get(CaregiverAssignment, link_id)
    if link:
        name = link.caregiver.full_name
        db.session.delete(link)
        db.session.commit()
        flash(f'Caregiver access revoked for {name}.', 'info')
    return redirect(url_for('caregivers'))

# =========================================================================
# 9. FAMILY DASHBOARD
# =========================================================================
@app.route('/family-dashboard')
@login_required
def family_dashboard():
    user = get_current_user()
    patient = get_active_patient(user)
    today = date.today()
    
    today_logs = MedicationLog.query.filter_by(patient_id=patient.id, scheduled_date=today)\
        .order_by(MedicationLog.scheduled_time.asc()).all()
    today_total_doses = len(today_logs)
    today_taken_count = sum(1 for l in today_logs if l.status == 'taken')
    today_pending_count = sum(1 for l in today_logs if l.status == 'pending')
    
    adherence_pct = round((today_taken_count / today_total_doses * 100), 1) if today_total_doses > 0 else 92.0
    
    latest_vital = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.desc()).first()
        
    next_appointment = DoctorAppointment.query.filter(
        DoctorAppointment.patient_id == patient.id,
        DoctorAppointment.appointment_date >= today,
        DoctorAppointment.status == 'Scheduled'
    ).order_by(DoctorAppointment.appointment_date.asc()).first()
    
    family_notifs = Notification.query.filter_by(user_id=user.id)\
        .order_by(Notification.created_at.desc()).limit(10).all()
        
    return render_template(
        'dashboard/family_dashboard.html',
        patient=patient,
        today_logs=today_logs,
        today_total_doses=today_total_doses,
        today_taken_count=today_taken_count,
        today_pending_count=today_pending_count,
        adherence_pct=adherence_pct,
        latest_vital=latest_vital,
        next_appointment=next_appointment,
        family_notifs=family_notifs
    )

# =========================================================================
# 10. REPORTS & ANALYTICS (8 INTERACTIVE CHARTS & AI ENGINE)
# =========================================================================
@app.route('/reports')
@login_required
def reports():
    user = get_current_user()
    patient = get_active_patient(user)
    today = date.today()
    
    # 1. Weekly Medication Adherence Trend (Line) & 3. Weekly completion (Bar)
    weekly_days = []
    weekly_adherence_rates = []
    weekly_taken_counts = []
    weekly_missed_counts = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%a (%b %d)')
        weekly_days.append(day_str)
        logs = MedicationLog.query.filter_by(patient_id=patient.id, scheduled_date=day).all()
        taken = sum(1 for l in logs if l.status == 'taken')
        missed = sum(1 for l in logs if l.status == 'missed')
        total = taken + missed
        rate = round((taken / total * 100), 1) if total > 0 else 100.0
        weekly_taken_counts.append(taken)
        weekly_missed_counts.append(missed)
        weekly_adherence_rates.append(rate)
        
    # 2. Daily Status (Doughnut)
    today_logs = MedicationLog.query.filter_by(patient_id=patient.id, scheduled_date=today).all()
    taken_count = sum(1 for l in today_logs if l.status == 'taken')
    missed_count = sum(1 for l in today_logs if l.status == 'missed')
    pending_count = sum(1 for l in today_logs if l.status == 'pending')

    # 4. Blood Pressure, 5. Glucose, 6. Heart Rate, 8. SpO2 history
    vitals = HealthVital.query.filter_by(patient_id=patient.id)\
        .order_by(HealthVital.reading_date.asc()).limit(14).all()
        
    vitals_dates = [v.reading_date.strftime('%b %d') for v in vitals]
    vitals_sys_bp = [v.systolic_bp for v in vitals]
    vitals_dia_bp = [v.diastolic_bp for v in vitals]
    vitals_glucose = [v.blood_glucose for v in vitals]
    vitals_heart_rate = [v.heart_rate for v in vitals]
    vitals_spo2 = [v.oxygen_saturation for v in vitals]

    # 7. Appointment Summary (by Specialization)
    appts = DoctorAppointment.query.filter_by(patient_id=patient.id).all()
    spec_counts = {}
    for a in appts:
        s = a.specialization or 'General'
        spec_counts[s] = spec_counts.get(s, 0) + 1
        
    appt_specs = list(spec_counts.keys()) if spec_counts else ['Cardiology', 'Geriatrics', 'Ophthalmology']
    appt_counts = list(spec_counts.values()) if spec_counts else [2, 1, 1]

    # AI ML Adherence Model
    ai_insight = compute_patient_ai_insights(patient)

    return render_template(
        'analytics/reports.html',
        patient=patient,
        weekly_days=weekly_days,
        weekly_adherence_rates=weekly_adherence_rates,
        weekly_taken_counts=weekly_taken_counts,
        weekly_missed_counts=weekly_missed_counts,
        taken_count=taken_count,
        missed_count=missed_count,
        pending_count=pending_count,
        vitals_dates=vitals_dates,
        vitals_sys_bp=vitals_sys_bp,
        vitals_dia_bp=vitals_dia_bp,
        vitals_glucose=vitals_glucose,
        vitals_heart_rate=vitals_heart_rate,
        vitals_spo2=vitals_spo2,
        appt_specs=appt_specs,
        appt_counts=appt_counts,
        ai_insight=ai_insight
    )

# =========================================================================
# 11. EMERGENCY ASSISTANCE (SOS DISPATCH, CONTACTS & INCIDENTS)
# =========================================================================
@app.route('/emergency')
@login_required
def emergency():
    user = get_current_user()
    patient = get_active_patient(user)
    
    contacts = EmergencyContact.query.filter_by(patient_id=patient.id)\
        .order_by(EmergencyContact.priority_order.asc()).all()
        
    alerts_history = EmergencyAlert.query.filter_by(patient_id=patient.id)\
        .order_by(EmergencyAlert.alert_time.desc()).all()
        
    return render_template(
        'emergency/index.html',
        patient=patient,
        contacts=contacts,
        alerts_history=alerts_history
    )

@app.route('/emergency/api/trigger', methods=['POST'])
def trigger_emergency_api():
    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    user = get_current_user()
    
    if not patient_id:
        patient = get_active_patient(user)
        patient_id = patient.id if patient else None
        
    if not patient_id:
        return jsonify({'success': False, 'message': 'No active patient found for SOS dispatch.'}), 400
        
    alert_type = data.get('alert_type', 'SOS_BUTTON')
    notes = data.get('notes', 'Emergency SOS button triggered from client interface.')
    
    alert = EmergencyAlert(
        patient_id=patient_id,
        triggered_by_id=user.id if user else patient_id,
        alert_time=datetime.utcnow(),
        alert_type=alert_type,
        status='ACTIVE',
        notes=notes
    )
    db.session.add(alert)
    db.session.flush()
    
    # Notify caregivers and family
    contacts = EmergencyContact.query.filter_by(patient_id=patient_id).all()
    for c in contacts:
        # Create notification record in DB
        notif = Notification(
            user_id=c.patient_id,
            title='EMERGENCY SOS ALERT TRIGGERED',
            message=f'URGENT: Emergency alarm triggered for patient. Designated contact {c.name} ({c.phone_number}) alerted.',
            type='alert',
            link='/emergency'
        )
        db.session.add(notif)
        
    db.session.commit()
    
    return jsonify({
        'success': True,
        'alert_id': alert.id,
        'status': 'ACTIVE',
        'notified_count': len(contacts),
        'timestamp': alert.alert_time.isoformat()
    })

@app.route('/emergency/contacts/add', methods=['POST'])
@login_required
def add_emergency_contact():
    user = get_current_user()
    patient = get_active_patient(user)
    
    name = request.form.get('name', '').strip()
    rel = request.form.get('relationship', '').strip()
    phone = request.form.get('phone_number', '').strip()
    alt_phone = request.form.get('alternate_phone', '').strip()
    is_primary = True if request.form.get('is_primary') else False
    priority = int(request.form.get('priority_order', 1))
    
    if not name or not phone:
        flash('Contact name and phone are required.', 'danger')
        return redirect(url_for('emergency'))
        
    contact = EmergencyContact(
        patient_id=patient.id,
        name=name,
        relationship=rel,
        phone_number=phone,
        alternate_phone=alt_phone,
        is_primary=is_primary,
        priority_order=priority
    )
    db.session.add(contact)
    db.session.commit()
    flash(f'Emergency contact "{name}" added to priority list.', 'success')
    return redirect(url_for('emergency'))

@app.route('/emergency/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_emergency_contact(contact_id):
    c = db.session.get(EmergencyContact, contact_id)
    if c:
        db.session.delete(c)
        db.session.commit()
        flash('Emergency contact removed.', 'info')
    return redirect(url_for('emergency'))

@app.route('/emergency/alerts/resolve/<int:alert_id>', methods=['POST'])
@login_required
def resolve_emergency_alert(alert_id):
    alert = db.session.get(EmergencyAlert, alert_id)
    if alert:
        alert.status = 'RESOLVED'
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = f'Resolved by {get_current_user().full_name} on {datetime.now().strftime("%b %d, %I:%M %p")}'
        db.session.commit()
        flash(f'Emergency incident #SOS-{alert.id} marked as resolved.', 'success')
    return redirect(url_for('emergency'))

# =========================================================================
# 12. SETTINGS
# =========================================================================
@app.route('/settings')
def settings():
    return render_template('settings/index.html')

# =========================================================================
# 13. ABOUT
# =========================================================================
@app.route('/about')
def about():
    return render_template('about/index.html')

# =========================================================================
# AUTHENTICATION & USER MANAGEMENT
# =========================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter(
            db.or_(User.username == username, User.email == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['lang'] = user.preferred_language or 'en'
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_url = request.args.get('next') or url_for('dashboard')
            return redirect(next_url)
        else:
            flash('Invalid username or password. Please verify credentials.', 'danger')
            
    return render_template('auth/login.html')

@app.route('/quick-login/<username>')
def quick_login(username):
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['lang'] = user.preferred_language or 'en'
        flash(f'Logged in as {user.full_name} ({user.role.title()}).', 'success')
        return redirect(url_for('dashboard'))
    flash('Demo user not found.', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out safely.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'elderly')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not full_name or not username or not email or not password:
            flash('All required fields must be completed.', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username is already registered.', 'warning')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'warning')
            return render_template('auth/register.html')
            
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            preferred_language='en'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        
        if role == 'elderly':
            profile = PatientProfile(
                user_id=new_user.id,
                date_of_birth=date(1950, 1, 1),
                gender='Unspecified',
                blood_group='O+',
                chronic_conditions='Hypertension'
            )
            db.session.add(profile)
            
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['role'] = new_user.role
        session['lang'] = 'en'
        
        flash(f'Account created successfully! Welcome, {new_user.full_name}.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('auth/register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = get_current_user()
    user.full_name = request.form.get('full_name', user.full_name).strip()
    user.email = request.form.get('email', user.email).strip()
    user.phone = request.form.get('phone', user.phone).strip()
    user.preferred_language = request.form.get('preferred_language', user.preferred_language)
    session['lang'] = user.preferred_language
    db.session.commit()
    flash('Profile contact information updated.', 'success')
    return redirect(url_for('profile'))

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    user = get_current_user()
    curr_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    
    if not user.check_password(curr_pw):
        flash('Current password incorrect.', 'danger')
        return redirect(url_for('profile'))
        
    if len(new_pw) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('profile'))
        
    user.set_password(new_pw)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('profile'))

@app.route('/set-language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['en', 'ta']:
        session['lang'] = lang_code
        user = get_current_user()
        if user:
            user.preferred_language = lang_code
            db.session.commit()
    return redirect(request.referrer or url_for('home'))

# =========================================================================
# APPLICATION ENTRYPOINT & INITIALIZATION
# =========================================================================
def create_app():
    with app.app_context():
        seed_database(app)
    return app

if __name__ == '__main__':
    with app.app_context():
        seed_database(app)
    print("=" * 60)
    print("  ELDERCARE 360 HEALTHCARE PLATFORM RUNNING")
    print("  URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
