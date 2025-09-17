from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table, Text, JSON
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

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True)  # Optional: company domain
    settings = Column(String)  # JSON string for org-specific settings
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    users = relationship('User', back_populates='organization')
    contacts = relationship('Contact', back_populates='organization')
    leads = relationship('Lead', back_populates='organization')
    deals = relationship('Deal', back_populates='organization')
    subscription = relationship('Subscription', back_populates='organization', uselist=False)
    chat_rooms = relationship('ChatRoom')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)  # Remove unique constraint - now unique per org
    password_hash = Column(String, nullable=False)
    avatar_url = Column(String)
    role = Column(String)  # admin, manager, agent within organization
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    organization = relationship('Organization', back_populates='users')
    # Relationships
    deals = relationship('Deal', back_populates='owner')
    leads = relationship('Lead', back_populates='owner')
    activities = relationship('Activity', back_populates='user')
    messages_sent = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    messages_received = relationship('Message', back_populates='recipient', foreign_keys='Message.recipient_id')
    # Chat relationships
    chat_rooms = relationship('ChatRoom', back_populates='created_by')
    chat_participants = relationship('ChatParticipant', back_populates='user')
    chat_messages = relationship('ChatMessage', back_populates='sender')
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
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationships
    owner = relationship('User')
    organization = relationship('Organization', back_populates='contacts')
    leads = relationship('Lead', back_populates='contact')
    deals = relationship('Deal', back_populates='contact')

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    status = Column(String)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Lead Scoring Fields
    score = Column(Integer, default=0)  # 0-100 score
    score_updated_at = Column(DateTime)
    score_factors = Column(String)  # JSON string of scoring factors
    score_confidence = Column(Float, default=0.0)  # 0.0-1.0 confidence
    # Relationships
    contact = relationship('Contact', back_populates='leads')
    owner = relationship('User', back_populates='leads')
    organization = relationship('Organization', back_populates='leads')

class Deal(Base):
    __tablename__ = 'deals'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    value = Column(Float)
    owner_id = Column(Integer, ForeignKey('users.id'))
    stage_id = Column(Integer, ForeignKey('stages.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    reminder_date = Column(DateTime)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    # Post-sale workflow fields
    status = Column(String, default='open')  # open, won, lost
    outcome_reason = Column(String)  # reason for won/lost
    customer_account_id = Column(Integer, ForeignKey('customer_accounts.id'), nullable=True)
    # Relationships
    owner = relationship('User', back_populates='deals')
    stage = relationship('Stage', back_populates='deals')
    contact = relationship('Contact', back_populates='deals')
    organization = relationship('Organization', back_populates='deals')
    activities = relationship('Activity', back_populates='deal')
    attachments = relationship('Attachment', back_populates='deal')
    tags = relationship('Tag', secondary=DealTag, back_populates='deals')
    watchers = relationship('User', secondary=Watcher, back_populates='watched_deals')
    # customer_account = relationship('CustomerAccount', back_populates='deal', uselist=False)

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

# SaaS Subscription Models
class Subscription(Base):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False, unique=True)
    plan = Column(String, nullable=False)  # 'free', 'pro', 'enterprise'
    status = Column(String, nullable=False, default='active')  # 'active', 'cancelled', 'expired', 'trial'
    billing_cycle = Column(String, default='monthly')  # 'monthly', 'yearly'
    user_limit = Column(Integer, nullable=False)
    features = Column(JSON)  # JSON object of enabled features
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    trial_ends_at = Column(DateTime)
    # Billing info
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    # Relationships
    organization = relationship('Organization', back_populates='subscription')

class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # 'free', 'pro', 'enterprise'
    display_name = Column(String, nullable=False)  # 'Free', 'Professional', 'Enterprise'
    description = Column(Text)
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    user_limit = Column(Integer, nullable=False)
    features = Column(JSON)  # JSON array of feature names
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Chat Models
class ChatRoom(Base):
    __tablename__ = 'chat_rooms'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    room_type = Column(String, nullable=False, default='group')  # 'direct', 'group', 'channel'
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship('Organization')
    created_by = relationship('User', back_populates='chat_rooms')
    participants = relationship('ChatParticipant', back_populates='room', cascade='all, delete-orphan')
    messages = relationship('ChatMessage', back_populates='room', cascade='all, delete-orphan')

class ChatParticipant(Base):
    __tablename__ = 'chat_participants'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role = Column(String, default='member')  # 'admin', 'moderator', 'member'
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_read_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    room = relationship('ChatRoom', back_populates='participants')
    user = relationship('User', back_populates='chat_participants')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default='text')  # 'text', 'image', 'file', 'system'
    reply_to_id = Column(Integer, ForeignKey('chat_messages.id'))
    edited_at = Column(DateTime)
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    room = relationship('ChatRoom', back_populates='messages')
    sender = relationship('User', back_populates='chat_messages')
    reply_to = relationship('ChatMessage', remote_side=[id])
    reactions = relationship('ChatReaction', back_populates='message', cascade='all, delete-orphan')

class ChatReaction(Base):
    __tablename__ = 'chat_reactions'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('chat_messages.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    emoji = Column(String, nullable=False)  # Unicode emoji or custom emoji code
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship('ChatMessage', back_populates='reactions')
    user = relationship('User')

class CustomerAccount(Base):
    __tablename__ = 'customer_accounts'
    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    account_name = Column(String, nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    account_type = Column(String, default='standard')  # standard, premium, enterprise
    onboarding_status = Column(String, default='pending')  # pending, in_progress, completed, failed
    success_manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    health_score = Column(Float, default=0.0)  # 0-100
    engagement_level = Column(String, default='low')  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # deal = relationship('Deal', back_populates='customer_account')
    contact = relationship('Contact')
    success_manager = relationship('User') 