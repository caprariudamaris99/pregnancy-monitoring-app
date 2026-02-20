from app import db
from datetime import datetime, timedelta

class Patient(db.Model):
    """Model pentru paciente (gravide)."""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Date sarcină
    lmp_date = db.Column(db.Date, nullable=True)  # DUM - Data Ultimei Menstruații
    pregnancy_type = db.Column(db.String(20), default='single')  # single/multiple
    due_date = db.Column(db.Date, nullable=True)  # DPN - Data Probabilă de Naștere
    
    # Profil medical
    blood_type = db.Column(db.String(10))  # ABO
    rh_factor = db.Column(db.String(10))  # + / -
    allergies = db.Column(db.Text)  # Alergii
    chronic_conditions = db.Column(db.Text)  # Afecțiuni cronice
    permanent_medication = db.Column(db.Text)  # Medicație permanentă
    surgical_history = db.Column(db.Text)  # Istoricul intervenţiilor chirurgicale
    
    # Relații
    user = db.relationship('User', backref=db.backref('patient_profile', uselist=False))
    associated_doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    associated_doctor = db.relationship('Doctor', backref=db.backref('patients'))
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_pregnancy_week(self):
        """Calculează săptămâna de sarcină curentă."""
        if not self.lmp_date:
            return None
        days_since_lmp = (datetime.utcnow().date() - self.lmp_date).days
        weeks = days_since_lmp // 7
        days = days_since_lmp % 7
        return (weeks, days)
    
    def update_due_date(self):
        """Actualizează DPN pe baza DUM."""
        if self.lmp_date:
            self.due_date = self.lmp_date + timedelta(days=280)  # ~40 săptămâni
    
    def __repr__(self):
        return f'<Patient {self.user.email}>'
