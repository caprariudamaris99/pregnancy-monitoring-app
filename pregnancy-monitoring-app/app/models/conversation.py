from app import db
from datetime import datetime


class Conversation(db.Model):
    """Optional conversation/thread grouping for messages."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255))
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ConversationParticipant(db.Model):
    """Associates users to conversations (for permission/unread tracking)."""
    __tablename__ = 'conversation_participants'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_muted = db.Column(db.Boolean, default=False)

    conversation = db.relationship('Conversation', backref=db.backref('participants', cascade='all, delete-orphan'))
    user = db.relationship('User')
