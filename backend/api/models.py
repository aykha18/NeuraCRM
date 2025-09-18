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

# Financial Management Models
class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    customer_account_id = Column(Integer, ForeignKey('customer_accounts.id'), nullable=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Invoice Details
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, default='draft')  # draft, sent, paid, overdue, cancelled
    
    # Financial Details
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    balance_due = Column(Float, nullable=False)
    
    # Invoice Content
    description = Column(Text)
    notes = Column(Text)
    terms_conditions = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)
    paid_at = Column(DateTime)
    
    # Relationships
    deal = relationship('Deal')
    customer_account = relationship('CustomerAccount')
    organization = relationship('Organization')
    creator = relationship('User')
    payments = relationship('Payment', back_populates='invoice')
    revenue_entries = relationship('Revenue', back_populates='invoice')

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Payment Details
    payment_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String, nullable=False)  # credit_card, bank_transfer, check, cash, other
    payment_reference = Column(String)  # transaction ID, check number, etc.
    
    # Status and Notes
    status = Column(String, default='pending')  # pending, completed, failed, refunded
    notes = Column(Text)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship('Invoice', back_populates='payments')
    organization = relationship('Organization')
    creator = relationship('User')

class Revenue(Base):
    __tablename__ = 'revenue'
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Revenue Details
    amount = Column(Float, nullable=False)
    recognition_date = Column(DateTime, default=datetime.utcnow)
    recognition_type = Column(String, default='immediate')  # immediate, monthly, quarterly, annually
    recognition_period = Column(String)  # 2024-01, Q1-2024, 2024, etc.
    
    # Revenue Classification
    revenue_type = Column(String, default='product')  # product, service, subscription, support
    revenue_category = Column(String)  # sales, upsell, renewal, etc.
    
    # Status
    status = Column(String, default='recognized')  # recognized, deferred, adjusted, reversed
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship('Invoice', back_populates='revenue_entries')
    deal = relationship('Deal')
    organization = relationship('Organization')

class FinancialReport(Base):
    __tablename__ = 'financial_reports'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Report Details
    report_type = Column(String, nullable=False)  # monthly, quarterly, annual, custom
    report_period = Column(String, nullable=False)  # 2024-01, Q1-2024, 2024, etc.
    report_name = Column(String, nullable=False)
    
    # Financial Data (JSON)
    revenue_data = Column(JSON)  # Revenue breakdown by category, period, etc.
    payment_data = Column(JSON)  # Payment metrics, collection rates, etc.
    invoice_data = Column(JSON)  # Invoice metrics, aging, etc.
    kpi_data = Column(JSON)  # Key performance indicators
    
    # Report Status
    status = Column(String, default='generated')  # generated, reviewed, approved, archived
    generated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    generator = relationship('User')

# Customer Support Models
class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True)
    ticket_number = Column(String, unique=True, nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Ticket Details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, default='medium')  # low, medium, high, urgent, critical
    status = Column(String, default='open')  # open, in_progress, pending_customer, resolved, closed, cancelled
    category = Column(String, nullable=False)  # technical, billing, feature_request, bug_report, general
    subcategory = Column(String)  # login_issue, payment_problem, etc.
    
    # Customer Information
    customer_account_id = Column(Integer, ForeignKey('customer_accounts.id'), nullable=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    customer_email = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    
    # Assignment and SLA
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime)
    sla_deadline = Column(DateTime)
    first_response_at = Column(DateTime)
    resolution_deadline = Column(DateTime)
    
    # Resolution
    resolution = Column(Text)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_at = Column(DateTime)
    escalated_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    escalation_reason = Column(String)
    
    # Customer Satisfaction
    satisfaction_rating = Column(Integer)  # 1-5 scale
    satisfaction_feedback = Column(Text)
    satisfaction_survey_sent = Column(Boolean, default=False)
    satisfaction_survey_sent_at = Column(DateTime)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # Support agent who created
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    organization = relationship('Organization')
    customer_account = relationship('CustomerAccount')
    contact = relationship('Contact')
    assigned_to = relationship('User', foreign_keys=[assigned_to_id])
    resolved_by = relationship('User', foreign_keys=[resolved_by_id])
    escalated_to = relationship('User', foreign_keys=[escalated_to_id])
    creator = relationship('User', foreign_keys=[created_by])
    comments = relationship('SupportComment', back_populates='ticket', cascade='all, delete-orphan')
    attachments = relationship('SupportAttachment', back_populates='ticket', cascade='all, delete-orphan')

class SupportComment(Base):
    __tablename__ = 'support_comments'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Null for customer comments
    author_name = Column(String, nullable=False)  # Support agent name or customer name
    author_email = Column(String, nullable=False)  # Support agent email or customer email
    author_type = Column(String, default='agent')  # agent, customer, system
    
    # Comment Content
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes not visible to customer
    comment_type = Column(String, default='comment')  # comment, status_change, assignment, escalation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship('SupportTicket', back_populates='comments')
    author = relationship('User')

class SupportAttachment(Base):
    __tablename__ = 'support_attachments'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    comment_id = Column(Integer, ForeignKey('support_comments.id'), nullable=True)
    
    # File Details
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Metadata
    uploaded_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship('SupportTicket', back_populates='attachments')
    comment = relationship('SupportComment')
    uploader = relationship('User')

class KnowledgeBaseArticle(Base):
    __tablename__ = 'knowledge_base_articles'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Article Details
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    
    # Categorization
    category = Column(String, nullable=False)  # getting_started, troubleshooting, billing, features
    subcategory = Column(String)
    tags = Column(JSON)  # Array of tags for better searchability
    
    # Status and Visibility
    status = Column(String, default='draft')  # draft, published, archived
    visibility = Column(String, default='public')  # public, internal, customer_only
    featured = Column(Boolean, default=False)
    
    # SEO and Analytics
    meta_description = Column(String)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # Workflow
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approved_at = Column(DateTime)
    last_reviewed_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Relationships
    organization = relationship('Organization')
    author = relationship('User', foreign_keys=[author_id])
    reviewer = relationship('User', foreign_keys=[reviewer_id])

class SupportSLA(Base):
    __tablename__ = 'support_slas'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # SLA Configuration
    name = Column(String, nullable=False)  # Standard, Premium, Enterprise
    priority = Column(String, nullable=False)  # low, medium, high, urgent, critical
    category = Column(String, nullable=True)  # Optional category-specific SLA
    
    # Response Times (in hours)
    first_response_time = Column(Integer, nullable=False)  # Hours to first response
    resolution_time = Column(Integer, nullable=False)  # Hours to resolution
    
    # Business Hours
    business_hours_only = Column(Boolean, default=True)
    business_hours_start = Column(String, default='09:00')  # HH:MM format
    business_hours_end = Column(String, default='17:00')  # HH:MM format
    business_days = Column(JSON, default=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
    
    # Escalation Rules
    auto_escalate = Column(Boolean, default=True)
    escalation_time = Column(Integer)  # Hours before escalation
    escalation_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    escalation_user = relationship('User')

class CustomerSatisfactionSurvey(Base):
    __tablename__ = 'customer_satisfaction_surveys'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Survey Details
    survey_type = Column(String, default='post_resolution')  # post_resolution, periodic, onboarding
    rating = Column(Integer, nullable=False)  # 1-5 scale
    nps_score = Column(Integer)  # Net Promoter Score (-100 to 100)
    
    # Survey Responses
    overall_satisfaction = Column(Integer)  # 1-5 scale
    response_time_rating = Column(Integer)  # 1-5 scale
    resolution_quality_rating = Column(Integer)  # 1-5 scale
    agent_knowledge_rating = Column(Integer)  # 1-5 scale
    communication_rating = Column(Integer)  # 1-5 scale
    
    # Open-ended Feedback
    what_went_well = Column(Text)
    what_could_improve = Column(Text)
    additional_comments = Column(Text)
    
    # Follow-up Actions
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    follow_up_assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)
    customer_email = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    
    # Relationships
    ticket = relationship('SupportTicket')
    organization = relationship('Organization')
    follow_up_assignee = relationship('User')

class SupportAnalytics(Base):
    __tablename__ = 'support_analytics'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Time Period
    period_type = Column(String, nullable=False)  # daily, weekly, monthly, quarterly, yearly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Ticket Metrics
    total_tickets = Column(Integer, default=0)
    open_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    closed_tickets = Column(Integer, default=0)
    
    # Response Time Metrics
    avg_first_response_time = Column(Float, default=0.0)  # Hours
    avg_resolution_time = Column(Float, default=0.0)  # Hours
    sla_breach_count = Column(Integer, default=0)
    sla_compliance_rate = Column(Float, default=0.0)  # Percentage
    
    # Customer Satisfaction
    avg_satisfaction_rating = Column(Float, default=0.0)
    nps_score = Column(Float, default=0.0)
    survey_response_rate = Column(Float, default=0.0)
    
    # Agent Performance
    tickets_per_agent = Column(JSON)  # Agent ID -> ticket count
    resolution_rate_per_agent = Column(JSON)  # Agent ID -> resolution rate
    
    # Category Breakdown
    tickets_by_category = Column(JSON)  # Category -> count
    tickets_by_priority = Column(JSON)  # Priority -> count
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization') 