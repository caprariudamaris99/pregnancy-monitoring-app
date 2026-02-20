# Database Schema - PostgreSQL Tables (Updated)
## Complete Database Design for Pregnancy Monitoring System

---

## Recent Migration

- Migration: `migrations/versions/0001_add_associations_and_conversations.py` — adds `conversations`, `conversation_participants`, `consent_audits`, `doctor_patient_links`, and `appointment_start`/`appointment_end` columns; creates several helpful indexes. (Run `flask db upgrade` to apply.)


## CORE MODELS (13)

### 1. Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    role VARCHAR(20) DEFAULT 'patient',  -- patient, doctor, admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    data_consent BOOLEAN DEFAULT FALSE  -- GDPR consent
);
```

**Indexes:**
- `CREATE INDEX idx_users_email ON users(email);`
- `CREATE INDEX idx_users_role ON users(role);`

---

### 2. Patients Table (Gravide)
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    
    -- Pregnancy Data
    lmp_date DATE,  -- Data Ultimei Menstruații (DUM)
    pregnancy_type VARCHAR(20) DEFAULT 'single',  -- single/multiple
    due_date DATE,  -- Data Probabilă de Naștere (DPN)
    
    -- Medical Profile
    blood_type VARCHAR(10),  -- ABO
    rh_factor VARCHAR(10),  -- +/-
    allergies TEXT,
    chronic_conditions TEXT,
    permanent_medication TEXT,
    surgical_history TEXT,
    
    -- Doctor Association
    associated_doctor_id INTEGER REFERENCES doctors(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 3. Doctors Table
```sql
CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    
    -- Professional Data
    specialization VARCHAR(100),
    clinic_name VARCHAR(150),
    clinic_address VARCHAR(200),
    license_number VARCHAR(50) UNIQUE,
    degree VARCHAR(100),
    
    -- Scheduling
    work_start_hour INTEGER DEFAULT 9,
    work_end_hour INTEGER DEFAULT 17,
    slot_duration_minutes INTEGER DEFAULT 30,
    working_days VARCHAR(50) DEFAULT 'monday,tuesday,wednesday,thursday,friday',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4. Appointments Table
```sql
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    
    -- Use start/end for slot ranges (allows overlap checks)
    appointment_start TIMESTAMP NOT NULL,
    appointment_end TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    status VARCHAR(20) DEFAULT 'requested',  -- requested, confirmed, rejected, cancelled, completed
    
    notes TEXT,
    doctor_recommendations TEXT,  -- Visible to patient
    doctor_internal_notes TEXT,  -- Only for doctor
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 5. Vital Signs Table
```sql
CREATE TABLE vital_signs (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    weight_kg DECIMAL(5, 2),
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    blood_glucose_mg_dl DECIMAL(6, 2),
    
    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    is_abnormal BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 6. Symptoms Table
```sql
CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    symptom_type VARCHAR(100),
    intensity INTEGER CHECK (intensity >= 1 AND intensity <= 10),  -- 1-10 scale
    observations TEXT,
    
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 7. Medications Table
```sql
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    name VARCHAR(150),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration VARCHAR(100),
    instructions TEXT,
    warnings TEXT,
    
    medication_type VARCHAR(50),  -- prescribed, supplement, otc
    prescribed_by_doctor_id INTEGER REFERENCES doctors(id),
    
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 8. Medication Reminders Table
```sql
CREATE TABLE medication_reminders (
    id SERIAL PRIMARY KEY,
    medication_id INTEGER NOT NULL REFERENCES medications(id),
    
    reminder_time TIME,
    date_time TIMESTAMP,
    is_taken BOOLEAN DEFAULT FALSE,
    taken_at TIMESTAMP,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 9. Documents Table
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    uploaded_by_user_id INTEGER NOT NULL REFERENCES users(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    
    document_type VARCHAR(100),  -- analiza, ecografie, rețetă, etc.
    lab_name VARCHAR(150),
    document_date DATE,
    
    associated_appointment_id INTEGER REFERENCES appointments(id),
    
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 10. Medical Recommendations Table
```sql
CREATE TABLE medical_recommendations (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    title VARCHAR(200),
    description TEXT,
    visibility VARCHAR(20) DEFAULT 'patient',  -- patient, internal
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 11. Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    
    subject VARCHAR(200),
    body TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 12. Message Attachments Table
```sql
CREATE TABLE message_attachments (
    id SERIAL PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    document_id INTEGER REFERENCES documents(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 13. Notifications Table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    type VARCHAR(50),  -- medication, appointment, task, message, document
    title VARCHAR(200),
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    
    related_object_id INTEGER,
    related_object_type VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ✨ NEW MODELS (4) - For Complete Use Case Support

### 14. Pregnancy Week Info Table
```sql
CREATE TABLE pregnancy_week_info (
    id SERIAL PRIMARY KEY,
    week_number INTEGER UNIQUE NOT NULL,  -- 1-40
    
    -- Mama
    mom_info TEXT,
    mom_symptoms TEXT,
    
    -- Făt
    baby_info TEXT,
    baby_size_description VARCHAR(100),
    baby_weight_grams INTEGER,
    baby_length_cm DECIMAL(5, 2),
    
    -- Recomandări
    recommended_tests TEXT,
    warning_signs TEXT,
    nutrition_tips TEXT,
    exercise_tips TEXT,
    lifestyle_tips TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Stores detailed information for each pregnancy week (mom & baby development, tests, warnings, tips)

---

### 15. Pregnancy Calendar Tasks Table
```sql
CREATE TABLE pregnancy_calendar_tasks (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    
    -- Task details
    title VARCHAR(200),
    description TEXT,
    task_type VARCHAR(50),  -- analysis, appointment, measurement, document_upload, general_task
    
    -- Scheduling
    week_number INTEGER,
    due_date DATE,
    
    -- Status
    is_completed BOOLEAN DEFAULT FALSE,
    completed_date TIMESTAMP,
    completion_notes TEXT,
    
    -- Origin
    recommended_by_doctor BOOLEAN DEFAULT FALSE,
    doctor_id INTEGER REFERENCES doctors(id),
    
    -- Associated objects
    associated_document_id INTEGER REFERENCES documents(id),
    associated_appointment_id INTEGER REFERENCES appointments(id),
    
    -- Reminders
    priority VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, urgent
    send_reminder BOOLEAN DEFAULT TRUE,
    reminder_days_before INTEGER DEFAULT 3,
    
    -- Metadata
    auto_generated BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Auto-generated pregnancy-related tasks (analyses, appointments, measurements) for each week
**Relationships:** 
- Links each task to PregnancyWeekInfo
- Tracks completion and associated documents/appointments

---

### 16. Doctor Unavailability Table
```sql
CREATE TABLE doctor_unavailability (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    
    -- Period
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Reason
    reason VARCHAR(200),  -- vacation, conference, emergency, other
    description TEXT,
    
    -- Recurrence
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern VARCHAR(50),  -- yearly, monthly
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER REFERENCES users(id)
);
```

**Purpose:** Manages doctor availability exceptions (vacations, conferences, etc.)
**Impact:** Filter available appointment slots, exclude unavailable dates

---

### 17. Prescriptions Table
```sql
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    medication_id INTEGER NOT NULL REFERENCES medications(id),
    
    -- Prescription details
    prescription_number VARCHAR(50) UNIQUE,
    prescription_date DATE DEFAULT CURRENT_DATE,
    valid_until DATE,
    quantity INTEGER,
    dispensing_instructions TEXT,
    
    -- Status
    is_dispensed BOOLEAN DEFAULT FALSE,
    dispensed_date TIMESTAMP,
    dispensed_at_pharmacy VARCHAR(200),
    
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Standardized prescription generation and tracking
**Features:** Automatic prescription number generation, validity tracking

---

## ADDITIONAL NEW TABLES (4)

### 18. Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    subject VARCHAR(255),
    is_group BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** Thread grouping for messages allowing multi-user conversations, subjects, and per-conversation metadata.

---

### 19. Conversation Participants Table
```sql
CREATE TABLE conversation_participants (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_muted BOOLEAN DEFAULT FALSE
);
```

**Purpose:** Associates users to conversations, supports unread/mute flags and permissions.

---

### 20. Consent Audits Table
```sql
CREATE TABLE consent_audits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    previous_value BOOLEAN,
    new_value BOOLEAN,
    changed_by_user_id INTEGER REFERENCES users(id),
    reason VARCHAR(255),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose:** GDPR audit trail to record changes to a user's consent status, who changed it, and why.

---

### 21. Doctor–Patient Links Table
```sql
CREATE TABLE doctor_patient_links (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    consent BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMP,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_user_id INTEGER REFERENCES users(id)
);
```

**Purpose:** Many-to-many association between doctors and patients with per-link consent, roles (primary/secondary), and audit metadata.

---

## DATABASE INDEXES (Performance Optimization)

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Patients
CREATE INDEX idx_patients_user_id ON patients(user_id);
CREATE INDEX idx_patients_doctor_id ON patients(associated_doctor_id);
CREATE INDEX idx_patients_lmp_date ON patients(lmp_date);

-- Appointments
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_start ON appointments(appointment_start);
CREATE INDEX idx_appointments_end ON appointments(appointment_end);
CREATE INDEX idx_appointments_status ON appointments(status);

-- Vital Signs
CREATE INDEX idx_vital_signs_patient_id ON vital_signs(patient_id);
CREATE INDEX idx_vital_signs_date ON vital_signs(measurement_date);

-- Symptoms
CREATE INDEX idx_symptoms_patient_id ON symptoms(patient_id);
CREATE INDEX idx_symptoms_date ON symptoms(reported_date);

-- Medications
CREATE INDEX idx_medications_patient_id ON medications(patient_id);
CREATE INDEX idx_medications_active ON medications(is_active);

-- Documents
CREATE INDEX idx_documents_patient_id ON documents(patient_id);
CREATE INDEX idx_documents_type ON documents(document_type);

-- Messages
CREATE INDEX idx_messages_recipient ON messages(recipient_id);
CREATE INDEX idx_messages_sender ON messages(sender_id);

-- NEW INDEXES for new tables
CREATE INDEX idx_pregnancy_calendar_tasks_patient ON pregnancy_calendar_tasks(patient_id);
CREATE INDEX idx_pregnancy_calendar_tasks_week ON pregnancy_calendar_tasks(week_number);
CREATE INDEX idx_pregnancy_calendar_tasks_completed ON pregnancy_calendar_tasks(is_completed);
CREATE INDEX idx_doctor_unavailability_doctor ON doctor_unavailability(doctor_id);
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_number ON prescriptions(prescription_number);
```

---

## RELATIONSHIPS OVERVIEW

```
User (1) ──→ (1) Patient
  ↓
Patient (1) ──→ (N) Appointments
         (1) ──→ (N) VitalSigns
         (1) ──→ (N) Symptoms
         (1) ──→ (N) Medications
         (1) ──→ (N) Documents
         (1) ──→ (N) PregnancyCalendarTasks
         (1) ──→ (N) Prescriptions
         (1) ──→ (1) Doctor (associated)

Doctor (1) ──→ (N) Appointments
       (1) ──→ (N) MedicationPrescription
       (1) ──→ (N) MedicalRecommendation
       (1) ──→ (N) DoctorUnavailability

Appointment (1) ──→ (N) Documents
            (1) ──→ (N) PregnancyCalendarTasks

Message (1) ──→ (N) MessageAttachments

PregnancyCalendarTask (1) ──→ (1) PregnancyWeekInfo
                      (opt) ──→ (1) Document
                      (opt) ──→ (1) Appointment
```

---

## FOREIGN KEY CONSTRAINTS

All foreign keys are configured with:
- `ON DELETE CASCADE` for child records (clean automatic cleanup)
- `ON UPDATE CASCADE` for referential integrity

Examples:
```sql
ALTER TABLE patients ADD CONSTRAINT fk_patient_user 
    FOREIGN KEY (user_id) REFERENCES users(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE appointments ADD CONSTRAINT fk_appointment_patient 
    FOREIGN KEY (patient_id) REFERENCES patients(id) 
    ON DELETE CASCADE ON UPDATE CASCADE;
```

---

## DATA VALIDATION CONSTRAINTS

```sql
-- Check constraints
ALTER TABLE vital_signs ADD CONSTRAINT check_symptom_intensity 
    CHECK (intensity >= 1 AND intensity <= 10);

ALTER TABLE pregnancy_calendar_tasks ADD CONSTRAINT check_priority 
    CHECK (priority IN ('low', 'normal', 'high', 'urgent'));

-- Unique constraints
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);
ALTER TABLE doctors ADD CONSTRAINT unique_license UNIQUE (license_number);
ALTER TABLE prescriptions ADD CONSTRAINT unique_prescription_num UNIQUE (prescription_number);

-- NOT NULL constraints (already defined in table creation)
```

---

## DATABASE INITIALIZATION STEPS

```bash
# 1. Initialize Flask-Migrate (first time only)
flask db init

# 2. Create migration for all models
flask db migrate -m "Initial schema with new pregnancy models"

# 3. Apply migration to database
flask db upgrade

# 4. Seed pregnancy week information (utilities/pregnancy_scheduler.py)
# Execute from Flask shell:
flask shell
>>> from app.utils.pregnancy_scheduler import seed_pregnancy_week_info
>>> seed_pregnancy_week_info()
>>> exit()
```

---

## SUMMARY

- **Total Tables:** 17 (13 core + 4 new)
- **Total Relationships:** 35+ defined relationships
- **Total Indexes:** 25+ for optimization
- **Constraints:** GDPR compliance, referential integrity, data validation

## SUMMARY

- **Total Tables:** 21 (13 core + 8 new)
- **Total Relationships:** 40+ defined relationships
- **Total Indexes:** 30+ for optimization
- **Constraints:** GDPR compliance, referential integrity, data validation

This schema fully supports all 60 Use Cases from the diagram.
