from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length

class DoctorProfileForm(FlaskForm):
    """Formular pentru profil medic."""
    specialization = StringField('Specializare', validators=[DataRequired(), Length(min=3, max=100)])
    clinic_name = StringField('Nume clinică', validators=[Optional(), Length(max=150)])
    clinic_address = StringField('Adresă clinică', validators=[Optional(), Length(max=200)])
    license_number = StringField('Licență medic', validators=[Optional(), Length(max=50)])
    degree = StringField('Titlu academic', validators=[Optional(), Length(max=100)])
    work_start_hour = IntegerField('Ora de început (format 24h, ex: 9)', validators=[DataRequired()])
    work_end_hour = IntegerField('Ora de sfârşit (format 24h, ex: 17)', validators=[DataRequired()])
    slot_duration_minutes = IntegerField('Durata slotului (minute)', validators=[DataRequired()])
    submit = SubmitField('Salvare profil medic')


class DoctorScheduleForm(FlaskForm):
    """Formular pentru programul default al medicului."""
    work_start_hour = IntegerField('Ora de inceput (0-23)', validators=[DataRequired()])
    work_end_hour = IntegerField('Ora de sfarsit (0-23)', validators=[DataRequired()])
    slot_duration_minutes = IntegerField('Durata slotului (minute)', validators=[DataRequired()])
    submit = SubmitField('Actualizeaza intervalul')

class DocumentUploadForm(FlaskForm):
    """Formular pentru încărcare documente."""
    document_file = FileField('Selectează fișier',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Tipuri de fișier permise: PDF, JPG, PNG, DOC, DOCX')])
    document_type = SelectField('Tip document',
        choices=[
            ('analiza', 'Analiză'),
            ('ecografie', 'Ecografie'),
            ('rețetă', 'Rețetă'),
            ('recomandare', 'Recomandare'),
            ('altele', 'Altele')
        ],
        validators=[DataRequired()])
    lab_name = StringField('Laborator/Clinică', validators=[Optional(), Length(max=150)])
    document_date = StringField('Data documentului (YYYY-MM-DD)', validators=[Optional()])
    submit = SubmitField('Încărcare')

class MedicationForm(FlaskForm):
    """Formular pentru medicație."""
    name = StringField('Nume medicament', validators=[DataRequired(), Length(max=150)])
    dosage = StringField('Doză', validators=[Optional(), Length(max=100)])
    frequency = StringField('Frecvență', validators=[Optional(), Length(max=100)])
    duration = StringField('Durată', validators=[Optional(), Length(max=100)])
    instructions = TextAreaField('Instrucțiuni', validators=[Optional()])
    warnings = TextAreaField('Atenționări', validators=[Optional()])
    medication_type = SelectField('Tip',
        choices=[('prescribed', 'Prescris'), ('supplement', 'Supliment'), ('otc', 'OTC')],
        validators=[DataRequired()])
    submit = SubmitField('Salvare medicament')

class RecommendationForm(FlaskForm):
    """Formular pentru recomandări medicale."""
    title = StringField('Titlu recomandare', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Descriere', validators=[DataRequired(), Length(min=10)])
    visibility = SelectField('Vizibilitate',
        choices=[('patient', 'Vizibil pentru pacientă'), ('internal', 'Intern (doar medic)')],
        validators=[DataRequired()])
    submit = SubmitField('Salvare recomandare')

class MessageForm(FlaskForm):
    """Formular pentru mesaj."""
    subject = StringField('Subiect', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Mesaj', validators=[DataRequired(), Length(min=5)])
    attachment = FileField('Atașament opțional',
        validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Tipuri permise')])
    submit = SubmitField('Trimite mesaj')
