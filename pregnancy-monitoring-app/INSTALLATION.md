# Aplicație de Monitorizare a Sarcinilor - Documentație Completă

## 📋 Descriere Generală

Aceasta este o aplicație web profesională pentru monitorizarea medicală a sarcinilor, dezvoltată pe baza stack-ului Python/Flask. Aplicația conectează paciente gravide cu medici obstetrici și ginecologi pentru o monitorizare eficientă și sigură a sarcinii.

## 🎯 Funcționalități Principale

### 1. Rol Pacientă
- ✅ Autentificare și gestionare profil
- ✅ Înregistrare date medicale și antecedente
- ✅ Monitorizare parametri vitali (greutate, tensiune, glicemie)
- ✅ Raportare simptome pe o scală 1-10
- ✅ Calendar de sarcină cu informații pe săptămâni
- ✅ Gestionare medicație (prescrisă, suplimente, OTC)
- ✅ Încărcare documente medicale
- ✅ Programări consultații cu medicul
- ✅ Mesagerie directă cu medicul
- ✅ Export date (CSV, PDF)
- ✅ Notificări pentru medicație și programări

### 2. Rol Medic
- ✅ Autentificare și profil profesional
- ✅ Gestionare paciente asociate
- ✅ Dosar complet al fiecărei paciente
- ✅ Gestionare disponibilitate (sloturi 30 min)
- ✅ Confirmarea/respingerea programărilor
- ✅ Adăugare recomandări medicale
- ✅ Gestionare medicație (prescripție)
- ✅ Mesagerie cu pacienții

### 3. Securitate și GDPR
- ✅ Hashing parole (Werkzeug)
- ✅ Roluri și permisiuni (Patient/Doctor)
- ✅ Consimțământ explicit pentru partajare date
- ✅ Criptare sesiuni
- ✅ Politici de retenție date

## 🛠️ Stack Tehnologic

### Backend
- **Framework:** Flask 2.3.2
- **ORM:** SQLAlchemy 2.0.19
- **Bază de date:** PostgreSQL
- **Autentificare:** Flask-Login, Werkzeug
- **Formulare:** Flask-WTF
- **Migrări:** Flask-Migrate (Alembic)

### Frontend
- **HTML5, CSS3** cu Bootstrap 5
- **JavaScript** pentru interactivitate
- **Chart.js** pentru grafice
- **Jinja2** templating engine

### Suport Suplimentar
- **ICS Export** pentru integrare calendar
- **File Upload** (PDF, JPG, PNG, DOC, DOCX)

## 📦 Instalare și Configurare

### 1. Precondiții
- Python 3.8+
- PostgreSQL instalat și rulând
- pip (Python Package Manager)

**Recomandare Python:** Pentru stabilitate și compatibilitate cu dependințele (în special SQLAlchemy/Flask-SQLAlchemy), folosiți Python 3.11 sau 3.12. Python 3.13 poate avea incompatibilități cu anumite versiuni de SQLAlchemy.

### 2. Instalare

```bash
# Clone the repository
cd pregnancy-monitoring-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Configurare Bază de Date

```bash
# Create database
createdb pregnancy_monitoring

# Run migrations
flask db upgrade

# Create admin user (opțional)
flask shell
>>> from app.models.user import User
>>> admin = User(email='admin@example.com', first_name='Admin', last_name='User', role='admin')
>>> admin.set_password('admin_password')
>>> db.session.add(admin)
>>> db.session.commit()
```

### 4. Porniți aplicația

```bash
# Development mode
python run.py

# Or using Flask CLI
flask run

# Production (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Accesați: http://localhost:5000

## 📂 Structura Directoarelor

```
pregnancy-monitoring-app/
├── app/
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   ├── appointment.py
│   │   ├── medication.py
│   │   ├── symptom.py
│   │   ├── document.py
│   │   └── message.py
│   ├── routes/                 # Flask blueprints
│   │   ├── auth.py
│   │   ├── patient_routes.py
│   │   ├── doctor_routes.py
│   │   └── common.py
│   ├── forms/                  # WTForms
│   │   ├── auth_forms.py
│   │   ├── patient_forms.py
│   │   └── medical_forms.py
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── patient/
│   │   └── doctor/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── uploads/                # Upload folder
│   └── __init__.py
├── migrations/                 # Alembic migrations
├── config.py                   # Configuration
├── run.py                      # Entry point
├── requirements.txt            # Dependencies
├── .env.example                # Environment template
└── README.md
```

## 🔐 Autentificare

### Fluxul de autentificare
1. Utilizatorul se înregistrează ca pacientă sau medic
2. Profil creat automat (Patient sau Doctor)
3. Flask-Login gestionează sesiunile
4. Parola criptată cu Werkzeug

### Roluri
- **Patient:** Acces la datele proprii, programări, medicație
- **Doctor:** Acces la pacienții asociați
- **Admin:** Acces complet (opțional)

## 📊 Schema Bază de Date

### Utilizatori (Users)
```
id, email (UNIQUE), first_name, last_name, phone, password_hash, role, 
created_at, updated_at, last_login, is_active, data_consent
```

### Paciente (Patients)
```
id, user_id (FK), lmp_date, pregnancy_type, due_date, blood_type, 
rh_factor, allergies, chronic_conditions, permanent_medication, 
surgical_history, associated_doctor_id (FK)
```

### Medici (Doctors)
```
id, user_id (FK), specialization, clinic_name, clinic_address, 
license_number, degree, work_start_hour, work_end_hour, 
slot_duration_minutes, working_days
```

### Programări (Appointments)
```
id, patient_id (FK), doctor_id (FK), appointment_date, 
duration_minutes, status, notes, doctor_recommendations, 
doctor_internal_notes
```

### Medicație (Medications)
```
id, patient_id (FK), name, dosage, frequency, duration, 
instructions, warnings, medication_type, prescribed_by_doctor_id (FK), 
start_date, end_date, is_active
```

### Parametri Vitali (VitalSigns)
```
id, patient_id (FK), weight_kg, systolic_bp, diastolic_bp, 
blood_glucose_mg_dl, measurement_date, notes
```

### Simptome (Symptoms)
```
id, patient_id (FK), symptom_type, intensity (1-10), 
observations, reported_date
```

### Documente (Documents)
```
id, uploaded_by_user_id (FK), patient_id (FK), file_name, 
file_path, file_type, file_size, document_type, lab_name, 
document_date, associated_appointment_id (FK)
```

### Mesaje (Messages)
```
id, sender_id (FK), recipient_id (FK), subject, content, 
is_read, read_at, sent_at
```

## 🚀 Folosire

### Pentru Paciente
1. **Înregistrare:** Click "Înregistrare pacientă"
2. **Profil medical:** Completați DUM, grup sanguín, antecedente
3. **Monitorizare:** Adăugați măsurători și simptome
4. **Programări:** Cereri programare la medic
5. **Comunicare:** Mesaje directe cu medicul

### Pentru Medici
1. **Înregistrare:** Click "Înregistrare medic"
2. **Profil:** Completați date profesionale și program
3. **Paciente:** Acceptați cereri de asociere
4. **Monitoring:** Consultați dosarele pacienților
5. **Management:** Confirmați programări și adăugați recomandări

## 🔒 GDPR și Confidențialitate

### Drepturi utilizatori
- Acces la date personale
- Ștergere cont și anonimizare date
- Export date (CSV, PDF)
- Revocare consimțământ
- Drept la opoziție

### Retenție date
- Datele medicale: 10 ani după finalizarea sarcinii
- Datele de utilizator: 1 an după ștergere cont
- Mesajele: conform cu ștergerea contului

## 🐛 Troubleshooting

### Eroare de conexiune la baza de date
```python
# Verificați în .env
DATABASE_URL=postgresql://user:password@localhost:5432/pregnancy_monitoring

# Testați conexiunea
python
>>> from app import db
>>> db.create_all()
```

### Migrări nereușite
```bash
# Revertați la versiunea anterioară
flask db downgrade

# Și rulați din nou
flask db upgrade
```

### Upload-uri blocate
```python
# Verificați permisiuni folder
chmod 755 app/uploads/

# Și mărime maximă în config.py
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
```

## 📝 Notă Juridică

Aceasta este o aplicație medicală și trebuie să respecte:
- Legile de protecție a datelor (GDPR)
- Reglementări medicale locale
- Standarde de siguranță în sănătate
- Obligații de secret profesional medical

## 👥 Contribuitori

- Dezvoltator Principal: [Nume]
- Data ultimei actualizări: 11.02.2026

## 📞 Support

Pentru întrebări și suport:
- Email: support@monitorizaresarcina.ro
- Forum: https://forum.monitorizaresarcina.ro
- Documentație: https://docs.monitorizaresarcina.ro

## 📄 Licență

Licență privată - Nu este permisă distribuirea fără autorizație.

---

**© 2026 Aplicație de Monitorizare a Sarcinilor. Toate drepturile rezervate.**
