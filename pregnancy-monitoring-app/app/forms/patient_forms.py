from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FloatField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional


class PatientProfileForm(FlaskForm):
    """Formular pentru profil pacienta."""
    lmp_date = DateField("Data Ultimei Menstruatii (DUM)", validators=[DataRequired()])
    pregnancy_type = SelectField(
        "Tip sarcina",
        choices=[("single", "Unicat"), ("multiple", "Multipla")],
        validators=[DataRequired()],
    )
    blood_type = SelectField(
        "Grupa sanguina",
        choices=[("O", "O"), ("A", "A"), ("B", "B"), ("AB", "AB")],
        validators=[Optional()],
    )
    rh_factor = SelectField(
        "Factor RH",
        choices=[("+", "Pozitiv"), ("-", "Negativ")],
        validators=[Optional()],
    )
    allergies = TextAreaField("Alergii", validators=[Optional(), Length(max=500)])
    chronic_conditions = TextAreaField(
        "Afectiuni cronice", validators=[Optional(), Length(max=500)]
    )
    permanent_medication = TextAreaField(
        "Medicatie permanenta", validators=[Optional(), Length(max=500)]
    )
    surgical_history = TextAreaField(
        "Istoricul interventiilor chirurgicale", validators=[Optional(), Length(max=500)]
    )
    reminder_hour = IntegerField("Ora reminder notificari (0-23)", validators=[Optional()])
    submit = SubmitField("Salvare profil medical")


class VitalSignForm(FlaskForm):
    """Formular pentru parametri vitali."""
    weight_kg = FloatField("Greutate (kg)", validators=[Optional()])
    systolic_bp = IntegerField("Tensiune sistola", validators=[Optional()])
    diastolic_bp = IntegerField("Tensiune diastola", validators=[Optional()])
    blood_glucose = FloatField("Glicemie (mg/dL)", validators=[Optional()])
    notes = TextAreaField("Simptome", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Inregistrare parametri")


class SymptomForm(FlaskForm):
    """Formular pentru raportare simptome."""
    symptom_type = SelectField(
        "Tip simptom",
        choices=[
            ("nausea", "Greata"),
            ("swelling", "Edeme"),
            ("pain", "Durere"),
            ("sleep_issues", "Probleme de somn"),
            ("mood", "Probleme de dispozitie"),
            ("fetal_movement", "Miscari fetale"),
            ("other", "Alte simptome"),
        ],
        validators=[DataRequired()],
    )
    other_symptom = StringField("Descrie altul", validators=[Optional(), Length(max=100)])
    intensity = IntegerField("Intensitate (1-10)", validators=[DataRequired()])
    observations = TextAreaField("Observatii", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Raporta simptom")


class AppointmentSlotSelectionForm(FlaskForm):
    """Formular pentru selectarea unui slot de programare."""
    slot_start = HiddenField("Inceput slot", validators=[DataRequired()])
    slot_end = HiddenField("Sfarsit slot", validators=[DataRequired()])
    notes = TextAreaField("Note (optional)", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Solicita programare")


class SelectDoctorAndDateForm(FlaskForm):
    """Formular pentru selectarea medicului si datei de programare."""
    doctor_id = SelectField("Selectati medicul", coerce=int, validators=[DataRequired()])
    appointment_date = DateField("Data programarii", validators=[DataRequired()])
    submit = SubmitField("Vizualizare sloturi disponibile")


class DoctorSelectionForm(FlaskForm):
    """Formular pentru alegerea medicului asociat."""
    doctor_id = SelectField("Alegeti medicul", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Salveaza medic")
