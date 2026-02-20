import argparse
import getpass
import os
import sys

from app import create_app, db
from app.models.user import User, UserRole


def main():
    parser = argparse.ArgumentParser(description="Create a user in the application database.")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--first", default="First", help="First name")
    parser.add_argument("--last", default="Last", help="Last name")
    parser.add_argument("--role", choices=[r.value for r in UserRole], default=UserRole.PATIENT.value, help="User role")
    parser.add_argument("--password", help="Password (will prompt if omitted)")
    parser.add_argument("--env", default=os.getenv('FLASK_ENV', 'development'), help="Flask env/config to use")

    args = parser.parse_args()

    if not args.password:
        pw = getpass.getpass("Password: ")
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            print("Passwords do not match", file=sys.stderr)
            sys.exit(2)
        password = pw
    else:
        password = args.password

    app = create_app(args.env)

    with app.app_context():
        existing = User.query.filter_by(email=args.email).first()
        if existing:
            print(f"User with email {args.email} already exists.")
            sys.exit(1)

        user = User(
            email=args.email,
            first_name=args.first,
            last_name=args.last,
            role=args.role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created user {user.email} with id={user.id} and role={user.role}")


if __name__ == '__main__':
    main()
