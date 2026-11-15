"""
ElderCare 360 - Comprehensive Automated Test Suite
Verifies all 13 sidebar pages, authentication, RBAC, Medication CRUD,
Health Vitals telemetry, Doctor appointments, Emergency SOS, Bilingual Tamil/English,
and AI Machine Learning model inference.
"""

import unittest
from datetime import date, datetime, timedelta
import json
import sys
import os

# Add ElderCare360 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Medication, MedicationLog, HealthVital, DoctorAppointment, EmergencyContact, EmergencyAlert
from ai_engine import predict_patient_adherence, evaluate_vitals_health_status, get_model_payload
from translations import translate

class ElderCarePlatformTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            from seed_data import seed_database
            seed_database(app)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # 1. Mandatory Background Image & Home Page Test
    def test_home_page_and_mandatory_background_image(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        # Check mandatory background image reference in hero section
        self.assertIn('hero-healthcare.jpg', html)
        self.assertIn('hero-healthcare-section', html)
        self.assertIn('ElderCare 360', html)
        print("✓ Home page loaded with mandatory colourful healthcare background image.")

    # 2. All 13 Mandatory Left-Sidebar Navigation Pages
    def test_all_13_sidebar_routes_load_successfully(self):
        # Log in first
        self.client.get('/quick-login/ramalingam')
        
        routes = [
            ('/', 'Home'),
            ('/dashboard', 'Dashboard'),
            ('/medications', 'Medication Management'),
            ('/reminders', 'Medication Reminders'),
            ('/health-records', 'Health Records'),
            ('/appointments', 'Doctor Appointments'),
            ('/health-monitoring', 'Health Monitoring'),
            ('/caregivers', 'Caregiver Management'),
            ('/family-dashboard', 'Family Dashboard'),
            ('/reports', 'Reports & Analytics'),
            ('/emergency', 'Emergency Assistance'),
            ('/settings', 'Settings'),
            ('/about', 'About')
        ]
        
        for path, name in routes:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Route {path} ({name}) failed with {res.status_code}")
            html = res.data.decode('utf-8')
            # Verify the left sidebar exists
            self.assertIn('id="left-sidebar"', html)
            self.assertIn('class="left-sidebar', html)
            print(f"✓ Sidebar Item: {name} ({path}) - 200 OK")

    # 3. Authentication & RBAC Test
    def test_authentication_workflow(self):
        # Register new caregiver
        res = self.client.post('/register', data={
            'full_name': 'Test Registered Nurse',
            'username': 'nurse_test',
            'email': 'nurse.test@hospital.org',
            'phone': '+91 91234 56789',
            'role': 'caregiver',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with app.app_context():
            user = User.query.filter_by(username='nurse_test').first()
            self.assertIsNotNone(user)
            self.assertTrue(user.check_password('password123'))
            self.assertFalse(user.check_password('wrongpass'))
            self.assertEqual(user.role, 'caregiver')
        print("✓ User registration, role mapping, and password hashing verified.")

    # 4. Medication CRUD & Status Tracking
    def test_medication_crud_and_status(self):
        self.client.get('/quick-login/ramalingam')
        
        # Add medication
        res = self.client.post('/medications/add', data={
            'name': 'Aspirin Cardio',
            'dosage': '75 mg',
            'frequency': 'Once Daily',
            'form': 'Tablet',
            'scheduled_times': '09:00',
            'instructions': 'Take with lunch',
            'prescribing_doctor': 'Dr. Subramanian',
            'doctor_phone': '+91 98840 11223'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with app.app_context():
            med = Medication.query.filter_by(name='Aspirin Cardio').first()
            self.assertIsNotNone(med)
            self.assertEqual(med.dosage, '75 mg')
            
            # Check today's generated dose log
            log = MedicationLog.query.filter_by(medication_id=med.id).first()
            self.assertIsNotNone(log)
            self.assertEqual(log.status, 'pending')
            
            # Mark dose as taken
            log_id = log.id
            
        res2 = self.client.post(f'/medications/log/{log_id}/status', data={'status': 'taken'}, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        
        with app.app_context():
            updated_log = db.session.get(MedicationLog, log_id)
            self.assertEqual(updated_log.status, 'taken')
            self.assertIsNotNone(updated_log.taken_at)
            
        print("✓ Medication CRUD, scheduled log generation, and taken status updates verified.")

    # 5. Health Monitoring Vitals Telemetry
    def test_vitals_telemetry_and_anomalies(self):
        self.client.get('/quick-login/nurse_anitha')
        
        # Post elevated vitals entry
        res = self.client.post('/health-monitoring/record', data={
            'systolic_bp': '155',
            'diastolic_bp': '95',
            'blood_glucose': '195',
            'glucose_type': 'Post-meal',
            'heart_rate': '88',
            'temperature': '98.6',
            'weight': '68.2',
            'oxygen_saturation': '97',
            'notes': 'Post-exercise blood pressure measurement'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with app.app_context():
            v = HealthVital.query.order_by(HealthVital.id.desc()).first()
            self.assertEqual(v.systolic_bp, 155)
            self.assertEqual(v.blood_glucose, 195.0)
            self.assertTrue(v.alert_flag) # Flagged because systolic >= 140
            
            # Test anomaly evaluator
            alerts = evaluate_vitals_health_status({
                'systolic_bp': v.systolic_bp,
                'diastolic_bp': v.diastolic_bp,
                'blood_glucose': v.blood_glucose,
                'oxygen_saturation': v.oxygen_saturation
            })
            self.assertTrue(len(alerts) >= 2)
            self.assertEqual(alerts[0]['vital'], 'Blood Pressure')
            print("✓ Vitals telemetry logging and clinical threshold anomaly detection verified.")

    # 6. Doctor Appointment Scheduling
    def test_doctor_appointment_scheduling(self):
        self.client.get('/quick-login/ramalingam')
        
        res = self.client.post('/appointments/add', data={
            'doctor_name': 'Dr. K. Subramanian',
            'specialization': 'Geriatrics',
            'appointment_date': (date.today() + timedelta(days=5)).isoformat(),
            'appointment_time': '11:00 AM',
            'clinic_hospital': 'Apollo Hospital',
            'purpose': 'Routine follow-up',
            'notes': 'Bring past glucose logs'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        with app.app_context():
            appt = DoctorAppointment.query.filter_by(doctor_name='Dr. K. Subramanian', status='Scheduled').first()
            self.assertIsNotNone(appt)
            appt_id = appt.id
            
        # Update status to Completed
        res2 = self.client.post(f'/appointments/update-status/{appt_id}', data={'status': 'Completed'}, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        
        with app.app_context():
            appt = db.session.get(DoctorAppointment, appt_id)
            self.assertEqual(appt.status, 'Completed')
            
        print("✓ Doctor appointment scheduling, status transitions, and queries verified.")

    # 7. Emergency SOS Dispatch API
    def test_emergency_sos_dispatch(self):
        self.client.get('/quick-login/ramalingam')
        
        with app.app_context():
            p = User.query.filter_by(username='ramalingam').first()
            pid = p.id
            
        res = self.client.post('/emergency/api/trigger', 
            data=json.dumps({'patient_id': pid, 'alert_type': 'SOS_BUTTON'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'ACTIVE')
        self.assertGreater(data['notified_count'], 0)
        
        with app.app_context():
            alert = db.session.get(EmergencyAlert, data['alert_id'])
            self.assertIsNotNone(alert)
            self.assertEqual(alert.status, 'ACTIVE')
            
        print("✓ Emergency SOS dispatch API, database incident logging, and guardian notification verified.")

    # 8. AI/ML Medication Adherence Inference Model
    def test_ai_ml_adherence_prediction(self):
        payload = get_model_payload()
        self.assertIn('model', payload)
        self.assertIn('accuracy', payload)
        self.assertGreaterEqual(payload['accuracy'], 0.75)
        
        # Test inference with high-risk profile
        high_risk_features = {
            'age': 82,
            'num_medications': 7,
            'daily_dose_count': 6,
            'past_adherence_rate': 0.50,
            'missed_streak': 3,
            'chronic_conditions_count': 4,
            'mobility_level': 2,
            'bp_variability': 22.0,
            'glucose_variability': 35.0
        }
        res = predict_patient_adherence(high_risk_features)
        self.assertIn(res['risk_level'], ['Moderate Risk', 'High Risk'])
        self.assertIn('probabilities', res)
        self.assertGreater(len(res['top_risk_factors']), 0)
        self.assertGreater(len(res['clinical_recommendations']), 0)
        print(f"✓ AI Random Forest model inference verified: Predicted '{res['risk_level']}' with {res['adherence_probability']}% adherence prob.")

    # 9. Bilingual Language Support (English & Tamil)
    def test_bilingual_translations(self):
        # English
        self.assertEqual(translate('nav_home', 'en'), 'Home')
        self.assertEqual(translate('nav_medications', 'en'), 'Medication Management')
        self.assertEqual(translate('nav_emergency', 'en'), 'Emergency Assistance')
        
        # Tamil (தமிழ்)
        self.assertEqual(translate('nav_home', 'ta'), 'முகப்பு')
        self.assertEqual(translate('nav_medications', 'ta'), 'மருந்து மேலாண்மை')
        self.assertEqual(translate('nav_emergency', 'ta'), 'அவசர உதவி')
        self.assertEqual(translate('nav_reminders', 'ta'), 'மருந்து நினைவூட்டல்கள்')
        self.assertEqual(translate('nav_monitoring', 'ta'), 'உடல்நல கண்காணிப்பு')
        print("✓ Bilingual English and Tamil translation dictionaries verified.")

if __name__ == '__main__':
    unittest.main()
