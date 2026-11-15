"""
ElderCare 360 - Bilingual Translation Dictionary (English & தமிழ்)
Covers all sidebar navigation, titles, buttons, clinical vitals, status badges, and messages.
"""

TRANSLATIONS = {
    'en': {
        # App Title & Branding
        'app_name': 'ElderCare 360',
        'tagline': 'Intelligent Elderly Care & Medication Management Platform',
        
        # Navigation
        'nav_home': 'Home',
        'nav_dashboard': 'Dashboard',
        'nav_medications': 'Medication Management',
        'nav_reminders': 'Medication Reminders',
        'nav_health_records': 'Health Records',
        'nav_appointments': 'Doctor Appointments',
        'nav_monitoring': 'Health Monitoring',
        'nav_caregivers': 'Caregiver Management',
        'nav_family': 'Family Dashboard',
        'nav_reports': 'Reports & Analytics',
        'nav_emergency': 'Emergency Assistance',
        'nav_settings': 'Settings',
        'nav_about': 'About',
        
        # Top bar
        'search_placeholder': 'Search medications, vitals, appointments...',
        'profile': 'My Profile',
        'logout': 'Sign Out',
        'login': 'Sign In',
        'register': 'Register Account',
        'role': 'Role',
        'role_elderly': 'Senior Patient',
        'role_caregiver': 'Caregiver',
        'role_family': 'Family Member',
        'role_doctor': 'Healthcare Professional',
        'role_admin': 'System Administrator',
        'emergency_sos_btn': 'EMERGENCY SOS',
        
        # Dashboard Cards
        'total_meds': 'Active Medications',
        'today_doses': "Today's Doses",
        'taken_doses': 'Doses Completed',
        'missed_doses': 'Missed Doses',
        'adherence_rate': 'Adherence Rate',
        'upcoming_appt': 'Next Appointment',
        'latest_bp': 'Latest Blood Pressure',
        'latest_glucose': 'Latest Blood Sugar',
        'heart_rate': 'Heart Rate',
        'oxygen_sat': 'SpO2 Oxygen',
        'body_temp': 'Temperature',
        'weight': 'Weight',
        
        # Medication Management
        'add_medication': 'Add New Medication',
        'edit_medication': 'Edit Medication',
        'med_name': 'Medicine Name',
        'dosage': 'Dosage',
        'frequency': 'Frequency',
        'form': 'Form / Type',
        'scheduled_time': 'Scheduled Times',
        'instructions': 'Instructions / Food Advice',
        'doctor': 'Prescribing Doctor',
        'status': 'Status',
        'active': 'Active',
        'completed': 'Completed',
        'actions': 'Actions',
        'mark_taken': 'Mark as Taken',
        'mark_missed': 'Mark as Missed',
        'view_schedule': "Today's Schedule",
        'warning_double_dose': 'IMPORTANT SAFETY NOTE: Never double your dose after a missed dose. Contact your doctor or pharmacist if unsure.',
        
        # Health Monitoring
        'record_vitals': 'Record New Vitals',
        'bp_systolic': 'Systolic (mmHg)',
        'bp_diastolic': 'Diastolic (mmHg)',
        'blood_sugar': 'Blood Sugar (mg/dL)',
        'glucose_type': 'Meal Timing',
        'fasting': 'Fasting',
        'post_meal': 'Post-Meal',
        'random': 'Random',
        'vitals_normal': 'Normal Range',
        'vitals_elevated': 'Elevated / Attention Needed',
        'vitals_critical': 'Critical Alert',
        
        # Emergency Assistance
        'emergency_alert_title': 'Emergency SOS Assistance',
        'trigger_sos': 'TRIGGER EMERGENCY SOS',
        'sos_confirm': 'Are you sure you want to trigger an Emergency SOS Alert? This will alert all primary caregivers, doctors, and log an urgent event.',
        'sos_cancel': 'Cancel Alert',
        'primary_contacts': 'Designated Emergency Contacts',
        'add_contact': 'Add Emergency Contact',
        'contact_name': 'Contact Name',
        'relationship': 'Relationship',
        'phone': 'Emergency Phone',
        
        # AI Adherence Intelligence
        'ai_intelligence_title': 'AI Medication Adherence & Risk Intelligence',
        'risk_level': 'Adherence Risk Level',
        'risk_low': 'Low Risk (High Adherence)',
        'risk_moderate': 'Moderate Risk (Attention Required)',
        'risk_high': 'High Risk (Intervention Needed)',
        'ai_confidence': 'Model Prediction Confidence',
        'adherence_probability': 'Adherence Probability',
        'top_factors': 'Contributing Behavioral Factors',
        'recommendations': 'Clinical Recommendations for Caregivers',
        'insufficient_data': 'Insufficient historical records. Minimum 3 doses or vitals required for statistical confidence.',
        
        # Buttons & Common
        'save': 'Save Changes',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'view_details': 'View Details',
        'filter': 'Filter',
        'search': 'Search',
        'language': 'Language',
        'english': 'English',
        'tamil': 'தமிழ் (Tamil)',
        'text_size': 'Text Size',
        'text_normal': 'Normal',
        'text_large': 'Large',
        'text_xlarge': 'Extra Large',
        'contrast_mode': 'High Contrast',
        'date': 'Date',
        'time': 'Time',
        'notes': 'Notes / Remarks'
    },
    'ta': {
        # App Title & Branding
        'app_name': 'எல்டர்கேர் 360',
        'tagline': 'முதியோர் பராமரிப்பு & மருந்து மேலாண்மை தளம்',
        
        # Navigation (All 13 Sidebar Items)
        'nav_home': 'முகப்பு',
        'nav_dashboard': 'கட்டுப்பாட்டுப் பலகை',
        'nav_medications': 'மருந்து மேலாண்மை',
        'nav_reminders': 'மருந்து நினைவூட்டல்கள்',
        'nav_health_records': 'சுகாதார பதிவுகள்',
        'nav_appointments': 'மருத்துவர் சந்திப்புகள்',
        'nav_monitoring': 'உடல்நல கண்காணிப்பு',
        'nav_caregivers': 'பராமரிப்பாளர் மேலாண்மை',
        'nav_family': 'குடும்ப முகப்பு',
        'nav_reports': 'அறிக்கைகள் & பகுப்பாய்வு',
        'nav_emergency': 'அவசர உதவி',
        'nav_settings': 'அமைப்புகள்',
        'nav_about': 'எங்களை பற்றி',
        
        # Top bar
        'search_placeholder': 'மருந்துகள், அளவீடுகள், சந்திப்புகளைத் தேடுங்கள்...',
        'profile': 'என் விவரக்குறிப்பு',
        'logout': 'வெளியேறு',
        'login': 'உள்நுழை',
        'register': 'பதிவு செய்',
        'role': 'பணிப்பொறுப்பு',
        'role_elderly': 'முதியவர் / நோயாளி',
        'role_caregiver': 'பராமரிப்பாளர்',
        'role_family': 'குடும்ப உறுப்பினர்',
        'role_doctor': 'மருத்துவர்',
        'role_admin': 'நிர்வாகி',
        'emergency_sos_btn': 'அவசர உதவி (SOS)',
        
        # Dashboard Cards
        'total_meds': 'செயலில் உள்ள மருந்துகள்',
        'today_doses': 'இன்றைய மருந்தளவுகள்',
        'taken_doses': 'எடுக்கப்பட்ட மருந்துகள்',
        'missed_doses': 'தவறவிடப்பட்டவை',
        'adherence_rate': 'மருந்து உட்கொள்ளும் வீதம்',
        'upcoming_appt': 'அடுத்த சந்திப்பு',
        'latest_bp': 'சமீபத்திய இரத்த அழுத்தம்',
        'latest_glucose': 'சமீபத்திய சர்க்கரை அளவு',
        'heart_rate': 'இதயத் துடிப்பு',
        'oxygen_sat': 'ஆக்சிஜன் அளவு (SpO2)',
        'body_temp': 'உடல் வெப்பநிலை',
        'weight': 'எடை',
        
        # Medication Management
        'add_medication': 'புதிய மருந்து சேர்க்க',
        'edit_medication': 'மருந்து திருத்து',
        'med_name': 'மருந்தின் பெயர்',
        'dosage': 'மருந்தளவு',
        'frequency': 'அதிர்வெண் (தடவைகள்)',
        'form': 'வடிவம் (மாத்திரை/சிரப்)',
        'scheduled_time': 'திட்டமிடப்பட்ட நேரம்',
        'instructions': 'உணவு வழிமுறைகள்',
        'doctor': 'பரிந்துரைத்த மருத்துவர்',
        'status': 'நிலை',
        'active': 'செயலில் உள்ளது',
        'completed': 'முடிவடைந்தது',
        'actions': 'செயல்கள்',
        'mark_taken': 'எடுக்கப்பட்டது என குறிக்க',
        'mark_missed': 'தவறவிடப்பட்டது என குறிக்க',
        'view_schedule': 'இன்றைய அட்டவணை',
        'warning_double_dose': 'முக்கிய பாதுகாப்பு எச்சரிக்கை: தவறவிட்ட மருந்திற்காக இரட்டை மாத்திரை எடுக்காதீர்கள். மருத்துவரை அணுகவும்.',
        
        # Health Monitoring
        'record_vitals': 'புதிய அளவீடு பதிவு செய்',
        'bp_systolic': 'சிஸ்டாலிக் (mmHg)',
        'bp_diastolic': 'டயஸ்டாலிக் (mmHg)',
        'blood_sugar': 'இரத்த சர்க்கரை (mg/dL)',
        'glucose_type': 'உணவு நேரம்',
        'fasting': 'உணவுக்கு முன் (வெறும் வயிறு)',
        'post_meal': 'உணவுக்குப் பின்',
        'random': 'வழக்கமான நேரம்',
        'vitals_normal': 'சாதாரண வரம்பு',
        'vitals_elevated': 'கவனம் தேவைப்படும் அளவு',
        'vitals_critical': 'அவசர எச்சரிக்கை',
        
        # Emergency Assistance
        'emergency_alert_title': 'அவசர உதவி (SOS)',
        'trigger_sos': 'அவசர உதவி பொத்தானை அழுத்துக',
        'sos_confirm': 'அவசர உதவி எச்சரிக்கையை அனுப்ப விரும்புகிறீர்களா? இது உங்கள் பராமரிப்பாளர் மற்றும் குடும்பத்தினருக்கு உடனடியாகத் தெரிவிக்கப்படும்.',
        'sos_cancel': 'ரத்து செய்',
        'primary_contacts': 'அவசர தொடர்பு எண்கள்',
        'add_contact': 'புதிய தொடர்பு சேர்க்க',
        'contact_name': 'தொடர்பு பெயர்',
        'relationship': 'உறவுமுறை',
        'phone': 'அவசர தொலைபேசி எண்',
        
        # AI Adherence Intelligence
        'ai_intelligence_title': 'AI மருந்து உட்கொள்ளல் & இடர் நுண்ணறிவு',
        'risk_level': 'இடர் நிலை',
        'risk_low': 'குறைந்த இடர் (சிறந்த மருந்து உட்கொள்ளல்)',
        'risk_moderate': 'மிதமான இடர் (கண்காணிப்பு தேவை)',
        'risk_high': 'அதிக இடர் (உடனடி தலையீடு தேவை)',
        'ai_confidence': 'கணிப்பு துல்லியம்',
        'adherence_probability': 'மருந்து உட்கொள்ளும் நிகழ்தகவு',
        'top_factors': 'முக்கிய காரணிகள்',
        'recommendations': 'பராமரிப்பாளருக்கான மருத்துவ பரிந்துரைகள்',
        'insufficient_data': 'போதுமான வரலாற்று தரவுகள் இல்லை. துல்லியமான கணிப்பிற்கு குறைந்தபட்சம் 3 பதிவுகள் தேவை.',
        
        # Buttons & Common
        'save': 'சேமிக்க',
        'cancel': 'ரத்து',
        'delete': 'நீக்கு',
        'edit': 'திருத்து',
        'view_details': 'விவரங்களை காண்க',
        'filter': 'வடிகட்டுக',
        'search': 'தேடு',
        'language': 'மொழி',
        'english': 'English',
        'tamil': 'தமிழ்',
        'text_size': 'எழுத்து அளவு',
        'text_normal': 'வழக்கமான அளவு',
        'text_large': 'பெரிய அளவு',
        'text_xlarge': 'மிகப்பெரிய அளவு',
        'contrast_mode': 'உயர் மாறுபட்ட நிறம்',
        'date': 'தேதி',
        'time': 'நேரம்',
        'notes': 'குறிப்புகள்'
    }
}

def translate(key, lang='en', default=None):
    """Returns the translation for the given key and language code."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    if key in lang_dict:
        return lang_dict[key]
    # Fallback to English
    return TRANSLATIONS['en'].get(key, default or key)
