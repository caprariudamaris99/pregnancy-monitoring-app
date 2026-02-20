"""
Models pentru gestionarea sarcinilor - informații săptămânale și calendar de sarcină.
"""
from app import db
from datetime import datetime, date, timedelta
from enum import Enum

class PregnancyWeekInfo(db.Model):
    """Model pentru informații detaliate despre fiecare săptămână de sarcină."""
    __tablename__ = 'pregnancy_week_info'
    
    id = db.Column(db.Integer, primary_key=True)
    week_number = db.Column(db.Integer, unique=True, nullable=False)  # 1-40
    
    # Informații despre mamă
    mom_info = db.Column(db.Text, nullable=False)  # Ce se întâmplă cu mama în această săptămână
    mom_symptoms = db.Column(db.Text)  # Simptome normale așteptate
    
    # Informații despre făt
    baby_info = db.Column(db.Text, nullable=False)  # Dezvoltarea fătului
    baby_size_description = db.Column(db.String(100))  # Ex: "mărimea unui piersic", "mărimea unei banane"
    baby_weight_grams = db.Column(db.Integer)  # Greutate estimată în grame
    baby_length_cm = db.Column(db.Float)  # Lungime estimată în cm
    
    # Investigații și teste recomandate
    recommended_tests = db.Column(db.Text)  # Analize/teste recomandate în această săptămână
    
    # Semnale de alarmă
    warning_signs = db.Column(db.Text)  # Simptome care necesită atenție medicală imediată
    
    # Sfaturi și recomandări
    nutrition_tips = db.Column(db.Text)  # Recomandări nutriționale
    exercise_tips = db.Column(db.Text)  # Sfaturi privind mișcarea
    lifestyle_tips = db.Column(db.Text)  # Alte sfaturi de stil de viață
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PregnancyWeekInfo Week {self.week_number}>'


class PregnancyCalendarTask(db.Model):
    """Model pentru task-uri de sarcină (analize, vizite, măsurări) auto-generate."""
    __tablename__ = 'pregnancy_calendar_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Detalii task
    title = db.Column(db.String(200), nullable=False)  # Ex: "Ecografie 20 săpt", "Analiza glicemie"
    description = db.Column(db.Text)  # Descriere detaliată
    
    # Tip de task
    task_type = db.Column(db.String(50), nullable=False)  # 'analysis', 'appointment', 'measurement', 'document_upload', 'general_task'
    
    # Programare în săptămâna de sarcină
    week_number = db.Column(db.Integer)  # Săptămâna din sarcină când se recomandă
    due_date = db.Column(db.Date)  # Data datorată (calculată din LMP + săptămâna)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    completion_notes = db.Column(db.Text)  # Rezultate/observații la completare
    
    # Origen
    recommended_by_doctor = db.Column(db.Boolean, default=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    
    # Documentație asociată
    associated_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    associated_appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    # Priorități și notificări
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'
    send_reminder = db.Column(db.Boolean, default=True)
    reminder_days_before = db.Column(db.Integer, default=3)  # Trimitere reminder cu X zile înainte
    
    # Metadate
    auto_generated = db.Column(db.Boolean, default=True)  # Generat automat din template vs manual
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relații
    patient = db.relationship('Patient', backref=db.backref('calendar_tasks'))
    doctor = db.relationship('Doctor', backref=db.backref('recommended_tasks'))
    associated_document = db.relationship('Document', foreign_keys=[associated_document_id])
    associated_appointment = db.relationship('Appointment', foreign_keys=[associated_appointment_id])
    
    def __repr__(self):
        return f'<PregnancyCalendarTask {self.title}>'
    
    def is_overdue(self):
        """Verifică dacă task-ul este expirat."""
        if self.is_completed or not self.due_date:
            return False
        return date.today() > self.due_date
    
    def days_until_due(self):
        """Calculează zilele rămase până la data datorată."""
        if not self.due_date:
            return None
        delta = self.due_date - date.today()
        return delta.days
    
    @staticmethod
    def get_tasks_by_pregnancy_week(patient_id, week_number):
        """Returnează task-urile pentru o anumită săptămână de sarcină."""
        return PregnancyCalendarTask.query.filter_by(
            patient_id=patient_id,
            week_number=week_number
        ).all()
    
    @staticmethod
    def get_pending_tasks(patient_id):
        """Returnează task-urile nesfinalizate pentru pacient."""
        return PregnancyCalendarTask.query.filter_by(
            patient_id=patient_id,
            is_completed=False
        ).order_by(PregnancyCalendarTask.due_date).all()
    
    @staticmethod
    def get_overdue_tasks(patient_id):
        """Returnează task-urile expirate."""
        pending_tasks = PregnancyCalendarTask.get_pending_tasks(patient_id)
        return [task for task in pending_tasks if task.is_overdue()]


class DoctorUnavailability(db.Model):
    """Model pentru perioadele când medicul nu e disponibil."""
    __tablename__ = 'doctor_unavailability'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Perioadă indisponibilitate
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Motivul
    reason = db.Column(db.String(200), nullable=False)  # 'vacation', 'conference', 'emergency', 'other'
    description = db.Column(db.Text)  # Descriere detaliată (opțional)
    
    # Status
    is_recurring = db.Column(db.Boolean, default=False)  # Ex: vacanța anuală
    recurring_pattern = db.Column(db.String(50))  # 'yearly', 'monthly' (dacă recurring)
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relații
    doctor = db.relationship('Doctor', backref=db.backref('unavailabilities'))
    created_by = db.relationship('User')
    
    def __repr__(self):
        return f'<DoctorUnavailability {self.doctor_id} {self.reason}>'
    
    def overlaps_with(self, start_date, end_date):
        """Verifică dacă perioada dată se suprapune cu indisponibilitatea."""
        return not (end_date < self.start_date or start_date > self.end_date)
    
    @staticmethod
    def is_doctor_available(doctor_id, check_date):
        """Verifică dacă medicul este disponibil la data dată."""
        unavailable = DoctorUnavailability.query.filter(
            DoctorUnavailability.doctor_id == doctor_id,
            DoctorUnavailability.start_date <= check_date,
            DoctorUnavailability.end_date >= check_date
        ).first()
        return unavailable is None
    
    @staticmethod
    def get_doctor_unavailabilities(doctor_id, start_date, end_date):
        """Returnează indisponibilități doctor-ului într-o perioadă."""
        return DoctorUnavailability.query.filter(
            DoctorUnavailability.doctor_id == doctor_id,
            DoctorUnavailability.start_date <= end_date,
            DoctorUnavailability.end_date >= start_date
        ).all()


class Prescription(db.Model):
    """Model pentru rețete standardizate (medical prescriptions)."""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    
    # Detalii rețetă
    prescription_number = db.Column(db.String(50), unique=True)
    prescription_date = db.Column(db.Date, default=date.today)
    valid_until = db.Column(db.Date)  # Valabilitate rețetă
    
    # Medicament - detalii
    quantity = db.Column(db.Integer)  # Nr. cutii/fiole
    dispensing_instructions = db.Column(db.Text)  # Instrucțiuni pt. farmacie
    
    # Status
    is_dispensed = db.Column(db.Boolean, default=False)  # Eliberat din farmacie?
    dispensed_date = db.Column(db.DateTime, nullable=True)
    dispensed_at_pharmacy = db.Column(db.String(200))  # Farmacia unde a fost eliberat
    
    # Notițe
    notes = db.Column(db.Text)
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relații
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions'))
    patient = db.relationship('Patient', backref=db.backref('prescriptions'))
    medication = db.relationship('Medication')
    
    def __repr__(self):
        return f'<Prescription {self.prescription_number}>'
    
    @property
    def is_valid(self):
        """Verifică dacă rețeta este încă valabilă."""
        if self.valid_until and date.today() > self.valid_until:
            return False
        return True
    
    @property
    def is_expired(self):
        """Verifică dacă rețeta a expirat."""
        return not self.is_valid
    
    @staticmethod
    def generate_prescription_number(doctor_id):
        """Generează un nr. unic de rețetă."""
        import time
        return f"RX{doctor_id}{int(time.time())}"


from sqlalchemy import event


@event.listens_for(Prescription, 'before_insert')
def set_prescription_number(mapper, connection, target):
    if not target.prescription_number:
        # Try to set a generated prescription number; collisions should be rare.
        target.prescription_number = Prescription.generate_prescription_number(target.doctor_id)
