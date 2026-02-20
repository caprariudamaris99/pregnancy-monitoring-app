from app import db
from datetime import datetime


class DoctorPatientLink(db.Model):
    """Many-to-many link between doctors and patients with consent metadata."""
    __tablename__ = 'doctor_patient_links'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    consent = db.Column(db.Boolean, default=False)
    consent_date = db.Column(db.DateTime)
    role = db.Column(db.String(50), default='primary')  # primary/secondary/consulting

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    doctor = db.relationship('Doctor', backref=db.backref('patient_links', cascade='all, delete-orphan'))
    patient = db.relationship('Patient', backref=db.backref('doctor_links', cascade='all, delete-orphan'))
    created_by = db.relationship('User')

    def __repr__(self):
        return f'<DoctorPatientLink {self.doctor_id}->{self.patient_id} consent={self.consent}>'
