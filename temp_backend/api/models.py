from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables
DealTag = Table(
    'deal_tag', Base.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)
Watcher = Table(
    'watcher', Base.metadata,
    Column('deal_id', Integer, ForeignKey('deals.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String)
    role = Column(String)
    created_at = Column(DateTime)
    # Relationships
    deals = relationship('Deal', back_populates='owner')
    leads = relationship('Lead', back_populates='owner')
    activities = relationship('Activity', back_populates='user')
    messages_sent = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    messages_received = relationship('Message', back_populates='recipient', foreign_keys='Message.recipient_id')
    attachments = relationship('Attachment', back_populates='uploader')
    watched_deals = relationship('Deal', secondary=Watcher, back_populates='watchers')

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    # Relationships
    owner = relationship('User')
    leads = relationship('Lead', back_populates='contact')
    deals = relationship('Deal', back_populates='contact')

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String)
    source = Column(String)
    created_at = Column(DateTime)
    # Lead Scoring Fields
    score = Column(Integer, default=0)  # 0-100 score
    score_updated_at = Column(DateTime)
    score_factors = Column(String)  # JSON string of scoring factors
    score_confidence = Column(Float, default=0.0)  # 0.0-1.0 confidence
    # Relationships
    contact = relationship('Contact', back_populates='leads')
    owner = relationship('User', back_populates='leads')

class Deal(Base):
    __tablename__ = 'deals'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    value = Column(Float)
    owner_id = Column(Integer, ForeignKey('users.id'))
    stage_id = Column(Integer, ForeignKey('stages.id'))
    description = Column(String)
    created_at = Column(DateTime)
    closed_at = Column(DateTime)
    reminder_date = Column(DateTime)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    # Relationships
    owner = relationship('User', back_populates='deals')
    stage = relationship('Stage', back_populates='deals')
    contact = relationship('Contact', back_populates='deals')
    activities = relationship('Activity', back_populates='deal')
    attachments = relationship('Attachment', back_populates='deal')
    tags = relationship('Tag', secondary=DealTag, back_populates='deals')
    watchers = relationship('User', secondary=Watcher, back_populates='watched_deals')

class Stage(Base):
    __tablename__ = 'stages'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    order = Column(Integer)
    wip_limit = Column(Integer)
    # Relationships
    deals = relationship('Deal', back_populates='stage')

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    type = Column(String)
    message = Column(String)
    timestamp = Column(DateTime)
    # Relationships
    deal = relationship('Deal', back_populates='activities')
    user = relationship('User', back_populates='activities')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String)
    channel_id = Column(Integer, ForeignKey('channels.id'))
    recipient_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    read = Column(Boolean, default=False)
    # Relationships
    sender = relationship('User', back_populates='messages_sent', foreign_keys=[sender_id])
    recipient = relationship('User', back_populates='messages_received', foreign_keys=[recipient_id])
    channel = relationship('Channel', back_populates='messages')
    attachments = relationship('Attachment', back_populates='message')

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_group = Column(Boolean, default=True)
    created_at = Column(DateTime)
    # Relationships
    messages = relationship('Message', back_populates='channel')

class Attachment(Base):
    __tablename__ = 'attachments'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    url = Column(String)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    deal_id = Column(Integer, ForeignKey('deals.id'))
    message_id = Column(Integer, ForeignKey('messages.id'))
    uploaded_at = Column(DateTime)
    # Relationships
    uploader = relationship('User', back_populates='attachments')
    deal = relationship('Deal', back_populates='attachments')
    message = relationship('Message', back_populates='attachments')

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    color = Column(String)
    # Relationships
    deals = relationship('Deal', secondary=DealTag, back_populates='tags')

class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)  # HTML content
    category = Column(String)  # welcome, follow_up, reminder, etc.
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    # Relationships
    creator = relationship('User')

class EmailCampaign(Base):
    __tablename__ = 'email_campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey('email_templates.id'))
    subject_override = Column(String)  # Optional override of template subject
    body_override = Column(String)  # Optional override of template body
    target_type = Column(String)  # leads, contacts, deals, custom
    target_ids = Column(String)  # JSON array of target IDs
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    status = Column(String, default='draft')  # draft, scheduled, sending, completed, paused
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    template = relationship('EmailTemplate')
    creator = relationship('User')
    logs = relationship('EmailLog', back_populates='campaign')

class EmailLog(Base):
    __tablename__ = 'email_logs'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('email_campaigns.id'))
    recipient_type = Column(String)  # lead, contact, deal
    recipient_id = Column(Integer)
    recipient_email = Column(String, nullable=False)
    recipient_name = Column(String)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)  # Final personalized content
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='sent')  # sent, delivered, opened, clicked, bounced, failed
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    error_message = Column(String)
    # Relationships
    campaign = relationship('EmailCampaign', back_populates='logs') 