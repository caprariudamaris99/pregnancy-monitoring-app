from datetime import datetime

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.message import Notification
from app.utils.ai_assistant import chat_with_openai

bp = Blueprint('common', __name__)


@bp.route('/')
def index():
    """Pagina principala."""
    if current_user.is_authenticated:
        return redirect(url_for('common.dashboard'))
    return render_template('index.html')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - redirectioneaza pe baza rolului."""
    if current_user.role == 'patient':
        return redirect(url_for('patient.dashboard'))
    if current_user.role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    if current_user.role == 'admin':
        return redirect(url_for('common.admin_dashboard'))
    return render_template('dashboard.html')


@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Dashboard admin."""
    if current_user.role != 'admin':
        return redirect(url_for('common.dashboard'))
    return render_template('admin/dashboard.html')


@bp.route('/notifications')
@login_required
def notifications():
    """Lista notificarilor utilizatorului curent."""
    items = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=items)


@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notif = Notification.query.get_or_404(notification_id)
    if notif.user_id != current_user.id:
        return redirect(url_for('common.notifications'))

    if not notif.is_read:
        notif.is_read = True
        notif.read_at = datetime.utcnow()

    if notif.type == 'appointment_rejected' and notif.related_object_type == 'Appointment' and notif.related_object_id:
        from app.models.appointment import Appointment

        appointment = Appointment.query.get(notif.related_object_id)
        if appointment and appointment.patient and appointment.patient.user_id == current_user.id:
            db.session.delete(appointment)

    db.session.commit()
    return redirect(url_for('common.notifications'))


@bp.route('/ai-assistant/chat', methods=['POST'])
@login_required
def ai_assistant_chat():
    """Chat AI contextual pentru pacienta autentificata."""
    if current_user.role != 'patient':
        return jsonify({'error': 'Asistentul AI este disponibil doar pentru conturile de pacienta.'}), 403

    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or '').strip()
    conversation = payload.get('conversation') or []
    if not user_message:
        return jsonify({'error': 'Mesajul este gol.'}), 400

    try:
        answer = chat_with_openai(current_user, user_message, conversation)
    except RuntimeError as exc:
        current_app.logger.warning('AI assistant error: %s', exc)
        return jsonify({'error': str(exc)}), 503
    except Exception as exc:
        current_app.logger.exception('Unexpected AI assistant error')
        return jsonify({'error': f'Eroare neasteptata: {exc}'}), 500

    return jsonify({
        'reply': answer,
        'timestamp': datetime.utcnow().strftime('%d.%m.%Y %H:%M'),
    })


@bp.route('/privacy')
def privacy():
    """Politica de confidentialitate - GDPR."""
    return render_template('privacy.html')


@bp.route('/terms')
def terms():
    """Termeni si conditii."""
    return render_template('terms.html')
