# Pregnancy Monitoring App

Aplicatie web pentru monitorizarea sarcinii si colaborarea dintre pacienta si medic.

## Stack tehnologic actual
- Backend: Python + Flask
- ORM: SQLAlchemy + Flask-Migrate
- Baza de date: PostgreSQL
- Frontend: Jinja2 templates + Bootstrap + JavaScript
- Autentificare: Flask-Login (session based)

## Rulare locala
bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python run.py

Aplicatia ruleaza la `http://localhost:5000`

### Functionalitati implementate

### Pacienta
- inregistrare, autentificare, profil medical
- urmarire sarcina (saptamana curenta + informatii pe saptamani)
- inregistrare parametri vitali (greutate, tensiune, glicemie)
- raportare simptome
- incarcare si descarcare documente medicale
- programari pe sloturi disponibile
- mesagerie cu medicul
- notificari in aplicatie (programari/medicatie/mesaje)

### Medic
- gestionare profil profesional si program de lucru
- gestionare exceptii de disponibilitate
- vizualizare paciente asociate
- confirmare/respingere programari
- recomandari medicale
- mesagerie cu pacientele



