from app import db
from datetime import datetime


class Message(db.Model):
    """Model pentru mesagerie pacienta-medic."""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)

    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)

    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_messages'))

    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    conversation = db.relationship('Conversation', backref=db.backref('messages', cascade='all, delete-orphan'))

    attachments = db.relationship('MessageAttachment', backref=db.backref('message'), cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Message {self.sender_id}->{self.recipient_id}>'


class MessageAttachment(db.Model):
    """Model pentru atasamente in mesaje."""
    __tablename__ = 'message_attachments'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    """Model pentru notificari."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    type = db.Column(db.String(50))  # message / appointment / medication_reminder etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)

    related_object_type = db.Column(db.String(50))
    related_object_id = db.Column(db.Integer)

    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifications'))


class NotificationPreference(db.Model):
    """Preferinte notificari per utilizator."""
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    reminder_hour = db.Column(db.Integer, default=9)
    enable_appointment_reminders = db.Column(db.Boolean, default=True)
    enable_medication_reminders = db.Column(db.Boolean, default=True)
    enable_message_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notification_preference', uselist=False))
