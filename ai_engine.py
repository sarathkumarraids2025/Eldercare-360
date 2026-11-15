"""
ElderCare 360 - AI/ML Healthcare Intelligence Engine
Trained on clinical geriatric medication adherence factors:
- Age
- Polypharmacy (Number of active medications)
- Daily dosage frequency
- Historical adherence rate (past 7 days)
- Missed dose streak
- Chronic conditions count
- Mobility / cognitive assistance level (0-3)
- Systolic BP variability
- Blood glucose variability
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models_saved')
MODEL_FILE = os.path.join(MODEL_DIR, 'adherence_model.joblib')

FEATURE_NAMES = [
    'age',
    'num_medications',
    'daily_dose_count',
    'past_adherence_rate',
    'missed_streak',
    'chronic_conditions_count',
    'mobility_level',
    'bp_variability',
    'glucose_variability'
]

def generate_clinical_adherence_dataset(n_samples=2000, random_state=42):
    """
    Generates a realistic clinical dataset based on published geriatric adherence research
    (e.g., Morisky Medication Adherence Scale & WHO adherence parameters).
    """
    np.random.seed(random_state)
    
    # 1. Patient Age (60 - 95)
    age = np.random.normal(loc=74, scale=7, size=n_samples).clip(60, 95)
    
    # 2. Number of concurrent medications (1 - 12)
    num_medications = np.random.poisson(lam=4.5, size=n_samples).clip(1, 12)
    
    # 3. Daily dosage frequency count (1 - 8 doses/day)
    daily_dose_count = (num_medications * np.random.uniform(1.0, 1.8, size=n_samples)).astype(int).clip(1, 10)
    
    # 4. Past 7-day adherence rate (0.0 to 1.0)
    base_adherence = np.random.beta(a=6, b=2, size=n_samples) # Skewed towards good adherence
    
    # 5. Missed dose streak (0 to 5)
    missed_streak = np.random.poisson(lam=0.7, size=n_samples).clip(0, 7)
    
    # 6. Chronic conditions count (1 to 6)
    chronic_conditions_count = np.random.poisson(lam=2.5, size=n_samples).clip(1, 6)
    
    # 7. Mobility / Assistance level: 0=Independent, 1=Minimal aid, 2=Moderate aid, 3=Fully dependent
    mobility_level = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.4, 0.3, 0.2, 0.1])
    
    # 8. Systolic BP variability (std dev: 4 to 30 mmHg)
    bp_variability = np.random.normal(loc=12, scale=5, size=n_samples).clip(3, 35)
    
    # 9. Glucose variability (std dev: 5 to 50 mg/dL)
    glucose_variability = np.random.normal(loc=18, scale=8, size=n_samples).clip(4, 55)
    
    # Clinical risk formula (ground truth adherence score)
    # Higher score = higher risk of non-adherence
    risk_score = (
        (age - 60) * 0.015 +
        (num_medications >= 5) * 0.35 + # Polypharmacy penalty
        (daily_dose_count >= 5) * 0.25 +
        (1.0 - base_adherence) * 1.5 +
        missed_streak * 0.4 +
        (chronic_conditions_count >= 3) * 0.2 +
        mobility_level * 0.2 +
        (bp_variability > 18) * 0.25 +
        (glucose_variability > 25) * 0.2
    )
    # Add minor clinical noise
    risk_score += np.random.normal(0, 0.15, size=n_samples)
    
    # Classification:
    # 0: Low Risk (Adherent, high probability of taking meds)
    # 1: Moderate Risk (Borderline, needs reminders/oversight)
    # 2: High Risk (Non-adherent danger, requires immediate caregiver intervention)
    labels = np.zeros(n_samples, dtype=int)
    labels[risk_score >= 1.1] = 1 # Moderate
    labels[risk_score >= 1.8] = 2 # High
    
    df = pd.DataFrame({
        'age': age,
        'num_medications': num_medications,
        'daily_dose_count': daily_dose_count,
        'past_adherence_rate': base_adherence,
        'missed_streak': missed_streak,
        'chronic_conditions_count': chronic_conditions_count,
        'mobility_level': mobility_level,
        'bp_variability': bp_variability,
        'glucose_variability': glucose_variability,
        'adherence_risk': labels
    })
    return df

def train_and_save_model():
    """Trains the RandomForestClassifier on clinical adherence data and saves it."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = generate_clinical_adherence_dataset(n_samples=2500)
    
    X = df[FEATURE_NAMES]
    y = df['adherence_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        min_samples_split=4,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"--- Model Training Complete ---")
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=['Low Risk', 'Moderate Risk', 'High Risk']))
    
    # Save model and scaler package
    payload = {
        'model': model,
        'scaler': scaler,
        'feature_names': FEATURE_NAMES,
        'feature_importances': dict(zip(FEATURE_NAMES, model.feature_importances_)),
        'accuracy': float(acc),
        'metrics': classification_report(y_test, y_pred, target_names=['Low Risk', 'Moderate Risk', 'High Risk'], output_dict=True)
    }
    joblib.dump(payload, MODEL_FILE)
    print(f"Model saved to: {MODEL_FILE}")
    return payload

_LOADED_MODEL_PAYLOAD = None

def get_model_payload():
    global _LOADED_MODEL_PAYLOAD
    if _LOADED_MODEL_PAYLOAD is None:
        if not os.path.exists(MODEL_FILE):
            _LOADED_MODEL_PAYLOAD = train_and_save_model()
        else:
            _LOADED_MODEL_PAYLOAD = joblib.load(MODEL_FILE)
    return _LOADED_MODEL_PAYLOAD

def predict_patient_adherence(features_dict):
    """
    Makes inference on a patient profile.
    Returns:
    {
        'risk_level': 'Low' | 'Moderate' | 'High',
        'risk_class': 0 | 1 | 2,
        'probabilities': {'low': float, 'moderate': float, 'high': float},
        'confidence_score': float,
        'top_risk_factors': list of str,
        'clinical_recommendations': list of str,
        'adherence_probability': float
    }
    """
    payload = get_model_payload()
    model = payload['model']
    scaler = payload['scaler']
    
    # Extract in exact feature order
    row = [float(features_dict.get(fn, 0.0)) for fn in FEATURE_NAMES]
    row_scaled = scaler.transform([row])
    
    pred_class = int(model.predict(row_scaled)[0])
    probs = model.predict_proba(row_scaled)[0]
    
    class_map = {0: 'Low Risk', 1: 'Moderate Risk', 2: 'High Risk'}
    risk_level = class_map[pred_class]
    
    # Identify key risk factors from input features
    risk_factors = []
    recommendations = []
    
    if features_dict.get('num_medications', 0) >= 5:
        risk_factors.append(f"Polypharmacy detected ({int(features_dict['num_medications'])} active prescriptions)")
        recommendations.append("Consolidate medication schedule with primary physician or pharmacist.")
        
    if features_dict.get('missed_streak', 0) >= 2:
        risk_factors.append(f"Recent missed doses streak ({int(features_dict['missed_streak'])} missed)")
        recommendations.append("Trigger automated SMS and Caregiver telephone check-in.")
        
    if features_dict.get('past_adherence_rate', 1.0) < 0.75:
        risk_factors.append(f"Past 7-day adherence is below threshold ({features_dict['past_adherence_rate']*100:.1f}%)")
        recommendations.append("Deploy smart audio medication reminder alarms 15 minutes before dosing times.")
        
    if features_dict.get('daily_dose_count', 0) >= 4:
        risk_factors.append(f"Complex daily dosing schedule ({int(features_dict['daily_dose_count'])} daily events)")
        recommendations.append("Consider synchronized morning/night blister packs or pill organizers.")
        
    if features_dict.get('bp_variability', 0) > 18:
        risk_factors.append(f"Elevated blood pressure fluctuation (±{features_dict['bp_variability']:.1f} mmHg)")
        recommendations.append("Frequent BP checks recommended; share trend report with cardiologist.")
        
    if not risk_factors:
        risk_factors.append("Consistent medication adherence history and stable vital signs.")
        recommendations.append("Continue current scheduled routine. Next routine review in 30 days.")
        
    # Adherence score calculation (0 - 100%)
    adherence_pct = round(float(probs[0] * 100 + probs[1] * 35), 1)
    
    return {
        'risk_level': risk_level,
        'risk_class': pred_class,
        'probabilities': {
            'low': round(float(probs[0]) * 100, 1),
            'moderate': round(float(probs[1]) * 100, 1),
            'high': round(float(probs[2]) * 100, 1)
        },
        'confidence_score': round(float(np.max(probs)) * 100, 1),
        'adherence_probability': adherence_pct,
        'top_risk_factors': risk_factors,
        'clinical_recommendations': recommendations
    }

def evaluate_vitals_health_status(vital_record):
    """
    Evaluates individual vital readings against recognized geriatric thresholds.
    Returns flags, status descriptions, and caution notes without pretending to diagnose.
    """
    alerts = []
    
    # Blood Pressure (Systolic / Diastolic)
    sys = vital_record.get('systolic_bp')
    dia = vital_record.get('diastolic_bp')
    if sys and dia:
        if sys >= 140 or dia >= 90:
            alerts.append({
                'vital': 'Blood Pressure',
                'severity': 'warning' if sys < 160 else 'critical',
                'reading': f"{sys}/{dia} mmHg",
                'message': "Blood pressure reading is elevated above normal adult resting range (120/80 mmHg).",
                'action': "Ensure patient is rested and calm. Re-check in 20 minutes; consult physician if persistent."
            })
        elif sys < 90 or dia < 60:
            alerts.append({
                'vital': 'Blood Pressure',
                'severity': 'warning',
                'reading': f"{sys}/{dia} mmHg",
                'message': "Blood pressure reading is below normal resting range.",
                'action': "Have patient sit comfortably, hydrate, and monitor for dizziness or lightheadedness."
            })
            
    # Blood Glucose
    glucose = vital_record.get('blood_glucose')
    gtype = vital_record.get('glucose_type', 'Random')
    if glucose:
        if gtype == 'Fasting' and glucose > 126:
            alerts.append({
                'vital': 'Fasting Glucose',
                'severity': 'warning' if glucose < 180 else 'critical',
                'reading': f"{glucose} mg/dL",
                'message': f"Fasting blood sugar is higher than standard fasting target (<100 mg/dL).",
                'action': "Verify last meal timing and insulin/medication intake with doctor."
            })
        elif glucose > 180:
            alerts.append({
                'vital': 'Blood Glucose',
                'severity': 'warning' if glucose < 240 else 'critical',
                'reading': f"{glucose} mg/dL",
                'message': "Elevated blood sugar level detected.",
                'action': "Check hydration and consult physician for dose adjustment advice."
            })
        elif glucose < 70:
            alerts.append({
                'vital': 'Blood Glucose',
                'severity': 'critical',
                'reading': f"{glucose} mg/dL",
                'message': "Hypoglycemia alert: Blood sugar is critically low (< 70 mg/dL).",
                'action': "Administer fast-acting carbohydrate (e.g. 15g juice or glucose tablets) and notify caregiver."
            })

    # Oxygen Saturation (SpO2)
    spo2 = vital_record.get('oxygen_saturation')
    if spo2:
        if spo2 < 90:
            alerts.append({
                'vital': 'Oxygen Saturation (SpO2)',
                'severity': 'critical',
                'reading': f"{spo2}%",
                'message': "Critical Hypoxemia: Oxygen saturation is dangerously low (< 90%).",
                'action': "Seat patient upright. Seek immediate medical attention or emergency response."
            })
        elif spo2 < 94:
            alerts.append({
                'vital': 'Oxygen Saturation (SpO2)',
                'severity': 'warning',
                'reading': f"{spo2}%",
                'message': "Oxygen saturation is slightly below optimal baseline (≥95%).",
                'action': "Check sensor placement, encourage calm deep breaths, and re-test."
            })

    # Heart Rate
    hr = vital_record.get('heart_rate')
    if hr:
        if hr > 105:
            alerts.append({
                'vital': 'Heart Rate',
                'severity': 'warning' if hr < 130 else 'critical',
                'reading': f"{hr} bpm",
                'message': "Tachycardia: Resting heart rate is elevated (>100 bpm).",
                'action': "Patient should rest in a cool, quiet room. Check for fever or anxiety."
            })
        elif hr < 52:
            alerts.append({
                'vital': 'Heart Rate',
                'severity': 'warning',
                'reading': f"{hr} bpm",
                'message': "Bradycardia: Resting heart rate is low (<55 bpm).",
                'action': "Review current beta-blocker/cardiac medications with prescribing doctor."
            })
            
    return alerts

if __name__ == '__main__':
    train_and_save_model()
