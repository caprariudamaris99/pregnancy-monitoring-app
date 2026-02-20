from app import db
from datetime import datetime


class ConsentAudit(db.Model):
    """Audit trail for GDPR consent changes."""
    __tablename__ = 'consent_audits'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    previous_value = db.Column(db.Boolean)
    new_value = db.Column(db.Boolean)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason = db.Column(db.String(255))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])
    changed_by = db.relationship('User', foreign_keys=[changed_by_user_id])
