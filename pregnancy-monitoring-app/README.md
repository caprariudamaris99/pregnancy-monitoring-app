# Pregnancy Monitoring App

Aplicatie web pentru monitorizarea sarcinii si colaborarea dintre pacienta si medic.

## Link către repository:
```https://github.com/caprariudamaris99/pregnancy-monitoring-app.git```


### 1. Instalare rapidă
```bash
cd pregnancy-monitoring-app
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Setup bază de date
```bash
createdb pregnancy_monitoring
flask db upgrade
```

### 3. Setări variabile de mediu
Creați fișierul `.env`:
```
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/pregnancy_monitoring
```

### 4. Pornire
```bash
python run.py
```

Accesați: `http://localhost:5000`


##  Checklist Configurare

- [ ] Python 3.8+ instalat
- [ ] PostgreSQL rulând
- [ ] Virtual environment creat și activat
- [ ] Dependencies instalate (`pip install -r requirements.txt`)
- [ ] Bază de date creată
- [ ] Migrări executate
- [ ] `.env` fișier configurat
- [ ] Secret key schimbat (production)
- [ ] Folderul `uploads/` are permisiuni



## Stack tehnologic actual
- Backend: Python + Flask
- ORM: SQLAlchemy + Flask-Migrate
- Baza de date: PostgreSQL
- Frontend: Jinja2 templates + Bootstrap + JavaScript
- Autentificare: Flask-Login (session based)

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



