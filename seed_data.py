"""
ElderCare 360 - Database Initializer & Realistic Clinical Seed Data
Creates users for all roles (Elderly, Caregiver, Family, Doctor, Admin),
realistic medication regimens, multi-day logs, vitals history, and appointments.
"""

from datetime import datetime, date, timedelta
import random
from models import db, User, PatientProfile, CaregiverAssignment, Medication, MedicationLog, HealthVital, DoctorAppointment, EmergencyContact, EmergencyAlert, Notification

def seed_database(app):
    with app.app_context():
        db.create_all()
        
        # Check if already seeded
        if User.query.filter_by(username='ramalingam').first():
            print("Database already contains seed data.")
            return

        print("Seeding database with clinical elderly care dataset...")

        # 1. USERS & ROLES
        # Elderly Patient: Mr. S. Ramalingam (Age 74)
        elderly_user = User(
            username='ramalingam',
            email='ramalingam@eldercare360.org',
            full_name='Mr. S. Ramalingam',
            phone='+91 98401 23456',
            role='elderly',
            preferred_language='en',
            accessibility_font='normal'
        )
        elderly_user.set_password('senior123')
        db.session.add(elderly_user)
        db.session.flush()

        profile = PatientProfile(
            user_id=elderly_user.id,
            date_of_birth=date(1952, 4, 12),
            gender='Male',
            blood_group='B+',
            emergency_notes='History of mild transient ischemic attack (2022). Allergic to Penicillin. Uses walking stick for support outdoors.',
            allergies='Penicillin, Sulfa drugs',
            chronic_conditions='Hypertension, Type-2 Diabetes Mellitus, Mild Osteoarthritis',
            mobility_level='Assisted (Walking Stick)',
            address='Flat 4B, Kaveri Towers, Anna Nagar West, Chennai - 600040'
        )
        db.session.add(profile)

        # Caregiver: Nurse Anitha
        caregiver_user = User(
            username='nurse_anitha',
            email='anitha.care@eldercare360.org',
            full_name='Nurse Anitha R.',
            phone='+91 97890 54321',
            role='caregiver',
            preferred_language='en'
        )
        caregiver_user.set_password('caregiver123')
        db.session.add(caregiver_user)
        db.session.flush()

        # Family Member: Son Vijay
        family_user = User(
            username='vijay_son',
            email='vijay.ram@globaltech.com',
            full_name='Vijay Ramalingam',
            phone='+91 94440 88990',
            role='family',
            preferred_language='en'
        )
        family_user.set_password('family123')
        db.session.add(family_user)
        db.session.flush()

        # Doctor: Dr. K. Subramanian
        doctor_user = User(
            username='dr_subramanian',
            email='dr.subramanian@apollohospitals.org',
            full_name='Dr. K. Subramanian, MD, DNB',
            phone='+91 98840 11223',
            role='doctor',
            preferred_language='en'
        )
        doctor_user.set_password('doctor123')
        db.session.add(doctor_user)
        db.session.flush()

        # Administrator
        admin_user = User(
            username='admin',
            email='admin@eldercare360.org',
            full_name='Healthcare System Administrator',
            phone='+91 99999 00000',
            role='admin',
            preferred_language='en'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.flush()

        # 2. CAREGIVER & FAMILY ASSIGNMENTS
        c_assign1 = CaregiverAssignment(
            patient_id=elderly_user.id,
            caregiver_id=caregiver_user.id,
            relationship='Primary Care Nurse',
            permission_level='full',
            notes='Visits daily from 8:00 AM to 1:00 PM. Manages morning and afternoon medications and vitals logs.'
        )
        c_assign2 = CaregiverAssignment(
            patient_id=elderly_user.id,
            caregiver_id=family_user.id,
            relationship='Son (Primary Contact)',
            permission_level='full',
            notes='Resides 15 minutes away. Receives instant emergency alerts and weekly adherence summaries.'
        )
        db.session.add_all([c_assign1, c_assign2])

        # 3. MEDICATIONS
        medications_data = [
            {
                'name': 'Metformin Hydrochloride',
                'dosage': '500 mg',
                'frequency': 'Twice Daily',
                'form': 'Tablet',
                'start_date': date.today() - timedelta(days=90),
                'scheduled_times': '08:00, 20:00',
                'instructions': 'Take with or immediately after meals with plenty of water. Do not crush.',
                'doctor': 'Dr. K. Subramanian, MD (Endocrinologist)'
            },
            {
                'name': 'Amlodipine Besylate',
                'dosage': '5 mg',
                'frequency': 'Once Daily',
                'form': 'Tablet',
                'start_date': date.today() - timedelta(days=120),
                'scheduled_times': '08:00',
                'instructions': 'Take in the morning with water. Monitor blood pressure weekly.',
                'doctor': 'Dr. K. Subramanian, MD (Cardiologist)'
            },
            {
                'name': 'Atorvastatin Calcium',
                'dosage': '20 mg',
                'frequency': 'Once Daily',
                'form': 'Tablet',
                'start_date': date.today() - timedelta(days=180),
                'scheduled_times': '21:00',
                'instructions': 'Take at night before bed. Avoid grapefruit consumption.',
                'doctor': 'Dr. K. Subramanian, MD (Cardiologist)'
            },
            {
                'name': 'Glimepiride',
                'dosage': '1 mg',
                'frequency': 'Once Daily',
                'form': 'Tablet',
                'start_date': date.today() - timedelta(days=60),
                'scheduled_times': '08:00',
                'instructions': 'Take 15 minutes before breakfast. Watch for signs of low blood sugar.',
                'doctor': 'Dr. K. Subramanian, MD (Endocrinologist)'
            },
            {
                'name': 'Calcium Carbonate + Vit D3',
                'dosage': '500 mg / 400 IU',
                'frequency': 'Once Daily',
                'form': 'Tablet',
                'start_date': date.today() - timedelta(days=45),
                'scheduled_times': '13:00',
                'instructions': 'Take with lunch. Supports bone mineral density.',
                'doctor': 'Dr. V. Meenakshi, Orthopedic Specialist'
            }
        ]

        created_meds = []
        for mdata in medications_data:
            med = Medication(
                patient_id=elderly_user.id,
                name=mdata['name'],
                dosage=mdata['dosage'],
                frequency=mdata['frequency'],
                form=mdata['form'],
                start_date=mdata['start_date'],
                end_date=None,
                scheduled_times=mdata['scheduled_times'],
                instructions=mdata['instructions'],
                prescribing_doctor=mdata['doctor'],
                doctor_phone='+91 98840 11223',
                is_active=True
            )
            db.session.add(med)
            created_meds.append(med)
        db.session.flush()

        # 4. MEDICATION LOGS (Past 10 days + Today)
        today = date.today()
        for day_offset in range(10, 0, -1):
            past_date = today - timedelta(days=day_offset)
            for med in created_meds:
                for t in med.get_times_list():
                    # 88% compliance rate with realistic occasional missed evening doses
                    is_missed = (random.random() < 0.12) or (t == '21:00' and day_offset in [3, 7])
                    status = 'missed' if is_missed else 'taken'
                    taken_time = datetime.combine(past_date, datetime.strptime(t, '%H:%M').time()) + timedelta(minutes=random.randint(5, 30)) if status == 'taken' else None
                    log = MedicationLog(
                        medication_id=med.id,
                        patient_id=elderly_user.id,
                        scheduled_date=past_date,
                        scheduled_time=t,
                        status=status,
                        taken_at=taken_time,
                        notes='Taken on schedule with water' if status == 'taken' else 'Dose skipped due to fatigue; caregiver notified'
                    )
                    db.session.add(log)

        # Today's logs
        for med in created_meds:
            for t in med.get_times_list():
                if t in ['08:00', '13:00']:
                    status = 'taken'
                    taken_time = datetime.combine(today, datetime.strptime(t, '%H:%M').time()) + timedelta(minutes=10)
                else:
                    status = 'pending' # Evening doses pending
                    taken_time = None
                log = MedicationLog(
                    medication_id=med.id,
                    patient_id=elderly_user.id,
                    scheduled_date=today,
                    scheduled_time=t,
                    status=status,
                    taken_at=taken_time,
                    notes='Taken under Nurse Anitha supervision' if status == 'taken' else 'Awaiting scheduled evening window'
                )
                db.session.add(log)

        # 5. HEALTH VITALS (Past 14 days)
        vitals_samples = [
            # days_ago, sys, dia, glucose, gtype, hr, temp, weight, spo2
            (14, 138, 86, 135, 'Post-meal', 74, 98.4, 68.5, 97),
            (13, 132, 84, 105, 'Fasting',   72, 98.2, 68.4, 98),
            (12, 136, 85, 142, 'Post-meal', 76, 98.6, 68.5, 97),
            (11, 140, 88, 112, 'Fasting',   78, 98.4, 68.3, 96),
            (10, 130, 82, 128, 'Post-meal', 70, 98.1, 68.4, 98),
            (9,  134, 84, 108, 'Fasting',   73, 98.3, 68.2, 97),
            (8,  142, 89, 155, 'Post-meal', 80, 98.5, 68.3, 96),
            (7,  135, 85, 110, 'Fasting',   75, 98.2, 68.1, 98),
            (6,  128, 80, 124, 'Post-meal', 71, 98.0, 68.2, 98),
            (5,  136, 86, 115, 'Fasting',   74, 98.4, 68.0, 97),
            (4,  130, 82, 138, 'Post-meal', 72, 98.3, 68.1, 98),
            (3,  138, 88, 118, 'Fasting',   76, 98.5, 68.0, 97),
            (2,  132, 84, 130, 'Post-meal', 73, 98.2, 67.9, 98),
            (1,  134, 85, 112, 'Fasting',   75, 98.3, 68.0, 97),
            (0,  128, 82, 108, 'Fasting',   72, 98.4, 68.0, 98),
        ]

        for item in vitals_samples:
            days_ago, sys_bp, dia_bp, gluc, gtype, hr, temp, wt, spo2 = item
            v_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(1, 4))
            vital = HealthVital(
                patient_id=elderly_user.id,
                recorded_by_id=caregiver_user.id,
                reading_date=v_time,
                systolic_bp=sys_bp,
                diastolic_bp=dia_bp,
                blood_glucose=gluc,
                glucose_type=gtype,
                heart_rate=hr,
                temperature=temp,
                weight=wt,
                oxygen_saturation=spo2,
                notes=f"Routine daily vitals reading recorded by {caregiver_user.full_name}",
                alert_flag=(sys_bp >= 140 or dia_bp >= 90 or gluc >= 180 or spo2 < 95)
            )
            db.session.add(vital)

        # 6. DOCTOR APPOINTMENTS
        appts = [
            {
                'doctor': 'Dr. K. Subramanian',
                'spec': 'Cardiology & Geriatrics',
                'hospital': 'Apollo Speciality Hospitals, Chennai',
                'date': today + timedelta(days=3),
                'time': '10:30 AM',
                'purpose': 'Bi-monthly Hypertension & Statin therapy review. Complete Lipid panel test discussion.',
                'status': 'Scheduled'
            },
            {
                'doctor': 'Dr. S. Radhakrishnan',
                'spec': 'Ophthalmology',
                'hospital': 'Sankara Nethralaya, Chennai',
                'date': today + timedelta(days=12),
                'time': '02:00 PM',
                'purpose': 'Diabetic Retinopathy annual dilated eye exam and cataract checkup.',
                'status': 'Scheduled'
            },
            {
                'doctor': 'Dr. V. Meenakshi',
                'spec': 'Orthopedics & Joint Care',
                'hospital': 'Kaveri Hospital, Anna Nagar',
                'date': today - timedelta(days=25),
                'time': '11:15 AM',
                'purpose': 'Knee osteoarthritis evaluation and physical therapy guidance.',
                'status': 'Completed'
            }
        ]
        for a in appts:
            appt = DoctorAppointment(
                patient_id=elderly_user.id,
                doctor_name=a['doctor'],
                specialization=a['spec'],
                clinic_hospital=a['hospital'],
                appointment_date=a['date'],
                appointment_time=a['time'],
                purpose=a['purpose'],
                status=a['status'],
                notes='Accompanied by Nurse Anitha. Patient advised to bring previous test records.'
            )
            db.session.add(appt)

        # 7. EMERGENCY CONTACTS
        e_contacts = [
            {
                'name': 'Vijay Ramalingam',
                'rel': 'Son (Primary Guardian)',
                'phone': '+91 94440 88990',
                'alt': '+91 44 2618 1234',
                'primary': True,
                'priority': 1
            },
            {
                'name': 'Nurse Anitha R.',
                'rel': 'Primary Day Caregiver',
                'phone': '+91 97890 54321',
                'alt': '+91 44 2620 9876',
                'primary': False,
                'priority': 2
            },
            {
                'name': 'Dr. K. Subramanian',
                'rel': 'Attending Physician (Geriatrician)',
                'phone': '+91 98840 11223',
                'alt': '+91 44 2829 0200',
                'primary': False,
                'priority': 3
            },
            {
                'name': 'Emergency Ambulance Services',
                'rel': 'Emergency Response (Apollo/108)',
                'phone': '108',
                'alt': '112',
                'primary': False,
                'priority': 4
            }
        ]
        for ec in e_contacts:
            contact = EmergencyContact(
                patient_id=elderly_user.id,
                name=ec['name'],
                relationship=ec['rel'],
                phone_number=ec['phone'],
                alternate_phone=ec['alt'],
                is_primary=ec['primary'],
                priority_order=ec['priority']
            )
            db.session.add(contact)

        # 8. EMERGENCY ALERTS LOG
        past_alert = EmergencyAlert(
            patient_id=elderly_user.id,
            triggered_by_id=elderly_user.id,
            alert_time=datetime.utcnow() - timedelta(days=18),
            alert_type='SOS_BUTTON',
            status='RESOLVED',
            notes='Patient felt dizzy after getting out of bed quickly. SOS button pressed.',
            resolution_notes='Nurse Anitha arrived in 6 minutes. Vitals checked: BP 118/74, Glucose 110 mg/dL. Rehydrated with electrolyte drink. Resting normally.',
            resolved_at=datetime.utcnow() - timedelta(days=18, hours=23)
        )
        db.session.add(past_alert)

        # 9. NOTIFICATIONS
        notifs = [
            {
                'user_id': elderly_user.id,
                'title': 'Upcoming Dose Reminder: Atorvastatin 20mg',
                'message': 'Scheduled tonight at 09:00 PM. Take with a glass of water.',
                'type': 'reminder',
                'link': '/reminders'
            },
            {
                'user_id': elderly_user.id,
                'title': 'Doctor Appointment in 3 Days',
                'message': 'Consultation with Dr. K. Subramanian on Thursday at 10:30 AM.',
                'type': 'appointment',
                'link': '/appointments'
            },
            {
                'user_id': family_user.id,
                'title': 'Weekly Adherence Report Available',
                'message': 'Mr. Ramalingam achieved 91.4% medication adherence this week.',
                'type': 'system',
                'link': '/family-dashboard'
            },
            {
                'user_id': caregiver_user.id,
                'title': 'Vitals Update: Blood Pressure Stable',
                'message': 'Morning BP recorded at 128/82 mmHg (within target range).',
                'type': 'system',
                'link': '/health-monitoring'
            }
        ]
        for n in notifs:
            notif = Notification(
                user_id=n['user_id'],
                title=n['title'],
                message=n['message'],
                type=n['type'],
                link=n['link']
            )
            db.session.add(notif)

        db.session.commit()
        print("Database seeded successfully with complete clinical demo records!")

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eldercare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    seed_database(app)
