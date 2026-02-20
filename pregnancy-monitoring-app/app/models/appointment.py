from app import db
from datetime import datetime, timedelta
from enum import Enum as PyEnum

class AppointmentStatus(PyEnum):
    """Stări ale unei programări."""
    REQUESTED = 'requested'  # Solicitată
    CONFIRMED = 'confirmed'  # Confirmată
    REJECTED = 'rejected'    # Respinsă
    CANCELLED = 'cancelled'  # Anulată
    COMPLETED = 'completed'  # Realizată

class Appointment(db.Model):
    """Model pentru programări consultație."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Detalii programare
    # Use start/end to allow overlap checks
    appointment_start = db.Column(db.DateTime, nullable=False)
    appointment_end = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default=AppointmentStatus.REQUESTED.value)
    
    # Note medicale
    notes = db.Column(db.Text)  # Note din consultație
    doctor_recommendations = db.Column(db.Text)  # Recomandări vizibile pentru pacientă
    doctor_internal_notes = db.Column(db.Text)  # Note interne (doar medic)
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relații
    patient = db.relationship('Patient', backref=db.backref('appointments'))
    doctor = db.relationship('Doctor', backref=db.backref('appointments'))
    
    def __repr__(self):
        return f'<Appointment {self.patient_id}/{self.doctor_id} {self.appointment_start}>'

    @staticmethod
    def is_doctor_available(doctor_id, start_dt, end_dt, exclude_appointment_id=None):
        """Checks for overlapping confirmed/accepted appointments for a doctor."""
        q = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.in_([
                AppointmentStatus.CONFIRMED.value,
                AppointmentStatus.REQUESTED.value,
            ]),
            Appointment.appointment_start < end_dt,
            Appointment.appointment_end > start_dt,
        )
        if exclude_appointment_id:
            q = q.filter(Appointment.id != exclude_appointment_id)
        return q.first() is None


class AppointmentSlot(db.Model):
    """Model pentru sloturi de programare disponibile ale medicului."""
    __tablename__ = 'appointment_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # Detalii slot
    slot_start = db.Column(db.DateTime, nullable=False)
    slot_end = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Metadate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relații
    doctor = db.relationship('Doctor', backref=db.backref('available_slots'))
    
    def __repr__(self):
        return f'<AppointmentSlot {self.doctor_id} {self.slot_start}>'
    
    @staticmethod
    def generate_slots_for_doctor(doctor_id, start_date, end_date):
        """
        Generează sloturi disponibile pentru un doctor într-o perioadă.
        Ține cont de disponibilitatea medicului și orele de lucru.
        """
        from app.models.doctor import Doctor, DoctorDailySchedule
        from app.models.pregnancy import DoctorUnavailability
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return []
        
        slots = []
        
        # Ensure start_date is datetime
        if not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        if not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        # Generate dates for working days in the range
        current_date = start_date.date()
        while current_date <= end_date.date():
            # Check if it's a working day (0=Monday, 4=Friday)
            if current_date.weekday() in [0, 1, 2, 3, 4]:  # Mon-Fri by default
                # Check if doctor is available this day
                if DoctorUnavailability.is_doctor_available(doctor_id, current_date):
                    # Use daily override if exists, otherwise default doctor program
                    day_schedule = DoctorDailySchedule.query.filter_by(
                        doctor_id=doctor_id,
                        schedule_date=current_date
                    ).first()
                    start_hour = day_schedule.work_start_hour if day_schedule else doctor.work_start_hour
                    end_hour = day_schedule.work_end_hour if day_schedule else doctor.work_end_hour
                    slot_duration = day_schedule.slot_duration_minutes if day_schedule else doctor.slot_duration_minutes

                    # Generate slots for this day
                    slot_start_dt = datetime.combine(
                        current_date,
                        datetime.min.time()
                    ).replace(hour=start_hour, minute=0)
                    
                    slot_end_dt = datetime.combine(
                        current_date,
                        datetime.min.time()
                    ).replace(hour=end_hour, minute=0)
                    
                    current_slot = slot_start_dt
                    while current_slot + timedelta(minutes=slot_duration) <= slot_end_dt:
                        slot_end = current_slot + timedelta(minutes=slot_duration)
                        
                        # Check if this slot is not already booked
                        if Appointment.is_doctor_available(
                            doctor_id,
                            current_slot,
                            slot_end
                        ):
                            slots.append({
                                'start': current_slot,
                                'end': slot_end,
                                'duration': slot_duration
                            })
                        
                        current_slot = slot_end
            
            current_date += timedelta(days=1)
        
        return slots
    
    @staticmethod
    def get_available_slots(doctor_id, start_date, end_date):
        """Obține sloturi disponibile pentru un doctor."""
        return AppointmentSlot.generate_slots_for_doctor(doctor_id, start_date, end_date)
