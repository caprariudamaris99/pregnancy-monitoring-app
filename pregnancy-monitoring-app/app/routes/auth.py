from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.forms.auth_forms import RegistrationForm, LoginForm, UpdateProfileForm
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Înregistrare utilizator."""
    if current_user.is_authenticated:
        return redirect(url_for('common.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=request.args.get('role', UserRole.PATIENT.value),
            data_consent=form.data_consent.data,
            consent_date=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Crează profil corespunzător rolului
        if user.role == UserRole.PATIENT.value:
            patient = Patient(user_id=user.id)
            db.session.add(patient)
        elif user.role == UserRole.DOCTOR.value:
            doctor = Doctor(user_id=user.id, specialization='Generalist')
            db.session.add(doctor)
        
        db.session.commit()
        
        flash('Înregistrare reușită! Vă puteți autentifica acum.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Autentificare utilizator."""
    if current_user.is_authenticated:
        return redirect(url_for('common.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Email sau parolă invalide.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Contul dumneavoastră a fost dezactivat.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=False)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        flash(f'Bine ați venit, {user.first_name}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('common.dashboard'))
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    """Deautentificare utilizator."""
    logout_user()
    flash('Deautentificare reușită.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """Gestionare profil utilizator."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Profil actualizat cu succes.', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
    
    return render_template('auth/profile.html', form=form)
