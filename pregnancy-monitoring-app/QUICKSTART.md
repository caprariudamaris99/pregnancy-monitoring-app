# Pregnancy Monitoring App - Quick Start Guide

## ⚡ Porniți aplicația în 5 minute

### 1. Instalare rapidă
```bash
cd pregnancy-monitoring-app
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Setup bază de date
```bash
# Asigurați-vă că PostgreSQL rulează
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

## 🔐 Conturi Test

### Crea

1. **Pacientă:**
   - Email: `patient@example.com`
   - Parolă: `password123` (min 8 caractere)

2. **Medic:**
   - Email: `doctor@example.com`
   - Parolă: `password123`

## 📋 Checklist Configurare

- [ ] Python 3.8+ instalat
- [ ] PostgreSQL rulând
- [ ] Virtual environment creat și activat
- [ ] Dependencies instalate (`pip install -r requirements.txt`)
- [ ] Bază de date creată
- [ ] Migrări executate
- [ ] `.env` fișier configurat
- [ ] Secret key schimbat (production)
- [ ] Folderul `uploads/` are permisiuni

## 🧪 Teste Rapide

```bash
# Test import models
python -c "from app import db; from app.models.user import User; print('Models OK')"

# Test database connection
flask shell
>>> from app import db
>>> db.engine.execute('SELECT 1')
# Should return (1,)

# Reset database (development only)
flask db downgrade
flask db upgrade
```

## 📚 Resurse

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🆘 Ajutor Rapid

**Erori comune:**

```
ModuleNotFoundError: No module named 'flask'
→ Rulați: pip install -r requirements.txt

Psycopg2 error: could not connect to server
→ Asigurați-vă că PostgreSQL rulează

SQLALCHEMY_DATABASE_URI not configured
→ Setați DATABASE_URL în .env
```

## ✨ Următorii pași

1. Explorați dashboard-ul
2. Creați conturi test
3. Completați profiluri medicale
4. Adăugați măsurători și simptome
5. Testați mesageria
6. Verificați exporturile

---

**Happy coding! 🎉**
