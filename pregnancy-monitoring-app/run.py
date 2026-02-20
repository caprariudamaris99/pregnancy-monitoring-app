from app import create_app, db
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Context pentru shell-ul Flask."""
    from app.models.user import User
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    return {'db': db, 'User': User, 'Patient': Patient, 'Doctor': Doctor}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
