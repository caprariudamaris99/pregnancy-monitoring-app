from app import db
from datetime import datetime

class Medication(db.Model):
    """Model pentru medicație."""
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Detalii medicament
    name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100))  # Ex: 500mg
    frequency = db.Column(db.String(100))  # Ex: 2x pe zi
    duration = db.Column(db.String(100))  # Ex: 7 zile
    instructions = db.Column(db.Text)
    warnings = db.Column(db.Text)  # Atencionări
    
    # Clasificare
    medication_type = db.Column(db.String(50))  # prescribed / supplement / otc
    prescribed_by_doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    
    # Start & end
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relații
    patient = db.relationship('Patient', backref=db.backref('medications'))
    doctor = db.relationship('Doctor', backref=db.backref('prescribed_medications'))
    
    # Aderență (reminders)
    reminders = db.relationship('MedicationReminder', backref=db.backref('medication'), cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medication {self.name}>'

class MedicationReminder(db.Model):
    """Model pentru remindere de medicație."""
    __tablename__ = 'medication_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    
    # Detalii reminder
    reminder_time = db.Column(db.Time, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    is_taken = db.Column(db.Boolean, default=False)
    taken_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)  # Observații după administrare
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
