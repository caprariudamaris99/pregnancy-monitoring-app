from app import db
from datetime import datetime

class VitalSign(db.Model):
    """Model pentru parametri vitali (greutate, TA, glicemie)."""
    __tablename__ = 'vital_signs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Greutate
    weight_kg = db.Column(db.Float, nullable=True)
    
    # Tensiune arterială
    systolic_bp = db.Column(db.Integer, nullable=True)  # Sistolă (ex: 120)
    diastolic_bp = db.Column(db.Integer, nullable=True)  # Diastolă (ex: 80)
    
    # Glicemie
    blood_glucose_mg_dl = db.Column(db.Float, nullable=True)  # mg/dL
    
    # Metadate
    measurement_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relații
    patient = db.relationship('Patient', backref=db.backref('vital_signs'))
    
    def __repr__(self):
        return f'<VitalSign {self.patient_id} {self.measurement_date}>'

class Symptom(db.Model):
    """Model pentru simptome."""
    __tablename__ = 'symptoms'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Tip simptom
    symptom_type = db.Column(db.String(100), nullable=False)  # greață, edeme, dureri, insomnie, etc.
    intensity = db.Column(db.Integer)  # 1-10 scală
    observations = db.Column(db.Text)
    
    # Metadate
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relații
    patient = db.relationship('Patient', backref=db.backref('symptoms'))
    
    def __repr__(self):
        return f'<Symptom {self.symptom_type}>'
