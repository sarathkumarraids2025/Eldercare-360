from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    # Roles: 'elderly', 'caregiver', 'family', 'doctor', 'admin'
    role = db.Column(db.String(20), nullable=False, default='elderly')
    preferred_language = db.Column(db.String(10), default='en') # 'en' or 'ta'
    accessibility_font = db.Column(db.String(20), default='normal') # 'normal', 'large', 'xlarge'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    medications = db.relationship('Medication', backref='patient', lazy='dynamic', cascade="all, delete-orphan")
    vitals = db.relationship('HealthVital', foreign_keys='HealthVital.patient_id', backref='patient', lazy='dynamic', cascade="all, delete-orphan")
    appointments = db.relationship('DoctorAppointment', backref='patient', lazy='dynamic', cascade="all, delete-orphan")
    emergency_contacts = db.relationship('EmergencyContact', backref='patient', lazy='dynamic', cascade="all, delete-orphan")
    emergency_alerts = db.relationship('EmergencyAlert', foreign_keys='EmergencyAlert.patient_id', backref='patient', lazy='dynamic', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'preferred_language': self.preferred_language,
            'accessibility_font': self.accessibility_font
        }

class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), default='Unspecified')
    blood_group = db.Column(db.String(10), default='O+')
    emergency_notes = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    chronic_conditions = db.Column(db.Text, nullable=True) # comma separated
    mobility_level = db.Column(db.String(50), default='Independent')
    address = db.Column(db.String(255), nullable=True)
    
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return 72 # Default representative geriatric age

class CaregiverAssignment(db.Model):
    __tablename__ = 'caregiver_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    relationship = db.Column(db.String(50), default='Caregiver')
    permission_level = db.Column(db.String(20), default='full') # 'full', 'view_only', 'emergency_only'
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='caregiver_links')
    caregiver = db.relationship('User', foreign_keys=[caregiver_id], backref='patient_links')

class Medication(db.Model):
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False) # e.g. "500 mg", "10 ml"
    frequency = db.Column(db.String(50), nullable=False) # e.g. "Once Daily", "Twice Daily"
    form = db.Column(db.String(30), default='Tablet') # Tablet, Capsule, Liquid, Injection, Inhaler, Drops
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    scheduled_times = db.Column(db.String(100), nullable=False, default="08:00") # Comma-separated: "08:00, 20:00"
    instructions = db.Column(db.Text, nullable=True) # e.g. "Take after breakfast with water"
    prescribing_doctor = db.Column(db.String(100), nullable=True)
    doctor_phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    logs = db.relationship('MedicationLog', backref='medication', lazy='dynamic', cascade="all, delete-orphan")
    
    def get_times_list(self):
        if not self.scheduled_times:
            return []
        return [t.strip() for t in self.scheduled_times.split(',') if t.strip()]

class MedicationLog(db.Model):
    __tablename__ = 'medication_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, default=date.today)
    scheduled_time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending', 'taken', 'missed', 'skipped'
    taken_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthVital(db.Model):
    __tablename__ = 'health_vitals'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reading_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    systolic_bp = db.Column(db.Integer, nullable=True) # mmHg
    diastolic_bp = db.Column(db.Integer, nullable=True) # mmHg
    blood_glucose = db.Column(db.Float, nullable=True) # mg/dL
    glucose_type = db.Column(db.String(20), default='Random') # Fasting, Post-meal, Random
    heart_rate = db.Column(db.Integer, nullable=True) # bpm
    temperature = db.Column(db.Float, nullable=True) # °F
    weight = db.Column(db.Float, nullable=True) # kg
    oxygen_saturation = db.Column(db.Integer, nullable=True) # % SpO2
    notes = db.Column(db.Text, nullable=True)
    alert_flag = db.Column(db.Boolean, default=False)
    
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])

class DoctorAppointment(db.Model):
    __tablename__ = 'doctor_appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), default='General Medicine')
    clinic_hospital = db.Column(db.String(150), nullable=True)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(20), nullable=False)
    purpose = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Scheduled') # Scheduled, Completed, Cancelled, Rescheduled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    priority_order = db.Column(db.Integer, default=1)

class EmergencyAlert(db.Model):
    __tablename__ = 'emergency_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    triggered_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    alert_time = db.Column(db.DateTime, default=datetime.utcnow)
    alert_type = db.Column(db.String(50), default='SOS_BUTTON') # SOS_BUTTON, CRITICAL_VITALS, MISSED_DOSE_STREAK, FALL_ALERT
    status = db.Column(db.String(20), default='ACTIVE') # ACTIVE, ACKNOWLEDGED, RESOLVED
    notes = db.Column(db.Text, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    triggered_by = db.relationship('User', foreign_keys=[triggered_by_id])

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='reminder') # reminder, alert, appointment, system
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
