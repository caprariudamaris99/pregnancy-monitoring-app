from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app import db
from app.models.doctor import Doctor, DoctorDailySchedule
from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus
from app.models.document import Document, MedicalRecommendation
from app.models.medication import Medication
from app.models.message import Message, Notification, NotificationPreference
from app.forms.medical_forms import (
    DoctorProfileForm,
    DoctorScheduleForm,
    MedicationForm,
    RecommendationForm,
    MessageForm,
    DocumentUploadForm,
)
from datetime import datetime, timedelta
from calendar import month_name, monthcalendar
import os
from werkzeug.utils import secure_filename

bp = Blueprint('doctor', __name__, url_prefix='/doctor')


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


def _validate_work_interval_against_appointments(doctor_id, start_hour, end_hour):
    """Returneaza (ok, conflict_appointment_or_none) pentru intervalul propus."""
    start_min = start_hour * 60
    end_min = end_hour * 60
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_([
            AppointmentStatus.REQUESTED.value,
            AppointmentStatus.CONFIRMED.value,
        ]),
        Appointment.appointment_end >= datetime.utcnow(),
    ).order_by(Appointment.appointment_start.asc()).all()

    for appt in upcoming:
        appt_start_min = appt.appointment_start.hour * 60 + appt.appointment_start.minute
        appt_end_min = appt.appointment_end.hour * 60 + appt.appointment_end.minute
        if appt_start_min < start_min or appt_end_min > end_min:
            return False, appt
    return True, None


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard medic - vizualizare principala."""
    if current_user.role != 'doctor':
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    if not doctor:
        flash('Profil de medic nu gasit.', 'warning')
        return redirect(url_for('doctor.edit_profile'))

    patients_count = len(doctor.patients)

    today = datetime.utcnow().date()
    todays_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_start >= datetime.combine(today, datetime.min.time()),
        Appointment.appointment_start < datetime.combine(today + timedelta(days=1), datetime.min.time()),
    ).all()

    pending_requests = Appointment.query.filter_by(
        doctor_id=doctor.id,
        status=AppointmentStatus.REQUESTED.value,
    ).all()

    unread_messages = Message.query.filter_by(recipient_id=current_user.id, is_read=False).count()

    return render_template(
        'doctor/dashboard.html',
        doctor=doctor,
        patients_count=patients_count,
        todays_appointments=todays_appointments,
        pending_requests=pending_requests,
        unread_messages=unread_messages,
    )


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Editare profil medic."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    if not doctor:
        doctor = Doctor(user_id=current_user.id)
        db.session.add(doctor)
        db.session.commit()

    form = DoctorProfileForm()
    if form.validate_on_submit():
        if form.work_start_hour.data >= form.work_end_hour.data:
            flash('Intervalul orar este invalid. Ora de inceput trebuie sa fie mai mica decat ora de sfarsit.', 'danger')
            return render_template('doctor/edit_profile.html', form=form)

        ok, conflict_appt = _validate_work_interval_against_appointments(
            doctor.id,
            form.work_start_hour.data,
            form.work_end_hour.data,
        )
        if not ok:
            flash(
                f'Nu puteti salva intervalul. Exista o programare la '
                f'{conflict_appt.appointment_start.strftime("%d.%m.%Y %H:%M")} '
                f'care ar iesi in afara noului interval.',
                'danger',
            )
            return render_template('doctor/edit_profile.html', form=form)

        doctor.specialization = form.specialization.data
        doctor.clinic_name = form.clinic_name.data
        doctor.clinic_address = form.clinic_address.data
        doctor.license_number = form.license_number.data
        doctor.degree = form.degree.data
        doctor.work_start_hour = form.work_start_hour.data
        doctor.work_end_hour = form.work_end_hour.data
        doctor.slot_duration_minutes = form.slot_duration_minutes.data
        db.session.commit()

        flash('Profil medic actualizat cu succes. Sloturile de programare au fost actualizate.', 'success')
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'GET':
        form.specialization.data = doctor.specialization
        form.clinic_name.data = doctor.clinic_name
        form.clinic_address.data = doctor.clinic_address
        form.license_number.data = doctor.license_number
        form.degree.data = doctor.degree
        form.work_start_hour.data = doctor.work_start_hour
        form.work_end_hour.data = doctor.work_end_hour
        form.slot_duration_minutes.data = doctor.slot_duration_minutes

    return render_template('doctor/edit_profile.html', form=form)


@bp.route('/calendar')
@login_required
def calendar():
    """Calendarul medicului - vizualizare pe zile."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    if not doctor:
        flash('Profil de medic nu gasit.', 'warning')
        return redirect(url_for('doctor.edit_profile'))

    today = datetime.utcnow().date()
    year = request.args.get('year', type=int) or today.year
    month = request.args.get('month', type=int) or today.month
    if month < 1 or month > 12:
        month = today.month
    if year < 2000 or year > 2100:
        year = today.year

    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)

    monthly_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_start >= month_start,
        Appointment.appointment_start < next_month_start,
    ).order_by(Appointment.appointment_start.asc()).all()

    appointments_by_day = {}
    for appt in monthly_appointments:
        day = appt.appointment_start.day
        appointments_by_day.setdefault(day, []).append(appt)

    schedule_overrides = DoctorDailySchedule.query.filter(
        DoctorDailySchedule.doctor_id == doctor.id,
        DoctorDailySchedule.schedule_date >= month_start.date(),
        DoctorDailySchedule.schedule_date < next_month_start.date(),
    ).all()
    overrides_by_day = {s.schedule_date.day: s for s in schedule_overrides}

    weeks = monthcalendar(year, month)
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return render_template(
        'doctor/calendar.html',
        doctor=doctor,
        year=year,
        month=month,
        month_name=month_name[month],
        weeks=weeks,
        appointments_by_day=appointments_by_day,
        overrides_by_day=overrides_by_day,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
    )


@bp.route('/calendar/day/<date_str>', methods=['GET', 'POST'])
@login_required
def calendar_day(date_str):
    """Editare interval doar pentru ziua selectata."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    if not doctor:
        flash('Profil de medic nu gasit.', 'warning')
        return redirect(url_for('doctor.edit_profile'))

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data selectata este invalida.', 'danger')
        return redirect(url_for('doctor.calendar'))

    day_override = DoctorDailySchedule.query.filter_by(
        doctor_id=doctor.id,
        schedule_date=selected_date
    ).first()

    form = DoctorScheduleForm()
    if request.method == 'GET':
        form.work_start_hour.data = day_override.work_start_hour if day_override else doctor.work_start_hour
        form.work_end_hour.data = day_override.work_end_hour if day_override else doctor.work_end_hour
        form.slot_duration_minutes.data = day_override.slot_duration_minutes if day_override else doctor.slot_duration_minutes

    if form.validate_on_submit():
        start_hour = form.work_start_hour.data
        end_hour = form.work_end_hour.data
        slot_duration = form.slot_duration_minutes.data

        if start_hour < 0 or start_hour > 23 or end_hour < 0 or end_hour > 23 or start_hour >= end_hour:
            flash('Interval invalid. Folositi ore intre 0 si 23, iar inceputul sa fie inainte de sfarsit.', 'danger')
        elif slot_duration <= 0:
            flash('Durata slotului trebuie sa fie mai mare de 0.', 'danger')
        else:
            day_start = datetime.combine(selected_date, datetime.min.time())
            day_end = datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
            day_appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.status.in_([AppointmentStatus.REQUESTED.value, AppointmentStatus.CONFIRMED.value]),
                Appointment.appointment_start >= day_start,
                Appointment.appointment_start < day_end,
            ).all()

            start_min = start_hour * 60
            end_min = end_hour * 60
            conflict = None
            for appt in day_appointments:
                appt_start_min = appt.appointment_start.hour * 60 + appt.appointment_start.minute
                appt_end_min = appt.appointment_end.hour * 60 + appt.appointment_end.minute
                if appt_start_min < start_min or appt_end_min > end_min:
                    conflict = appt
                    break

            if conflict:
                flash(
                    f'Nu puteti salva intervalul pentru aceasta zi. Programarea de la '
                    f'{conflict.appointment_start.strftime("%H:%M")} ar iesi in afara intervalului.',
                    'danger'
                )
            else:
                if day_override is None:
                    day_override = DoctorDailySchedule(
                        doctor_id=doctor.id,
                        schedule_date=selected_date,
                    )
                    db.session.add(day_override)
                day_override.work_start_hour = start_hour
                day_override.work_end_hour = end_hour
                day_override.slot_duration_minutes = slot_duration
                db.session.commit()
                flash('Intervalul pentru ziua selectata a fost actualizat.', 'success')
                return redirect(url_for('doctor.calendar_day', date_str=date_str))

    day_start = datetime.combine(selected_date, datetime.min.time())
    day_end = datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
    day_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_start >= day_start,
        Appointment.appointment_start < day_end,
    ).order_by(Appointment.appointment_start.asc()).all()

    return render_template(
        'doctor/calendar_day.html',
        doctor=doctor,
        selected_date=selected_date,
        appointments=day_appointments,
        form=form,
        has_override=day_override is not None,
    )


@bp.route('/calendar/day/<date_str>/reset', methods=['POST'])
@login_required
def reset_calendar_day(date_str):
    """Sterge override-ul unei zile si revine la programul default."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    if not doctor:
        flash('Profil de medic nu gasit.', 'warning')
        return redirect(url_for('doctor.edit_profile'))

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Data selectata este invalida.', 'danger')
        return redirect(url_for('doctor.calendar'))

    day_override = DoctorDailySchedule.query.filter_by(
        doctor_id=doctor.id,
        schedule_date=selected_date
    ).first()
    if day_override:
        db.session.delete(day_override)
        db.session.commit()
        flash('Ziua a revenit la intervalul default.', 'success')
    else:
        flash('Nu exista override pentru aceasta zi.', 'info')

    return redirect(url_for('doctor.calendar_day', date_str=date_str))


@bp.route('/patients')
@login_required
def patients():
    """Lista paciente asociate."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patients_list = doctor.patients

    search = request.args.get('search', '')
    if search:
        patients_list = [
            p
            for p in patients_list
            if search.lower() in (p.user.first_name + ' ' + p.user.last_name).lower()
        ]

    return render_template('doctor/patients.html', patients=patients_list, search=search)


@bp.route('/patient/<int:patient_id>')
@login_required
def patient_details(patient_id):
    """Dosar pacient - detalii complete."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)

    if patient.associated_doctor_id != doctor.id:
        flash('Nu aveti acces la acest dosar.', 'danger')
        return redirect(url_for('doctor.patients'))

    pregnancy_info = patient.calculate_pregnancy_week()
    vital_signs = patient.vital_signs[-10:] if patient.vital_signs else []
    symptoms = patient.symptoms[-20:] if patient.symptoms else []
    documents = patient.documents
    appointments = patient.appointments

    recommendations = MedicalRecommendation.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient.id,
    ).all()

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == patient.user_id))
        | ((Message.sender_id == patient.user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.sent_at.desc()).all()

    message_form = MessageForm()
    document_form = DocumentUploadForm()

    return render_template(
        'doctor/patient_details.html',
        patient=patient,
        pregnancy_info=pregnancy_info,
        vital_signs=vital_signs,
        symptoms=symptoms,
        documents=documents,
        appointments=appointments,
        recommendations=recommendations,
        messages=messages,
        message_form=message_form,
        document_form=document_form,
    )


@bp.route('/appointments')
@login_required
def appointments():
    """Gestionare programari."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    appointments_list = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.appointment_start).all()

    status_filter = request.args.get('status', 'all')
    if status_filter != 'all':
        appointments_list = [a for a in appointments_list if a.status == status_filter]

    return render_template('doctor/appointments.html', appointments=appointments_list, status=status_filter)


@bp.route('/appointment/<int:appointment_id>/confirm', methods=['POST'])
@login_required
def confirm_appointment(appointment_id):
    """Confirmare programare."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.doctor_profile.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.appointments'))

    appointment.status = AppointmentStatus.CONFIRMED.value
    pref = _get_or_create_notification_preference(appointment.patient.user_id)
    if pref.enable_appointment_reminders:
        db.session.add(Notification(
            user_id=appointment.patient.user_id,
            type='appointment',
            title='Programare confirmata',
            message=f'Programarea din {appointment.appointment_start.strftime("%d.%m.%Y %H:%M")} a fost confirmata de medic.',
            related_object_type='Appointment',
            related_object_id=appointment.id,
        ))
    db.session.commit()
    flash('Programare confirmata.', 'success')
    return redirect(url_for('doctor.appointments'))


@bp.route('/appointment/<int:appointment_id>/reject', methods=['POST'])
@login_required
def reject_appointment(appointment_id):
    """Respinge programare."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.doctor_profile.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.appointments'))

    appointment.status = AppointmentStatus.REJECTED.value
    db.session.commit()
    flash('Programare respinsa.', 'success')
    return redirect(url_for('doctor.appointments'))


@bp.route('/recommendation/add/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_recommendation(patient_id):
    """Adauga recomandare medicala."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)

    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))

    form = RecommendationForm()
    if form.validate_on_submit():
        recommendation = MedicalRecommendation(
            doctor_id=doctor.id,
            patient_id=patient.id,
            title=form.title.data,
            description=form.description.data,
            visibility=form.visibility.data,
        )
        db.session.add(recommendation)
        db.session.commit()

        flash('Recomandare adaugata cu succes.', 'success')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id))

    return render_template('doctor/add_recommendation.html', form=form, patient=patient)


@bp.route('/patient/<int:patient_id>/message/send', methods=['POST'])
@login_required
def send_message_to_patient(patient_id):
    """Trimite mesaj catre pacienta din dosar."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))

    form = MessageForm()
    if form.validate_on_submit():
        new_message = Message(
            sender_id=current_user.id,
            recipient_id=patient.user_id,
            subject=form.subject.data,
            content=form.content.data,
        )
        db.session.add(new_message)
        pref = _get_or_create_notification_preference(patient.user_id)
        if pref.enable_message_notifications:
            db.session.add(Notification(
                user_id=patient.user_id,
                type='message',
                title='Mesaj nou',
                message=f'Ai primit un mesaj nou de la Dr. {current_user.last_name}.',
                related_object_type='Message',
            ))
        db.session.commit()
        flash('Mesajul a fost trimis.', 'success')
    else:
        flash('Mesajul nu a putut fi trimis. Verificati campurile.', 'danger')

    return redirect(url_for('doctor.patient_details', patient_id=patient_id, tab='messages'))


@bp.route('/patient/<int:patient_id>/document/upload', methods=['POST'])
@login_required
def upload_patient_document(patient_id):
    """Incarca document in dosarul pacientei (medic)."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))

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
            file_name=file.filename,
            file_path=filepath,
            file_type=filename.split('.')[-1],
            document_type=form.document_type.data,
            lab_name=form.lab_name.data,
            document_date=datetime.strptime(form.document_date.data, '%Y-%m-%d') if form.document_date.data else None,
            uploaded_at=datetime.utcnow(),
        )
        db.session.add(document)
        db.session.commit()
        flash('Document incarcat cu succes.', 'success')
    else:
        flash('Documentul nu a putut fi incarcat. Verificati campurile.', 'danger')

    return redirect(url_for('doctor.patient_details', patient_id=patient_id, tab='documents'))


@bp.route('/patient/<int:patient_id>/document/<int:document_id>/download')
@login_required
def download_patient_document(patient_id, document_id):
    """Descarca documentul pacientei din dosar (pentru medicul asociat)."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    if patient.associated_doctor_id != doctor.id:
        flash('Nu aveti acces la acest dosar.', 'danger')
        return redirect(url_for('doctor.patients'))

    document = Document.query.get_or_404(document_id)
    if document.patient_id != patient.id:
        flash('Documentul nu apartine acestei paciente.', 'danger')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id, tab='documents'))

    file_path = _resolve_document_path(document.file_path)
    if not os.path.exists(file_path):
        flash('Fisierul nu a fost gasit pe server.', 'danger')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id, tab='documents'))

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.file_name
    )


@bp.route('/patient/<int:patient_id>/medication/<int:medication_id>/delete', methods=['POST'])
@login_required
def delete_medication(patient_id, medication_id):
    """Sterge o medicatie din dosarul pacientei."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))

    medication = Medication.query.get_or_404(medication_id)
    if medication.patient_id != patient.id:
        flash('Medicamentul nu apartine acestei paciente.', 'danger')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id))

    db.session.delete(medication)
    db.session.commit()
    flash('Medicamentul a fost sters.', 'success')
    return redirect(url_for('doctor.patient_details', patient_id=patient.id))


@bp.route('/patient/<int:patient_id>/recommendation/<int:recommendation_id>/delete', methods=['POST'])
@login_required
def delete_recommendation(patient_id, recommendation_id):
    """Sterge o recomandare medicala."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))

    recommendation = MedicalRecommendation.query.get_or_404(recommendation_id)
    if recommendation.patient_id != patient.id or recommendation.doctor_id != doctor.id:
        flash('Recomandarea nu poate fi stearsa.', 'danger')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id))

    db.session.delete(recommendation)
    db.session.commit()
    flash('Recomandarea a fost stearsa.', 'success')
    return redirect(url_for('doctor.patient_details', patient_id=patient.id))


@bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    """Mesagerie."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    doctor = current_user.doctor_profile
    patients = doctor.patients if doctor else []
    form = MessageForm()
    preselected_recipient_id = request.args.get('recipient_user_id', type=int)
    reply_subject = request.args.get('reply_subject', type=str)

    if request.method == 'POST':
        recipient_user_id = request.form.get('recipient_user_id', type=int)
        allowed_recipient_ids = {p.user_id for p in patients}

        if not recipient_user_id or recipient_user_id not in allowed_recipient_ids:
            flash('Selectati o pacienta valida pentru trimiterea mesajului.', 'danger')
            return redirect(url_for('doctor.messages'))

        if form.validate_on_submit():
            new_message = Message(
                sender_id=current_user.id,
                recipient_id=recipient_user_id,
                subject=form.subject.data,
                content=form.content.data,
            )
            db.session.add(new_message)
            pref = _get_or_create_notification_preference(recipient_user_id)
            if pref.enable_message_notifications:
                db.session.add(Notification(
                    user_id=recipient_user_id,
                    type='message',
                    title='Mesaj nou',
                    message=f'Ai primit un mesaj nou de la Dr. {current_user.last_name}.',
                    related_object_type='Message',
                ))
            db.session.commit()
            flash('Mesajul a fost trimis cu succes.', 'success')
            return redirect(url_for('doctor.messages'))
        flash('Mesajul nu a putut fi trimis. Verificati campurile.', 'danger')
    elif reply_subject:
        form.subject.data = reply_subject

    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.sent_at.desc()).all()

    return render_template(
        'doctor/messages.html',
        messages=messages,
        form=form,
        patients=patients,
        preselected_recipient_id=preselected_recipient_id,
    )


@bp.route('/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Marcheaza mesajul ca citit pentru medic."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))

    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.messages'))

    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.session.commit()

    return redirect(url_for('doctor.messages'))
