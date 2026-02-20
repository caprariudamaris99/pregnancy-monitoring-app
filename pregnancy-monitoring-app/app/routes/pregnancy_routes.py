"""
Routes suplimentare pentru gestionarea calendarului de sarcină și task-urilor.
Adaugă-le la patient_routes.py
"""
# adăugare importuri și blueprint pentru a rezolva erori de nume nedeterminate
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models.pregnancy import PregnancyWeekInfo, PregnancyCalendarTask, DoctorUnavailability, Prescription
from app.models.patient import Patient
from app.models.medication import Medication
from app.models.message import Notification
from app.forms.pregnancy_forms import (
    PregnancyCalendarTaskForm,
    DoctorUnavailabilityForm,
    PrescriptionForm,
    MarkTaskCompleteForm
)

# folosim același prefix ca `patient_routes` pentru a păstra consistența
bp = Blueprint('patient', __name__, url_prefix='/patient')
# ===== PREGNANCY CALENDAR & TASKS =====

@bp.route('/calendar')
@login_required
def pregnancy_calendar():
    """Afișează calendarul de sarcină cu task-urile săptămânale."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    if not patient or not patient.lmp_date:
        flash('Completați mai întâi data ultimei menstruații.', 'warning')
        return redirect(url_for('patient.edit_profile'))
    
    # Calculează săptămâna curentă
    current_week, current_day = patient.calculate_pregnancy_week()
    
    # Obțin task-uri pentru săptămânile curente și viitoare (5 săptămâni)
    upcoming_weeks = range(current_week, min(current_week + 5, 41))
    
    calendar_data = []
    for week in upcoming_weeks:
        week_info = PregnancyWeekInfo.query.filter_by(week_number=week).first()
        
        tasks = PregnancyCalendarTask.query.filter_by(
            patient_id=patient.id,
            week_number=week
        ).all()
        
        calendar_data.append({
            'week': week,
            'info': week_info,
            'tasks': tasks,
            'is_current': week == current_week,
            'is_past': week < current_week
        })
    
    return render_template('patient/pregnancy_calendar.html',
                         patient=patient,
                         current_week=current_week,
                         current_day=current_day,
                         calendar_data=calendar_data)


@bp.route('/tasks')
@login_required
def pregnancy_tasks():
    """Afișează toate task-urile de sarcină ale pacientei."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    
    # Obțin categorii de task-uri
    pending_tasks = PregnancyCalendarTask.get_pending_tasks(patient.id)
    completed_tasks = PregnancyCalendarTask.query.filter_by(
        patient_id=patient.id,
        is_completed=True
    ).order_by(PregnancyCalendarTask.completed_date.desc()).all()
    
    overdue_tasks = [t for t in pending_tasks if t.is_overdue()]
    
    return render_template('patient/pregnancy_tasks.html',
                         patient=patient,
                         pending_tasks=pending_tasks,
                         completed_tasks=completed_tasks,
                         overdue_tasks=overdue_tasks)


@bp.route('/task/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """Marchează un task ca finalizat."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    task = PregnancyCalendarTask.query.get_or_404(task_id)
    patient = current_user.patient_profile
    
    if task.patient_id != patient.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('patient.pregnancy_tasks'))
    
    form = MarkTaskCompleteForm()
    
    if form.validate_on_submit():
        from app.utils.pregnancy_scheduler import mark_task_completed
        mark_task_completed(task_id, form.completion_notes.data)
        
        # Crează notificare pentru doctor dacă task-ul era recomandat de medic
        if task.recommended_by_doctor and task.doctor_id:
            notification = Notification(
                user_id=task.doctor_id,
                type='task',
                title=f'Task completat: {task.title}',
                message=f'Pacientă {patient.user.first_name} {patient.user.last_name} a marcat task-ul "{task.title}" ca finalizat.',
                related_object_id=task.id,
                related_object_type='PregnancyCalendarTask'
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('Task marcat ca finalizat.', 'success')
        return redirect(url_for('patient.pregnancy_tasks'))
    
    return render_template('patient/task_complete.html', task=task, form=form)


@bp.route('/week-info/<int:week_number>')
@login_required
def week_info(week_number):
    """Afișează informații detaliate pentru o anumită săptămână."""
    if current_user.role != 'patient':
        return redirect(url_for('common.dashboard'))
    
    patient = current_user.patient_profile
    
    if week_number < 1 or week_number > 40:
        flash('Săptămâna introdusă nu este validă.', 'danger')
        return redirect(url_for('patient.pregnancy_calendar'))
    
    week_info_obj = PregnancyWeekInfo.query.filter_by(week_number=week_number).first()
    
    if not week_info_obj:
        flash('Informații pentru această săptămână nu sunt disponibile.', 'warning')
        return redirect(url_for('patient.pregnancy_calendar'))
    
    # Obțin task-urile pentru această săptămână
    tasks = PregnancyCalendarTask.query.filter_by(
        patient_id=patient.id,
        week_number=week_number
    ).all()
    
    return render_template('patient/week_info_detail.html',
                         patient=patient,
                         week_number=week_number,
                         week_info=week_info_obj,
                         tasks=tasks)


# ===== DOCTOR - MANAGING PATIENT AVAILABILITY =====

@bp.route('/availability')
@login_required
def doctor_availability():
    """Gestionarea disponibilității medicului."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))
    
    doctor = current_user.doctor_profile
    
    unavailabilities = DoctorUnavailability.query.filter_by(doctor_id=doctor.id).all()
    form = DoctorUnavailabilityForm()
    
    if form.validate_on_submit():
        unavailability = DoctorUnavailability(
            doctor_id=doctor.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            description=form.description.data,
            is_recurring=form.is_recurring.data,
            recurring_pattern=form.recurring_pattern.data,
            created_by_user_id=current_user.id
        )
        db.session.add(unavailability)
        db.session.commit()
        
        flash('Perioadă de indisponibilitate adăugată.', 'success')
        return redirect(url_for('doctor.doctor_availability'))
    
    return render_template('doctor/availability.html',
                         doctor=doctor,
                         unavailabilities=unavailabilities,
                         form=form)


@bp.route('/availability/<int:unavail_id>/delete', methods=['POST'])
@login_required
def delete_unavailability(unavail_id):
    """Șterge o perioadă de indisponibilitate."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))
    
    unavail = DoctorUnavailability.query.get_or_404(unavail_id)
    doctor = current_user.doctor_profile
    
    if unavail.doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.doctor_availability'))
    
    db.session.delete(unavail)
    db.session.commit()
    
    flash('Perioadă de indisponibilitate ștearsă.', 'success')
    return redirect(url_for('doctor.doctor_availability'))


@bp.route('/patient/<int:patient_id>/task/add', methods=['GET', 'POST'])
@login_required
def add_pregnancy_task(patient_id):
    """Medic adaugă un task de sarcină pentru pacientă."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))
    
    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))
    
    form = PregnancyCalendarTaskForm()
    
    if form.validate_on_submit():
        task = PregnancyCalendarTask(
            patient_id=patient.id,
            title=form.title.data,
            description=form.description.data,
            task_type=form.task_type.data,
            week_number=form.week_number.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            send_reminder=form.send_reminder.data,
            reminder_days_before=form.reminder_days_before.data,
            recommended_by_doctor=True,
            doctor_id=doctor.id,
            auto_generated=False
        )
        db.session.add(task)
        
        # Crează notificare pentru pacientă
        notification = Notification(
            user_id=patient.user_id,
            type='task',
            title=f'Task nou de sarcină: {form.title.data}',
            message=f'Medicul {doctor.user.first_name} {doctor.user.last_name} a adăugat un task: {form.title.data}',
            related_object_id=task.id,
            related_object_type='PregnancyCalendarTask'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Task adăugat cu succes.', 'success')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id))
    
    return render_template('doctor/add_pregnancy_task.html',
                         patient=patient,
                         form=form)


@bp.route('/prescription/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
def add_prescription(patient_id):
    """Medic generează o rețetă pentru pacientă."""
    if current_user.role != 'doctor':
        return redirect(url_for('common.dashboard'))
    
    doctor = current_user.doctor_profile
    patient = Patient.query.get_or_404(patient_id)
    
    if patient.associated_doctor_id != doctor.id:
        flash('Acces neautorizat.', 'danger')
        return redirect(url_for('doctor.patients'))
    
    # Obțin medicamentele pacientei
    medications = Medication.query.filter_by(patient_id=patient.id).all()
    
    form = PrescriptionForm()
    form.medication_id.choices = [(0, '- Selectați medicament -')] + [
        (m.id, f"{m.name} ({m.dosage})") for m in medications
    ]
    
    if form.validate_on_submit():
        medication = Medication.query.get(form.medication_id.data)
        if not medication or medication.patient_id != patient.id:
            flash('Medicament invalid.', 'danger')
            return redirect(url_for('doctor.patient_details', patient_id=patient.id))
        
        # Generează nr. unic de rețetă
        prescription_number = Prescription.generate_prescription_number(doctor.id)
        
        prescription = Prescription(
            doctor_id=doctor.id,
            patient_id=patient.id,
            medication_id=medication.id,
            prescription_number=prescription_number,
            prescription_date=form.prescription_date.data,
            valid_until=form.valid_until.data,
            quantity=form.quantity.data,
            dispensing_instructions=form.dispensing_instructions.data,
            notes=form.notes.data
        )
        db.session.add(prescription)
        
        # Crează notificare pentru pacientă
        notification = Notification(
            user_id=patient.user_id,
            type='document',
            title='Rețetă nouă disponibilă',
            message=f'Rețeta pentru {medication.name} a fost generată. Nr: {prescription_number}',
            related_object_id=prescription.id,
            related_object_type='Prescription'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Rețetă generată: {prescription_number}', 'success')
        return redirect(url_for('doctor.patient_details', patient_id=patient.id))
    
    return render_template('doctor/add_prescription.html',
                         patient=patient,
                         form=form)


@bp.route('/prescription/<int:prescription_id>/pdf')
@login_required
def prescription_pdf(prescription_id):
    """
    Generează PDF-ul rețetei.
    Necesită reportlab library.
    """
    prescription = Prescription.query.get_or_404(prescription_id)
    
    # Verifică drepturi de acces
    if current_user.role == 'doctor':
        if current_user.doctor_profile.id != prescription.doctor_id:
            flash('Acces neautorizat.', 'danger')
            return redirect(url_for('common.dashboard'))
    elif current_user.role == 'patient':
        if current_user.patient_profile.id != prescription.patient_id:
            flash('Acces neautorizat.', 'danger')
            return redirect(url_for('common.dashboard'))
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from datetime import datetime
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=6,
            alignment=1  # Center
        )
        
        elements.append(Paragraph('REȚETĂ MEDICALĂ', title_style))
        elements.append(Spacer(1, 12))
        
        # Doctor info
        doctor_info = f"""
        <b>Medicul prescriptor:</b><br/>
        {prescription.doctor.user.first_name} {prescription.doctor.user.last_name}<br/>
        Specializare: {prescription.doctor.specialization}<br/>
        Clinica: {prescription.doctor.clinic_name}<br/>
        Adresă: {prescription.doctor.clinic_address}<br/>
        Telefon: {prescription.doctor.user.phone}<br/>
        Licență: {prescription.doctor.license_number}
        """
        elements.append(Paragraph(doctor_info, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Patient info
        patient_info = f"""
        <b>Pacient:</b><br/>
        {prescription.patient.user.first_name} {prescription.patient.user.last_name}<br/>
        Email: {prescription.patient.user.email}<br/>
        Telefon: {prescription.patient.user.phone}
        """
        elements.append(Paragraph(patient_info, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Prescription details
        med = prescription.medication
        prescription_details = f"""
        <b>Medicament:</b> {med.name}<br/>
        <b>Doză:</b> {med.dosage}<br/>
        <b>Frecvență:</b> {med.frequency}<br/>
        <b>Durata tratamentului:</b> {med.duration}<br/>
        <b>Cantitate:</b> {prescription.quantity}<br/>
        <b>Instrucțiuni de administrare:</b><br/>
        {med.instructions or 'Conform recomandațiilor medicale'}<br/>
        <b>Instrucțiuni pentru farmacie:</b><br/>
        {prescription.dispensing_instructions or 'Niciuna'}<br/>
        <b>Avertismente:</b><br/>
        {med.warnings or 'Niciun avertisment specific'}
        """
        elements.append(Paragraph(prescription_details, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Metadata
        metadata = f"""
        <b>Numărul rețetei:</b> {prescription.prescription_number}<br/>
        <b>Data emiterii:</b> {prescription.prescription_date.strftime('%d.%m.%Y')}<br/>
        <b>Valabilă până la:</b> {prescription.valid_until.strftime('%d.%m.%Y') if prescription.valid_until else 'NEspecificat'}<br/>
        <b>Status:</b> {'Eliberat' if prescription.is_dispensed else 'În așteptare'}<br/>
        <b>Generat la:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
        """
        elements.append(Paragraph(metadata, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Reteta_{prescription.prescription_number}.pdf'
        )
    
    except ImportError:
        flash('Generarea PDF necesită biblioteca reportlab. Instalați: pip install reportlab', 'danger')
        return redirect(url_for('doctor.patient_details', patient_id=prescription.patient_id))
