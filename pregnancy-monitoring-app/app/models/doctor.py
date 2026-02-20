from app import db
from datetime import datetime

class Doctor(db.Model):
    """Model pentru medici."""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Date profesionale
    specialization = db.Column(db.String(100), nullable=False)  # Ex: Ginecologie
    clinic_name = db.Column(db.String(150))
    clinic_address = db.Column(db.String(200))
    license_number = db.Column(db.String(50), unique=True)
    degree = db.Column(db.String(100))  # Ex: Dr., Prof.
    
    # Disponibilitate implicită
    work_start_hour = db.Column(db.Integer, default=9)  # 9:00
    work_end_hour = db.Column(db.Integer, default=17)  # 17:00
    slot_duration_minutes = db.Column(db.Integer, default=30)  # Sloturi de 30 min
    working_days = db.Column(db.String(50), default='monday,tuesday,wednesday,thursday,friday')  # luni-vineri
    
    # Relații
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Doctor {self.user.email}>'


class DoctorDailySchedule(db.Model):
    """Override de interval pentru o zi specifica a medicului."""
    __tablename__ = 'doctor_daily_schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    schedule_date = db.Column(db.Date, nullable=False)
    work_start_hour = db.Column(db.Integer, nullable=False)
    work_end_hour = db.Column(db.Integer, nullable=False)
    slot_duration_minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor = db.relationship('Doctor', backref=db.backref('daily_schedules', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'schedule_date', name='uq_doctor_schedule_date'),
    )

    def __repr__(self):
        return f'<DoctorDailySchedule {self.doctor_id} {self.schedule_date}>'
