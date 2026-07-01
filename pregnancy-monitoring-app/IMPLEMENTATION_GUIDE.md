# IMPLEMENTATION GUIDE - Pregnancy Monitoring System 

## 📋 Pre-Requirements

- **Python 3.8+** installed
- **PostgreSQL 12+** installed and running
- **Git** installed 
- **pip** (Python package manager)
- **Virtual environment** tool (`venv` or `virtualenv`)


## STEP-BY-STEP INSTALLATION

### PHASE 1: Environment Setup (15 min)

#### 1.1 Create and activate virtual environment
```bash
# Navigate to project directory
cd c:\Users\capra\OneDrive\Desktop\Scoala\Licenta\pregnancy-monitoring-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 1.2 Install dependencies
```bash
pip install -r requirements.txt

# Optional: For PDF export functionality
pip install reportlab

# Optional: For background task scheduling
pip install APScheduler
```

#### 1.3 Configure environment variables
```bash
# Copy example to .env
copy .env.example .env  # On Windows
# OR
cp .env.example .env    # On macOS/Linux

# Edit .env with your settings
```

**Edit `./.env` file:**
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://postgres:password@localhost:5432/pregnancy_monitoring
DEBUG=True
TESTING=False
```

---

### PHASE 2: Database Setup (20 min)

#### 2.1 Create PostgreSQL database
```bash
# Using psql command line
psql -U postgres

# Inside psql prompt:
CREATE DATABASE pregnancy_monitoring;
CREATE USER pregnancy_app WITH PASSWORD 'secure_password_here';
ALTER ROLE pregnancy_app SET client_encoding TO 'utf8';
ALTER ROLE pregnancy_app SET default_transaction_isolation TO 'read committed';
ALTER ROLE pregnancy_app SET default_transaction_deferrable TO on;
ALTER ROLE pregnancy_app SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pregnancy_monitoring TO pregnancy_app;
\q
```

**OR use GUI tool (pgAdmin):**
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `pregnancy_monitoring`
4. Owner: `pregnancy_app` (or your user)

#### 2.2 Initialize Flask-Migrate
```bash
# Create migrations folder
flask db init

# Generate initial migration from models
flask db migrate -m "Initial schema with all 17 models"

# Apply migration to database
flask db upgrade
```

#### 2.3 Seed pregnancy week information
```bash
# Enter Flask shell
flask shell

# Run seeding function
>>> from app.utils.pregnancy_scheduler import seed_pregnancy_week_info
>>> seed_pregnancy_week_info()
# Should output: True

# Exit flask shell
>>> exit()
```

**Verification in database:**
```sql
SELECT COUNT(*) FROM pregnancy_week_info;
-- Should return: 40 (one for each pregnancy week)
```
### PHASE 3: Test Application (10 min)

#### 3.1 Start development server
```bash
python run.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

#### 3.2 Access application
Open browser and go to: **http://localhost:5000**

You should see the home page with login/register options.

#### 3.3 Create test accounts
```
--- PATIENT TEST ACCOUNT ---
Email: patient@test.com
Password: TestPass123!
Role: Patient (select at registration)

--- DOCTOR TEST ACCOUNT ---
Email: doctor@test.com
Password: TestPass456!
Role: Doctor (select at registration)
```


## 🔧 TROUBLESHOOTING

### Issue 1: Database connection error
```
Error: could not connect to server: Connection refused
```
**Solution:**
```bash
# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Start PostgreSQL if stopped
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Issue 2: ModuleNotFoundError: No module named 'app'
```
Solution: Make sure you're in project root directory
cd c:\Users\capra\OneDrive\Desktop\Scoala\Licenta\pregnancy-monitoring-app
```

### Issue 3: SQLAlchemy import errors
```bash
# Reinstall packages
pip uninstall -y SQLAlchemy Flask-SQLAlchemy
pip install SQLAlchemy==2.0.19 Flask-SQLAlchemy==3.0.5
```

### Issue 4: PDF export not working
```
Error: ModuleNotFoundError: No module named 'reportlab'
Solution:
pip install reportlab
```

### Issue 5: Port 5000 already in use
```bash
# Use different port
python run.py --port 5001
# OR find and kill process using port 5000
# Windows: netstat -ano | findstr :5000
# macOS/Linux: lsof -i :5000 | kill -9
```

