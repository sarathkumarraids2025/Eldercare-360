# ElderCare 360 - Intelligent Elderly Care & Medication Management Platform

> **A production-ready, accessible, intelligent healthcare ecosystem empowering senior citizens, families, caregivers, and physicians with real-time vitals telemetry, smart scheduled dose alarms, and AI-driven adherence risk prevention.**

---

## 🌟 Key Platform Highlights & Compliance

### 1. Mandatory Background Image Requirement

- **Real, Colorful Healthcare Background Image:** The Home Page hero section prominently features a high-resolution healthcare photograph (`static/images/hero-healthcare.jpg`, 285 KB) showcasing elderly healthcare and compassionate senior living.
- **Text Legibility:** Overlaid with a modern linear and radial gradient (`rgba(15, 23, 42, 0.80)` to `rgba(13, 148, 136, 0.72)`) guaranteeing crisp typography and accessibility.
- **Offline Stability:** Downloaded and stored locally in `static/images/` with fallback SVG styling so it never fails to load.

### 2. Mandatory Left-Sidebar Navigation (Left-Side Only)

All main navigation is strictly positioned on the **Left Side**:

1. 🏠 **Home** (`/`)
2. 📊 **Dashboard** (`/dashboard`)
3. 💊 **Medication Management** (`/medications`)
4. ⏰ **Medication Reminders** (`/reminders`)
5. 📋 **Health Records** (`/health-records`)
6. 📅 **Doctor Appointments** (`/appointments`)
7. 🩺 **Health Monitoring** (`/health-monitoring`)
8. 🤝 **Caregiver Management** (`/caregivers`)
9. 👨‍👩‍👧 **Family Dashboard** (`/family-dashboard`)
10. 📈 **Reports & Analytics** (`/reports`)
11. 🚨 **Emergency Assistance** (`/emergency`)
12. ⚙️ **Settings** (`/settings`)
13. ℹ️ **About** (`/about`)

The left sidebar is collapsible, highlights active pages, supports responsive off-canvas mobile drawers, and never overlaps main content. The top navigation is minimal, reserved for profile controls, font sizers, language switcher, and the Emergency SOS trigger.

---

## 🎨 Color Palette & Visual Design

Crafted using modern healthcare color psychology:

- **Teal Primary:** `#0d9488` / `#14b8a6`
- **Sky Blue:** `#0284c7` / `#38bdf8`
- **Mint Green:** `#10b981` / `#34d399`
- **Soft Purple:** `#8b5cf6` / `#a78bfa`
- **Coral Accent / SOS:** `#f43f5e` / `#fb7185`
- **Glassmorphism & Soft Gradients:** `linear-gradient(135deg, #f0fdfa 0%, #f0f9ff 50%, #faf5ff 100%)`

---

## 🤖 Genuine AI / ML Component: Medication Adherence & Risk Engine

- **Trained Model:** Scikit-learn `RandomForestClassifier` trained on geriatric clinical adherence parameters (MMAS-8 & WHO adherence benchmarks).
- **Saved Model File:** `models_saved/adherence_model.joblib`.

### Clinical Input Features (9):

1. Patient Age
2. Polypharmacy (Number of active medications)
3. Daily dosing frequency count
4. Past 7-day historical adherence rate
5. Consecutive missed doses streak
6. Chronic conditions count (e.g., Hypertension, Diabetes, Osteoarthritis)
7. Mobility / Cognitive assistance tier (0 to 3)
8. Systolic Blood Pressure variability (standard deviation)
9. Blood Glucose variability (standard deviation)

### Real-Time Inference Output:

- Risk Categorization: `Low Risk`, `Moderate Risk`, `High Risk`
- Statistical Adherence Probability %
- Identified Behavioral Contributing Drivers (e.g., Polypharmacy > 5 meds, frequent missed night doses)
- Actionable clinical recommendations for caregivers and doctors
- Explicit notification when insufficient data exists (< 3 doses or vitals).

---

## 📊 8 Interactive Chart.js Visualizations (Real Database Telemetry)

1. **Medication Adherence Trend** – Line chart showing weekly compliance %
2. **Daily Medication Status** – Doughnut chart (Taken, Pending, Missed)
3. **Weekly Medication Completion** – Stacked Bar chart of daily dose volume
4. **Blood Pressure History** – Dual Line chart (Systolic & Diastolic mmHg)
5. **Blood Glucose History** – Line chart (Fasting vs. Post-meal mg/dL)
6. **Heart Rate History** – Line chart (Resting bpm)
7. **Appointment Summary** – Bar chart by medical specialization
8. **Oxygen Saturation (SpO2) Trajectory** – Line chart tracking pulse oximetry %

---

## 🌐 Accessibility & Bilingual Language Support

- **Bilingual English & Tamil (தமிழ்):** Instant header toggle between English and Tamil translating all navigation labels, medical terms, form controls, and emergency alerts.
- **Elderly Text Size Scaling:** Dynamic font sizing (`A` Normal, `A+` Large, `A++` Extra Large).
- **High Contrast Mode:** High-contrast toggle for seniors with cataract or visual impairments.
- **Web Audio API Synthesizer:** Built-in chime for dosing alarms and siren for Emergency SOS alerts (no external audio files required).

---

## 🚀 Quick Demo Accounts (1-Click Login)

Pre-seeded with complete clinical telemetry, 5 active medications, 14-day vitals logs, and appointments:

| Role | Username | Password | Purpose |
|---|---|---|---|
| **Senior Patient** | `ramalingam` | `senior123` | Mr. S. Ramalingam (Age 74, Hypertension, Diabetes) |
| **Caregiver** | `nurse_anitha` | `caregiver123` | Nurse Anitha R. (Registered Geriatric Nurse) |
| **Family Member** | `vijay_son` | `family123` | Vijay Ramalingam (Son & Primary Guardian) |
| **Doctor** | `dr_subramanian` | `doctor123` | Dr. K. Subramanian, MD (Attending Geriatrician) |
| **Administrator** | `admin` | `admin123` | System Administrator |

---

## 🛠️ Installation & Local Running Instructions

### 1. Requirements

- Python 3.10+
- SQLite (Zero setup, embedded)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application

```bash
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Automated Testing

Run the complete automated test suite verifying all 13 sidebar pages, authentication, CRUD, and AI model inference:

```bash
python test_suite.py
```

**Test Result:**

```text
Ran 9 tests in 6.908s
OK
```

---

## ⚕️ Important Note

ElderCare 360 is intended for elderly-care management and demonstration purposes. AI-generated adherence risk insights are supportive estimates and should not replace professional medical advice or clinical decisions. Demo credentials should be changed before public deployment, and real patient data must be protected appropriately.

---

**ElderCare 360 – Intelligent Healthcare. Compassionate Elderly Care.**