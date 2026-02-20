"""
WTForms pentru gestionarea sarcinilor și disponibi medicului.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, NumberRange
from datetime import date


class PregnancyCalendarTaskForm(FlaskForm):
    """Form pentru crearea/editarea task-urilor de sarcină."""
    
    title = StringField('Titlu Task',
                       validators=[DataRequired(), Length(min=5, max=200)])
    
    description = TextAreaField('Descriere',
                               validators=[Optional()])
    
    task_type = SelectField('Tip Task',
                           choices=[
                               ('analysis', 'Analiză de laborator'),
                               ('appointment', 'Întâlnire medicală'),
                               ('measurement', 'Măsurare parametri'),
                               ('document_upload', 'Încărcare document'),
                               ('general_task', 'Task general')
                           ],
                           validators=[DataRequired()])
    
    week_number = IntegerField('Săptămâna de sarcină',
                              validators=[Optional(), NumberRange(min=1, max=40)])
    
    due_date = DateField('Data datorată',
                        validators=[DataRequired()])
    
    priority = SelectField('Prioritate',
                          choices=[
                              ('low', 'Joasă'),
                              ('normal', 'Normală'),
                              ('high', 'Înaltă'),
                              ('urgent', 'Urgentă')
                          ],
                          default='normal')
    
    send_reminder = BooleanField('Trimite reminder')
    
    reminder_days_before = IntegerField('Zile înainte de reminder',
                                       default=3,
                                       validators=[NumberRange(min=1, max=30)])
    
    completion_notes = TextAreaField('Note la completare',
                                    validators=[Optional()])
    
    submit = SubmitField('Salvează Task')


class DoctorUnavailabilityForm(FlaskForm):
    """Form pentru setarea perioadelor de indisponibilitate ale medicului."""
    
    start_date = DateField('Data început',
                          validators=[DataRequired()])
    
    end_date = DateField('Data sfârșit',
                        validators=[DataRequired()])
    
    reason = SelectField('Motivul indisponibilității',
                        choices=[
                            ('vacation', 'Vacanță'),
                            ('conference', 'Conferință'),
                            ('emergency', 'Urgență'),
                            ('other', 'Altul')
                        ],
                        validators=[DataRequired()])
    
    description = TextAreaField('Descriere detaliat (opțional)',
                               validators=[Optional(), Length(max=500)])
    
    is_recurring = BooleanField('Aceasta este o perioadă recurentă?')
    
    recurring_pattern = SelectField('Model recurență',
                                   choices=[
                                       ('yearly', 'Anual'),
                                       ('monthly', 'Lunar')
                                   ],
                                   validators=[Optional()])
    
    submit = SubmitField('Salvează Indisponibilitate')
    
    def validate_end_date(self, field):
        """Validează că data de sfârșit este după data de început."""
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('Data de sfârșit trebuie să fie după data de început.')


class PrescriptionForm(FlaskForm):
    """Form pentru crearea rețetelor."""
    
    medication_id = SelectField('Medicament',
                               coerce=int,
                               validators=[DataRequired()])
    
    quantity = IntegerField('Cantitate (Nr. cutii/fiole)',
                           validators=[DataRequired(), NumberRange(min=1)])
    
    prescription_date = DateField('Data rețetă',
                                 default=date.today(),
                                 validators=[DataRequired()])
    
    valid_until = DateField('Valabilă până',
                           validators=[Optional()])
    
    dispensing_instructions = TextAreaField('Instrucțiuni pt. farmacie',
                                           validators=[Optional()])
    
    notes = TextAreaField('Note suplimentare',
                         validators=[Optional()])
    
    submit = SubmitField('Generează Rețetă')
    
    def validate_valid_until(self, field):
        """Validează că data de valabilitate este în viitor."""
        if field.data and field.data < self.prescription_date.data:
            raise ValidationError('Rețeta trebuie să fie valabilă după data de emitere.')


class MarkTaskCompleteForm(FlaskForm):
    """Form pentru marcarea unui task ca finalizat."""
    
    completion_notes = TextAreaField('Note la completare',
                                    validators=[Optional(), Length(max=1000)])
    
    submit = SubmitField('Marchează Realizat')
