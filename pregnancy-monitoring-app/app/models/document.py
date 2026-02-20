from app import db
from datetime import datetime

class Document(db.Model):
    """Model pentru documente medicale."""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Partidă - cine a încărcat documentul
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Detalii document
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, jpg, png, etc.
    file_size = db.Column(db.Integer)  # în bytes
    
    # Metadate medicale
    document_type = db.Column(db.String(100))  # analiza, ecografie, rețetă, etc.
    lab_name = db.Column(db.String(150), nullable=True)  # Laborator/Clinică
    document_date = db.Column(db.Date, nullable=True)
    
    # Asocieri
    associated_appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    # Metadate
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relații
    uploaded_by = db.relationship('User', backref=db.backref('uploaded_documents'))
    patient = db.relationship('Patient', backref=db.backref('documents'))
    associated_appointment = db.relationship('Appointment', backref=db.backref('documents'))
    
    def __repr__(self):
        return f'<Document {self.file_name}>'

class MedicalRecommendation(db.Model):
    """Model pentru recomandări medicale."""
    __tablename__ = 'medical_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Conținut
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(20), default='patient')  # patient / internal
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relații
    doctor = db.relationship('Doctor', backref=db.backref('recommendations'))
    patient = db.relationship('Patient', backref=db.backref('recommendations'))
    
    def __repr__(self):
        return f'<Recommendation {self.title}>'
