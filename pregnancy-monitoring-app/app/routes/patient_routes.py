from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus, AppointmentSlot
from app.models.medication import Medication
from app.models.symptom import Symptom, VitalSign
from app.models.document import Document, MedicalRecommendation
from app.models.message import Message, Notification, NotificationPreference
from app.models.user import User
from app.data.sfaturi import sfaturi_sarcina
from app.forms.patient_forms import (
    AppointmentSlotSelectionForm,
    DoctorSelectionForm,
    PatientProfileForm,
    SelectDoctorAndDateForm,
    SymptomForm,
    VitalSignForm,
)
from app.forms.medical_forms import DocumentUploadForm, MessageForm
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

bp = Blueprint('patient', __name__, url_prefix='/patient')


def _resolve_document_path(file_path):
    """Rezolva calea fizica a documentului stocat relativ."""
    if os.path.isabs(file_path):
        return file_path

    project_root = os.path.abspath(os.path.join(current_app.root_path, '..'))
    candidates = [
        os.path.join(project_root, file_path),
        os.path.join(current_app.root_path, file_path),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def _get_or_create_notification_preference(user_id):
    pref = NotificationPreference.query.filter_by(user_id=user_id).first()
    if not pref:
        pref = NotificationPreference(user_id=user_id, reminder_hour=9)
        db.session.add(pref)
        db.session.commit()
    return pref


def _create_patient_reminder_notifications(patient):
    """Genereaza reminder-e la accesarea dashboard-ului, cu deduplicare."""
    pref = _get_or_create_notification_preference(current_user.id)
    now = datetime.utcnow()
    if now.hour < pref.reminder_hour:
        return

    if pref.enable_appointment_reminders:
        tomorrow = (now + timedelta(days=1)).date()
        appts = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status.in_([AppointmentStatus.REQUESTED.value, AppointmentStatus.CONFIRMED.value]),
            Appointment.appointment_start >= datetime.combine(tomorrow, datetime.min.time()),
            Appointment.appointment_start < datetime.combine(tomorrow + timedelta(days=1), datetime.min.time()),
        ).all()
        for appt in appts:
            exists = Notification.query.filter(
                Notification.user_id == current_user.id,
                Notification.type == 'appointment_reminder',
                Notification.related_object_type == 'Appointment',
                Notification.related_object_id == appt.id,
                Notification.created_at >= datetime.combine(now.date(), datetime.min.time()),
            ).first()
            if not exists:
                db.session.add(Notification(
                    user_id=current_user.id,
                    type='appointment_reminder',
                    title='Reminder programare',
                    message=f'Ai programare maine la {appt.appointment_start.strftime("%H:%M")}.',
                    related_object_type='Appointment',
                    related_object_id=appt.id,
                ))

    if pref.enable_medication_reminders:
        active_meds = Medication.query.filter_by(patient_id=patient.id, is_active=True).all()
        for med in active_meds:
            exists = Notification.query.filter(
                Notification.user_id == current_user.id,
                Notification.type == 'medication_reminder',
                Notification.related_object_type == 'Medication',
                Notification.related_object_id == med.id,
                Notification.created_at >= datetime.combine(now.date(), datetime.min.time()),
            ).first()
            if not exists:
                db.session.add(Notification(
                    user_id=current_user.id,
                    type='medication_reminder',
                    title='Reminder medicatie',
                    message=f'Nu uita medicatia de azi: {med.name}.',
                    related_object_type='Medication',
                    related_object_id=med.id,
                ))

    db.session.commit()

def _get_current_pregnancy_week(patient):
    """Returneaza saptamana curenta de sarcina in intervalul 1..40."""
    pregnancy_info = patient.calculate_pregnancy_week()
    if not pregnancy_info:
        return 1, pregnancy_info
    week_number = pregnancy_info[0]
    week_number = max(1, min(40, week_number))
    return week_number, pregnancy_info

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard pacientă - vizualizare principală."""
    if current_user.role != 'patient':
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    if not patient:
        flash('Profil de pacientă nu găsit.', 'warning')
        return redirect(url_for('patient.edit_profile'))
    
    # Calculare săptămâni de sarcină
    current_week, pregnancy_info = _get_current_pregnancy_week(patient)
    
    # Ultimele măsurători
    latest_vital_signs = VitalSign.query.filter_by(patient_id=patient.id).order_by(VitalSign.measurement_date.desc()).limit(5).all()
    chart_points = list(reversed(latest_vital_signs))
    chart_data = {
        'labels': [v.measurement_date.strftime('%d.%m.%Y') for v in chart_points],
        'weights': [v.weight_kg for v in chart_points],
        'systolic': [v.systolic_bp for v in chart_points],
        'diastolic': [v.diastolic_bp for v in chart_points],
        'glucose': [v.blood_glucose_mg_dl for v in chart_points],
    }
    
    # Programări viitoare
    upcoming_appointments = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.appointment_start >= datetime.utcnow()
    ).order_by(Appointment.appointment_start).limit(5).all()
    
    # Recomandari vizibile
    visible_recommendations = MedicalRecommendation.query.filter_by(
        patient_id=patient.id,
        visibility='patient'
    ).order_by(MedicalRecommendation.created_at.desc()).all()

    _create_patient_reminder_notifications(patient)

    # Notificări necitite
    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()
    
    current_week_article = sfaturi_sarcina.get(current_week)

    return render_template('patient/dashboard.html',
        patient=patient,
        pregnancy_info=pregnancy_info,
        current_week=current_week,
        current_week_article=current_week_article,
        latest_vital_signs=latest_vital_signs,
        chart_data=chart_data,
        upcoming_appointments=upcoming_appointments,
        visible_recommendations=visible_recommendations,
        unread_messages=unread_messages)

@bp.route('/weekly-info')
@login_required
def weekly_info():
    """Afiseaza informatiile pe saptamani, cu selectie de saptamana."""
    patient = current_user.patient_profile
    if not patient:
        flash('Doar conturile cu profil de pacienta pot accesa aceasta pagina.', 'danger')
        return redirect(url_for('common.dashboard'))

    current_week, pregnancy_info = _get_current_pregnancy_week(patient)
    requested_week = request.args.get('week', type=int)
    selected_week = current_week if requested_week is None else max(1, min(40, requested_week))

    selected_article = sfaturi_sarcina.get(selected_week)
    week_numbers = sorted(sfaturi_sarcina.keys())

    return render_template(
        'patient/weekly_info.html',
        patient=patient,
        pregnancy_info=pregnancy_info,
        current_week=current_week,
        selected_week=selected_week,
        selected_article=selected_article,
        week_numbers=week_numbers,
    )

@bp.route('/weekly-info/<int:week_number>')
@login_required
def weekly_info_week(week_number):
    """Shortcut pentru deschiderea unei saptamani specifice."""
    return redirect(url_for('patient.weekly_info', week=week_number))


@bp.route('/doctor/select', methods=['GET', 'POST'])
@login_required
def select_doctor():
    """Alegere sau schimbare medic asociat."""
    if current_user.role != 'patient':
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('common.dashboard'))

    patient = current_user.patient_profile
    if not patient:
        flash('Profil de pacienta negasit.', 'warning')
        return redirect(url_for('patient.edit_profile'))

    from app.models.doctor import Doctor

    doctors = Doctor.query.join(Doctor.user).order_by(User.first_name, User.last_name).all()
    if not doctors:
        flash('Nu exista medici disponibili momentan.', 'info')
        return redirect(url_for('common.dashboard'))

    form = DoctorSelectionForm()
    form.doctor_id.choices = [
        (
            doctor.id,
            f"Dr. {doctor.user.first_name} {doctor.user.last_name} - "
            f"{doctor.specialization or 'Nespecificat'}",
        )
        for doctor in doctors
    ]

    if request.method == 'GET' and patient.associated_doctor_id:
        form.doctor_id.data = patient.associated_doctor_id

    if form.validate_on_submit():
        selected_doctor = Doctor.query.get_or_404(form.doctor_id.data)
        previous_doctor_id = patient.associated_doctor_id
        patient.associated_doctor_id = selected_doctor.id
        db.session.commit()

        if previous_doctor_id and previous_doctor_id != selected_doctor.id:
            flash('Medicul asociat a fost schimbat cu succes.', 'success')
        elif previous_doctor_id == selected_doctor.id:
            flash('Acest medic este deja asociat contului dumneavoastra.', 'info')
        else:
            flash('Medicul a fost asociat cu succes.', 'success')
        return redirect(url_for('common.dashboard'))

    return render_template(
        'patient/select_doctor.html',
        form=form,
        patient=patient,
    )

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editare profil medical - date sarcină și antecedente."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    if not patient:
        patient = Patient(user_id=current_user.id)
        db.session.add(patient)
        db.session.commit()
    
    form = PatientProfileForm()
    pref = _get_or_create_notification_preference(current_user.id)
    if form.validate_on_submit():
        patient.lmp_date = form.lmp_date.data
        patient.pregnancy_type = form.pregnancy_type.data
        patient.blood_type = form.blood_type.data
        patient.rh_factor = form.rh_factor.data
        patient.allergies = form.allergies.data
        patient.chronic_conditions = form.chronic_conditions.data
        patient.permanent_medication = form.permanent_medication.data
        patient.surgical_history = form.surgical_history.data
        if form.reminder_hour.data is not None:
            if form.reminder_hour.data < 0 or form.reminder_hour.data > 23:
                flash('Ora reminder trebuie sa fie intre 0 si 23.', 'danger')
                return render_template('patient/edit_profile.html', form=form)
            pref.reminder_hour = form.reminder_hour.data
        
        patient.update_due_date()
        db.session.commit()
        
        flash('Profil medical actualizat cu succes.', 'success')
        return redirect(url_for('patient.dashboard'))
    
    elif request.method == 'GET':
        if patient.lmp_date:
            form.lmp_date.data = patient.lmp_date
        form.pregnancy_type.data = patient.pregnancy_type
        form.blood_type.data = patient.blood_type
        form.rh_factor.data = patient.rh_factor
        form.allergies.data = patient.allergies
        form.chronic_conditions.data = patient.chronic_conditions
        form.permanent_medication.data = patient.permanent_medication
        form.surgical_history.data = patient.surgical_history
        form.reminder_hour.data = pref.reminder_hour
    
    return render_template('patient/edit_profile.html', form=form)

@bp.route('/vital-signs', methods=['GET', 'POST'])
@login_required
def vital_signs():
    """Monitorizare parametri vitali."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    form = VitalSignForm()
    
    if form.validate_on_submit():
        vital_sign = VitalSign(
            patient_id=patient.id,
            weight_kg=form.weight_kg.data,
            systolic_bp=form.systolic_bp.data,
            diastolic_bp=form.diastolic_bp.data,
            blood_glucose_mg_dl=form.blood_glucose.data,
            notes=form.notes.data,
            measurement_date=datetime.utcnow()
        )
        db.session.add(vital_sign)
        db.session.commit()
        
        flash('Parametri înregistrați cu succes.', 'success')
        return redirect(url_for('patient.vital_signs'))
    
    vital_signs_list = VitalSign.query.filter_by(patient_id=patient.id).order_by(VitalSign.measurement_date.desc()).all()
    
    return render_template('patient/vital_signs.html', form=form, vital_signs=vital_signs_list)

@bp.route('/symptoms', methods=['GET', 'POST'])
@login_required
def symptoms():
    """Raportare simptome."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    form = SymptomForm()
    
    if form.validate_on_submit():
        symptom_type = form.other_symptom.data if form.symptom_type.data == 'other' else form.symptom_type.data
        
        symptom = Symptom(
            patient_id=patient.id,
            symptom_type=symptom_type,
            intensity=form.intensity.data,
            observations=form.observations.data,
            reported_date=datetime.utcnow()
        )
        db.session.add(symptom)
        db.session.commit()
        
        flash('Simptom înregistrat cu succes.', 'success')
        return redirect(url_for('patient.symptoms'))
    
    symptoms_list = Symptom.query.filter_by(patient_id=patient.id).order_by(Symptom.reported_date.desc()).all()
    
    return render_template('patient/symptoms.html', form=form, symptoms=symptoms_list)

@bp.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    """Gestionare documente medicale."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    form = DocumentUploadForm()
    
    if form.validate_on_submit() and form.document_file.data:
        file = form.document_file.data
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join('uploads', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        document = Document(
            uploaded_by_user_id=current_user.id,
            patient_id=patient.id,
            file_name=form.document_file.data.filename,
            file_path=filepath,
            file_type=filename.split('.')[-1],
            document_type=form.document_type.data,
            lab_name=form.lab_name.data,
            document_date=datetime.strptime(form.document_date.data, '%Y-%m-%d') if form.document_date.data else None,
            uploaded_at=datetime.utcnow()
        )
        db.session.add(document)
        db.session.commit()
        
        flash('Document încărcat cu succes.', 'success')
        return redirect(url_for('patient.documents'))
    
    patient_documents = Document.query.filter_by(patient_id=patient.id).order_by(Document.uploaded_at.desc()).all()
    
    return render_template('patient/documents.html', form=form, documents=patient_documents)

@bp.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    """Gestionare programări consultații."""
    patient = current_user.patient_profile
    if not patient:
        flash('Doar conturile cu profil de pacienta pot accesa programarile.', 'danger')
        return redirect(url_for('common.dashboard'))
    
    # Filtrare programări
    status_filter = request.args.get('status', 'all')
    if status_filter == 'all':
        appointments_list = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_start).all()
    else:
        appointments_list = Appointment.query.filter_by(patient_id=patient.id, status=status_filter).order_by(Appointment.appointment_start).all()
    
    return render_template('patient/appointments.html', appointments=appointments_list, status=status_filter)

@bp.route('/appointments/new', methods=['GET', 'POST'])
@login_required
def request_appointment():
    """Selectare medic și dată pentru a vedea sloturi disponibile."""
    patient = current_user.patient_profile
    if not patient:
        flash('Doar conturile cu profil de pacienta pot solicita programari.', 'danger')
        return redirect(url_for('common.dashboard'))
    from app.models.doctor import Doctor
    
    form = SelectDoctorAndDateForm()
    # Populează lista de medici
    form.doctor_id.choices = [(d.id, f"{d.user.first_name} {d.user.last_name} ({d.specialization})") 
                               for d in Doctor.query.all()]
    
    if form.validate_on_submit():
        # Redirecționează la pagina cu sloturi disponibile
        return redirect(url_for('patient.view_appointment_slots',
                              doctor_id=form.doctor_id.data,
                              date=form.appointment_date.data.isoformat()))
    
    return render_template('patient/request_appointment.html', form=form)


@bp.route('/appointments/slots/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def view_appointment_slots(doctor_id):
    """Vizualizează sloturi disponibile ale unui medic."""
    patient = current_user.patient_profile
    if not patient:
        flash('Doar conturile cu profil de pacienta pot vedea sloturi.', 'danger')
        return redirect(url_for('common.dashboard'))
    
    from app.models.doctor import Doctor
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Obține data din parametru query
    date_str = request.args.get('date')
    if not date_str:
        flash('Data programării nu a fost specificată.', 'warning')
        return redirect(url_for('patient.request_appointment'))
    
    try:
        appointment_date = datetime.fromisoformat(date_str).date()
    except (ValueError, AttributeError):
        flash('Data programării nu este validă.', 'danger')
        return redirect(url_for('patient.request_appointment'))
    
    # Verifică că data nu este în trecut
    if appointment_date < datetime.now().date():
        flash('Nu puteți programa o consultație în trecut.', 'danger')
        return redirect(url_for('patient.request_appointment'))
    
    # Generează sloturi pentru ziua selectată
    day_start = datetime.combine(appointment_date, datetime.min.time()).replace(hour=doctor.work_start_hour)
    day_end = datetime.combine(appointment_date, datetime.min.time()).replace(hour=doctor.work_end_hour)
    
    available_slots = AppointmentSlot.get_available_slots(doctor_id, day_start, day_end)
    
    if not available_slots:
        flash('Nu sunt sloturi disponibile în ziua selectată. Vă rugăm selectați o altă dată.', 'info')
        return redirect(url_for('patient.request_appointment'))
    
    return render_template('patient/appointment_slots.html',
                         doctor=doctor,
                         appointment_date=appointment_date,
                         slots=available_slots,
                         patient=patient)


@bp.route('/appointments/confirm-slot', methods=['POST'])
@login_required
def confirm_appointment_slot():
    """Confirmă o programare pentru un slot selectat."""
    patient = current_user.patient_profile
    if not patient:
        flash('Doar conturile cu profil de pacienta pot confirma programari.', 'danger')
        return redirect(url_for('common.dashboard'))
    
    from app.models.doctor import Doctor
    
    # Obține datele din formular
    slot_start_str = request.form.get('slot_start')
    slot_end_str = request.form.get('slot_end')
    doctor_id = request.form.get('doctor_id')
    notes = request.form.get('notes', '')
    
    if not all([slot_start_str, slot_end_str, doctor_id]):
        flash('Datele slotului nu sunt complete.', 'danger')
        return redirect(url_for('patient.request_appointment'))
    
    try:
        slot_start = datetime.fromisoformat(slot_start_str)
        slot_end = datetime.fromisoformat(slot_end_str)
        doctor_id = int(doctor_id)
    except (ValueError, TypeError):
        flash('Date invalide.', 'danger')
        return redirect(url_for('patient.request_appointment'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Verifică disponibilitatea
    if not Appointment.is_doctor_available(doctor_id, slot_start, slot_end):
        flash('Slotul selectat nu mai este disponibil.', 'warning')
        return redirect(url_for('patient.request_appointment'))
    
    # Crează programarea
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        appointment_start=slot_start,
        appointment_end=slot_end,
        duration_minutes=doctor.slot_duration_minutes,
        notes=notes,
        status=AppointmentStatus.REQUESTED.value
    )
    db.session.add(appointment)
    db.session.commit()
    
    # Crea notificare pentru medic
    from app.models.message import Notification
    notification = Notification(
        user_id=doctor.user_id,
        type='appointment',
        title='Cerere nouă de programare',
        message=f'Pacientă {patient.user.first_name} {patient.user.last_name} a solicitat o programare pe {slot_start.strftime("%d.%m.%Y %H:%M")}',
        related_object_id=appointment.id,
        related_object_type='Appointment'
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Cererea de programare a fost trimisă. Așteptați confirmarea medicului.', 'success')
    return redirect(url_for('patient.appointments'))

@bp.route('/medications')
@login_required
def medications():
    """Vizualizare medicație."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    visible_recommendations = MedicalRecommendation.query.filter_by(
        patient_id=patient.id,
        visibility='patient'
    ).order_by(MedicalRecommendation.created_at.desc()).all()
    
    return render_template(
        'patient/medications.html',
        visible_recommendations=visible_recommendations
    )

@bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    """Mesagerie."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))

    patient = current_user.patient_profile
    doctor = patient.associated_doctor if patient else None
    form = MessageForm()
    document_form = DocumentUploadForm()
    reply_subject = request.args.get('reply_subject', type=str)

    if request.method == 'POST':
        if not doctor:
            flash('Nu aveti medic asociat. Selectati mai intai un medic.', 'warning')
            return redirect(url_for('patient.select_doctor'))

        if form.validate_on_submit():
            new_message = Message(
                sender_id=current_user.id,
                recipient_id=doctor.user_id,
                subject=form.subject.data,
                content=form.content.data
            )
            db.session.add(new_message)
            pref = _get_or_create_notification_preference(doctor.user_id)
            if pref.enable_message_notifications:
                db.session.add(Notification(
                    user_id=doctor.user_id,
                    type='message',
                    title='Mesaj nou',
                    message=f'Ai primit un mesaj nou de la {current_user.first_name} {current_user.last_name}.',
                    related_object_type='Message',
                ))
            db.session.commit()
            flash('Mesajul a fost trimis cu succes.', 'success')
            return redirect(url_for('patient.messages'))
        flash('Mesajul nu a putut fi trimis. Verificati campurile.', 'danger')
    elif reply_subject:
        form.subject.data = reply_subject
    
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.sent_at.desc()).all()
    patient_documents = Document.query.filter_by(patient_id=patient.id).order_by(Document.uploaded_at.desc()).limit(10).all()
    
    return render_template(
        'patient/messages.html',
        messages=messages,
        form=form,
        doctor=doctor,
        document_form=document_form,
        documents=patient_documents
    )


@bp.route('/messages/document/upload', methods=['POST'])
@login_required
def upload_document_from_messages():
    """Incarca document medical din pagina de mesagerie."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))

    patient = current_user.patient_profile
    form = DocumentUploadForm()
    if form.validate_on_submit() and form.document_file.data:
        file = form.document_file.data
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join('uploads', filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)

        document = Document(
            uploaded_by_user_id=current_user.id,
            patient_id=patient.id,
            file_name=form.document_file.data.filename,
            file_path=filepath,
            file_type=filename.split('.')[-1],
            document_type=form.document_type.data,
            lab_name=form.lab_name.data,
            document_date=datetime.strptime(form.document_date.data, '%Y-%m-%d') if form.document_date.data else None,
            uploaded_at=datetime.utcnow()
        )
        db.session.add(document)
        db.session.commit()
        flash('Document incarcat cu succes.', 'success')
    else:
        flash('Documentul nu a putut fi incarcat. Verificati campurile.', 'danger')
    return redirect(url_for('patient.messages'))


@bp.route('/document/<int:document_id>/download')
@login_required
def download_document(document_id):
    """Descarca documentul pacientei curente."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))

    patient = current_user.patient_profile
    if not patient:
        flash('Profil pacienta negasit.', 'danger')
        return redirect(url_for('common.dashboard'))

    document = Document.query.get_or_404(document_id)
    if document.patient_id != patient.id:
        flash('Nu aveti acces la acest document.', 'danger')
        return redirect(url_for('patient.messages'))

    file_path = _resolve_document_path(document.file_path)
    if not os.path.exists(file_path):
        flash('Fisierul nu a fost gasit pe server.', 'danger')
        return redirect(url_for('patient.messages'))

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.file_name
    )

@bp.route('/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Marchează mesaj ca citit."""
    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('patient.messages'))
    
    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.session.commit()
    
    return redirect(url_for('patient.messages'))

