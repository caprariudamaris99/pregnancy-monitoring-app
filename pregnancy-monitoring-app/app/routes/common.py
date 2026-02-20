from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.message import Notification

bp = Blueprint('common', __name__)

@bp.route('/')
def index():
    """Pagina principală."""
    if current_user.is_authenticated:
        return redirect(url_for('common.dashboard'))
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - redirecționează pe baza rolului."""
    if current_user.role == 'patient':
        return redirect(url_for('patient.dashboard'))
    elif current_user.role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('common.admin_dashboard'))
    return render_template('dashboard.html')

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Dashboard admin (opțional)."""
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
        from datetime import datetime
        notif.read_at = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('common.notifications'))

@bp.route('/privacy')
def privacy():
    """Politica de confidențialitate - GDPR."""
    return render_template('privacy.html')

@bp.route('/terms')
def terms():
    """Termeni și condiții."""
    return render_template('terms.html')
