from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.forms.auth_forms import LoginForm, RegistrationForm, UpdateProfileForm
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User, UserRole

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inregistrare utilizator."""
    if current_user.is_authenticated:
        return redirect(url_for('common.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user_role = request.args.get('role', UserRole.PATIENT.value)
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role=user_role,
            data_consent=form.data_consent.data,
            consent_date=datetime.utcnow(),
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        if user.role == UserRole.PATIENT.value:
            db.session.add(Patient(user_id=user.id, age=form.patient_age.data))
        elif user.role == UserRole.DOCTOR.value:
            db.session.add(Doctor(user_id=user.id, specialization='Generalist'))

        db.session.commit()

        login_user(user, remember=False)
        user.last_login = datetime.utcnow()
        db.session.commit()

        if user.role == UserRole.PATIENT.value:
            flash('Cont creat. Completeaza mai intai profilul medical.', 'success')
            return redirect(url_for('patient.edit_profile', onboarding='1'))

        flash('Cont creat. Completeaza profilul contului.', 'success')
        return redirect(url_for('auth.profile'))

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
            flash('Email sau parola invalida.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Contul dumneavoastra a fost dezactivat.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=False)
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash(f'Bine ai venit, {user.first_name}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('common.dashboard'))

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    """Deautentificare utilizator."""
    logout_user()
    flash('Deautentificare reusita.', 'info')
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
        if current_user.role == UserRole.PATIENT.value:
            patient = current_user.patient_profile
            if not patient:
                patient = Patient(user_id=current_user.id)
                db.session.add(patient)
            patient.age = form.age.data
        db.session.commit()
        flash('Profil actualizat cu succes.', 'success')
        return redirect(url_for('auth.profile'))

    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        if current_user.role == UserRole.PATIENT.value:
            patient = current_user.patient_profile
            if patient:
                form.age.data = patient.age

    return render_template('auth/profile.html', form=form)
