from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from app.models.user import User, UserRole

class RegistrationForm(FlaskForm):
    """Formular de înregistrare."""
    first_name = StringField('Prenume', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Nume', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefon', validators=[Length(min=10, max=20)])
    patient_age = IntegerField('Varsta (ani)', validators=[Optional(), NumberRange(min=0, max=120)])
    password = PasswordField('Parolă', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirmare parolă',
        validators=[DataRequired(), EqualTo('password', message='Parolele trebuie să coincidă.')])
    data_consent = BooleanField('Accept termenii și condiții', validators=[DataRequired()])
    submit = SubmitField('Înregistrare')
    
    def validate_email(self, email):
        """Verifică dacă emailul este deja folosit."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email-ul este deja folosit.')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        role = request.args.get('role', UserRole.PATIENT.value)
        if role == UserRole.PATIENT.value and self.patient_age.data is None:
            self.patient_age.errors.append('Varsta este obligatorie pentru o pacientă.')
            return False

        return True

class LoginForm(FlaskForm):
    """Formular de autentificare."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Parolă', validators=[DataRequired()])
    remember_me = BooleanField('Ține-mă minte')
    submit = SubmitField('Autentificare')

class ResetPasswordRequestForm(FlaskForm):
    """Formular pentru cererea de resetare parolă."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitare resetare parolă')

class ResetPasswordForm(FlaskForm):
    """Formular pentru resetarea parolei."""
    password = PasswordField('Parolă nouă', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirmare parolă',
        validators=[DataRequired(), EqualTo('password', message='Parolele trebuie să coincidă.')])
    submit = SubmitField('Resetare parolă')

class UpdateProfileForm(FlaskForm):
    """Formular pentru actualizarea profilului."""
    first_name = StringField('Prenume', validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Nume', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Telefon', validators=[Length(min=10, max=20)])
    age = IntegerField('Varsta (ani)', validators=[Optional(), NumberRange(min=0, max=120)])
    submit = SubmitField('Salvare modificări')
