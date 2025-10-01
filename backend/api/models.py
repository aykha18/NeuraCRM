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
    # Telephony relationships
    pbx_providers = relationship('PBXProvider', back_populates='organization')
    pbx_extensions = relationship('PBXExtension', back_populates='organization')
    calls = relationship('Call', back_populates='organization')
    call_queues = relationship('CallQueue', back_populates='organization')
    call_campaigns = relationship('CallCampaign', back_populates='organization')
    call_analytics = relationship('CallAnalytics', back_populates='organization')
    # Payment relationships
    #payment_methods = relationship('PaymentMethod')
    #payments = relationship('Payment')
    #subscriptions = relationship('Subscription')

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
    # Telephony relationships
    pbx_providers = relationship('PBXProvider', back_populates='creator')
    pbx_extensions = relationship('PBXExtension', back_populates='user')
    call_campaigns = relationship('CallCampaign', back_populates='creator')
    call_activities = relationship('CallActivity', back_populates='user')
    call_queue_members = relationship('CallQueueMember', back_populates='user')
    calls_as_agent = relationship('Call', back_populates='agent', foreign_keys='Call.agent_id')

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
    # Telephony relationships
    calls = relationship('Call', back_populates='contact')
    campaign_calls = relationship('CampaignCall', back_populates='target_contact')
    # Payment relationships
    # payment_methods = relationship('PaymentMethod')
    payments = relationship('Payment',back_populates='contact')
    # subscriptions = relationship('Subscription')

class Lead(Base):
    __tablename__ = 'leads'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    status = Column(String)
    source = Column(String)
    # UTM and attribution fields
    utm_source = Column(String)
    utm_medium = Column(String)
    utm_campaign = Column(String)
    utm_term = Column(String)
    utm_content = Column(String)
    referrer_url = Column(String)
    landing_page_url = Column(String)
    gclid = Column(String)
    fbclid = Column(String)
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
    # Telephony relationships
    calls = relationship('Call', back_populates='lead')
    campaign_calls = relationship('CampaignCall', back_populates='target_lead')

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
    # Telephony relationships
    calls = relationship('Call', back_populates='deal')

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
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)

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
    contact = relationship('Contact',back_populates='payments')


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
    assignment_reason = Column(Text)  # Why was this ticket assigned
    assignment_type = Column(String, default='manual')  # manual, auto, round_robin, skills_based, escalation
    queue_id = Column(Integer, ForeignKey('support_queues.id'), nullable=True)
    sla_deadline = Column(DateTime)
    first_response_at = Column(DateTime)
    resolution_deadline = Column(DateTime)
    
    # Resolution
    resolution = Column(Text)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Closure Workflow
    closure_reason = Column(String)  # resolved, duplicate, not_reproducible, customer_cancelled, etc.
    closure_category = Column(String)  # technical_fix, workaround, user_education, etc.
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    follow_up_notes = Column(Text)
    customer_satisfied = Column(Boolean)  # Customer satisfaction before closure
    internal_notes = Column(Text)  # Internal notes not visible to customer
    
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
    queue = relationship('SupportQueue', back_populates='tickets')
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

# Support Assignment Models
class SupportQueue(Base):
    __tablename__ = 'support_queues'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # e.g., "Technical Support", "Billing", "Tier 2"
    description = Column(Text)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Queue Settings
    auto_assign = Column(Boolean, default=True)
    round_robin = Column(Boolean, default=True)
    max_workload = Column(Integer, default=10)  # Max tickets per agent
    business_hours_only = Column(Boolean, default=False)
    business_hours_start = Column(String, default="09:00")  # HH:MM format
    business_hours_end = Column(String, default="17:00")   # HH:MM format
    timezone = Column(String, default="UTC")
    
    # Priority Routing
    handles_priorities = Column(JSON)  # List of priorities this queue handles
    escalation_queue_id = Column(Integer, ForeignKey('support_queues.id'), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    tickets = relationship('SupportTicket', back_populates='queue')
    escalation_queue = relationship('SupportQueue', remote_side=[id])

class UserSkill(Base):
    __tablename__ = 'user_skills'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    skill_name = Column(String, nullable=False)  # e.g., "technical", "billing", "api_integration"
    skill_level = Column(String, default='intermediate')  # beginner, intermediate, advanced, expert
    category = Column(String)  # technical, product, billing, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User')

class AssignmentAudit(Base):
    __tablename__ = 'assignment_audits'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('support_tickets.id'), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assignment_type = Column(String, nullable=False)  # manual, auto, round_robin, skills_based, escalation
    assignment_reason = Column(Text)
    previous_assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    queue_id = Column(Integer, ForeignKey('support_queues.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship('SupportTicket')
    assigned_to = relationship('User', foreign_keys=[assigned_to_id])
    assigned_by = relationship('User', foreign_keys=[assigned_by_id])
    previous_assigned_to = relationship('User', foreign_keys=[previous_assigned_to_id])
    queue = relationship('SupportQueue')

# Customer Segmentation Models
class CustomerSegment(Base):
    __tablename__ = 'customer_segments'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Segment Details
    name = Column(String, nullable=False)  # e.g., "High-Value Customers", "At-Risk Customers"
    description = Column(Text)
    segment_type = Column(String, default='behavioral')  # behavioral, demographic, transactional, predictive
    
    # Segmentation Criteria (JSON)
    criteria = Column(JSON, nullable=False)  # Rules and conditions for segment membership
    criteria_description = Column(Text)  # Human-readable description of criteria
    
    # Segment Statistics
    customer_count = Column(Integer, default=0)
    total_deal_value = Column(Float, default=0.0)
    avg_deal_value = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # AI-Generated Insights
    insights = Column(JSON)  # AI-generated insights about the segment
    recommendations = Column(JSON)  # AI recommendations for this segment
    risk_score = Column(Float, default=0.0)  # 0-100 risk assessment
    opportunity_score = Column(Float, default=0.0)  # 0-100 opportunity assessment
    
    # Status and Settings
    is_active = Column(Boolean, default=True)
    is_auto_updated = Column(Boolean, default=True)  # Auto-update when criteria change
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    creator = relationship('User')
    segment_members = relationship('CustomerSegmentMember', back_populates='segment', cascade='all, delete-orphan')

class CustomerSegmentMember(Base):
    __tablename__ = 'customer_segment_members'
    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey('customer_segments.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    
    # Membership Details
    membership_score = Column(Float, default=1.0)  # How well they fit the segment (0-1)
    membership_reasons = Column(JSON)  # Reasons why they're in this segment
    added_by_ai = Column(Boolean, default=False)  # Was this membership AI-generated?
    
    # Engagement Metrics for this segment
    segment_engagement_score = Column(Float, default=0.0)  # 0-100
    last_activity_in_segment = Column(DateTime)
    
    # Metadata
    added_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    segment = relationship('CustomerSegment', back_populates='segment_members')
    contact = relationship('Contact')

class SegmentAnalytics(Base):
    __tablename__ = 'segment_analytics'
    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey('customer_segments.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Time Period
    period_type = Column(String, nullable=False)  # daily, weekly, monthly, quarterly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Segment Performance Metrics
    customer_count = Column(Integer, default=0)
    new_members = Column(Integer, default=0)
    lost_members = Column(Integer, default=0)
    
    # Revenue Metrics
    total_revenue = Column(Float, default=0.0)
    avg_revenue_per_customer = Column(Float, default=0.0)
    revenue_growth_rate = Column(Float, default=0.0)
    
    # Engagement Metrics
    avg_engagement_score = Column(Float, default=0.0)
    active_customers = Column(Integer, default=0)
    churn_rate = Column(Float, default=0.0)
    
    # Deal Metrics
    total_deals = Column(Integer, default=0)
    closed_deals = Column(Integer, default=0)
    avg_deal_size = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # AI Insights
    trends = Column(JSON)  # Trending patterns in this segment
    predictions = Column(JSON)  # Future predictions for this segment
    recommendations = Column(JSON)  # Actionable recommendations
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    segment = relationship('CustomerSegment')
    organization = relationship('Organization')

# Advanced Forecasting Models
class ForecastingModel(Base):
    __tablename__ = 'forecasting_models'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    model_type = Column(String, nullable=False)  # 'revenue', 'pipeline', 'customer_growth', 'churn'
    data_source = Column(String, nullable=False)  # 'deals', 'contacts', 'activities'
    model_algorithm = Column(String, nullable=False)  # 'ARIMA', 'Prophet', 'Linear_Regression', 'Exponential_Smoothing'
    model_parameters = Column(JSON)
    training_data_period = Column(String, nullable=False)  # '3_months', '6_months', '12_months', '24_months'
    forecast_horizon = Column(String, nullable=False)  # '1_month', '3_months', '6_months', '12_months'
    accuracy_metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    last_trained = Column(DateTime)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organization = relationship('Organization')
    creator = relationship('User')
    forecasts = relationship('ForecastResult', back_populates='model', cascade='all, delete-orphan')

class ForecastResult(Base):
    __tablename__ = 'forecast_results'
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('forecasting_models.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    forecast_type = Column(String, nullable=False)
    forecast_period = Column(String, nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    forecasted_value = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    actual_value = Column(Float)
    accuracy_score = Column(Float)
    trend_direction = Column(String)  # 'increasing', 'decreasing', 'stable'
    seasonality_factor = Column(Float)
    anomaly_detected = Column(Boolean, default=False)
    forecast_quality_score = Column(Float)
    insights = Column(JSON)
    recommendations = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    model = relationship('ForecastingModel', back_populates='forecasts')
    organization = relationship('Organization')

class ForecastingAnalytics(Base):
    __tablename__ = 'forecasting_analytics'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    analytics_type = Column(String, nullable=False)  # 'model_performance', 'forecast_accuracy', 'trend_analysis'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    total_forecasts = Column(Integer, default=0)
    accurate_forecasts = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    avg_forecast_error = Column(Float, default=0.0)
    best_performing_model = Column(String)
    worst_performing_model = Column(String)
    trend_analysis = Column(JSON)
    seasonality_analysis = Column(JSON)
    anomaly_detection = Column(JSON)
    performance_insights = Column(JSON)
    improvement_recommendations = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    organization = relationship('Organization')

# Telephony Models
class PBXProvider(Base):
    __tablename__ = 'pbx_providers'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Provider Details
    name = Column(String, nullable=False)  # e.g., "Asterisk", "FreePBX", "3CX", "Twilio", "Yeastar"
    provider_type = Column(String, nullable=False)  # 'asterisk', 'freepbx', '3cx', 'twilio', 'yeastar', 'custom'
    display_name = Column(String, nullable=False)
    description = Column(Text)
    
    # Basic Connection Settings
    host = Column(String, nullable=False)  # IP or domain
    port = Column(Integer, default=5060)  # SIP port (5060) or AMI port (8088)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Encrypted
    authentication_name = Column(String)  # Separate auth name (often same as username)
    
    # Advanced Connection Settings
    enable_outbound_proxy = Column(Boolean, default=False)
    outbound_proxy_host = Column(String)
    outbound_proxy_port = Column(Integer, default=5060)
    transport = Column(String, default='UDP')  # UDP, TCP, TLS, DNS-NAPTR
    enable_nat_traversal = Column(Boolean, default=False)
    nat_type = Column(String)  # 'auto', 'force_rport', 'comedia'
    local_network = Column(String)  # Local network CIDR
    
    # Trunk Configuration (Yeastar/Enterprise PBX)
    trunk_type = Column(String, default='register')  # 'register', 'peer', 'user'
    register_interval = Column(Integer, default=3600)  # Registration interval in seconds
    register_timeout = Column(Integer, default=20)  # Registration timeout
    max_retries = Column(Integer, default=5)  # Max registration retries
    
    # SIP Settings
    sip_context = Column(String, default='default')  # SIP context
    caller_id_field = Column(String, default='CallerIDNum')  # Field to extract caller ID
    dialplan_context = Column(String, default='from-internal')  # Context for outbound calls
    from_domain = Column(String)  # From domain for SIP
    to_domain = Column(String)  # To domain for SIP
    
    # DID/DDI Configuration
    did_numbers = Column(Text)  # JSON array of DID numbers
    did_pattern = Column(String)  # DID pattern matching
    did_strip_digits = Column(Integer, default=0)  # Digits to strip from DID
    
    # Caller ID Reformatting
    inbound_caller_id_reformatting = Column(Boolean, default=False)
    outbound_caller_id_reformatting = Column(Boolean, default=False)
    caller_id_prefix = Column(String)  # Prefix to add to caller ID
    caller_id_suffix = Column(String)  # Suffix to add to caller ID
    caller_id_replacement_rules = Column(Text)  # JSON array of replacement rules
    
    # SIP Headers
    custom_sip_headers = Column(Text)  # JSON object of custom SIP headers
    p_asserted_identity = Column(String)  # P-Asserted-Identity header
    remote_party_id = Column(String)  # Remote-Party-ID header
    
    # Codec Settings
    preferred_codecs = Column(Text)  # JSON array of preferred codecs
    codec_negotiation = Column(String, default='negotiate')  # 'negotiate', 'force'
    dtmf_mode = Column(String, default='rfc2833')  # 'rfc2833', 'inband', 'sip_info'
    
    # Quality of Service (QoS)
    enable_qos = Column(Boolean, default=False)
    dscp_value = Column(Integer, default=46)  # DSCP value for QoS
    bandwidth_limit = Column(Integer)  # Bandwidth limit in kbps
    
    # Security Settings
    enable_srtp = Column(Boolean, default=False)
    srtp_mode = Column(String, default='optional')  # 'optional', 'required'
    enable_tls = Column(Boolean, default=False)
    tls_cert_path = Column(String)  # Path to TLS certificate
    tls_key_path = Column(String)  # Path to TLS private key
    tls_ca_path = Column(String)  # Path to TLS CA certificate
    
    # Advanced Settings
    recording_enabled = Column(Boolean, default=True)
    recording_path = Column(String, default='/var/spool/asterisk/monitor')
    transcription_enabled = Column(Boolean, default=False)
    cdr_enabled = Column(Boolean, default=True)
    cdr_path = Column(String, default='/var/log/asterisk/cdr-csv')
    call_forwarding_enabled = Column(Boolean, default=True)
    call_waiting_enabled = Column(Boolean, default=True)
    three_way_calling_enabled = Column(Boolean, default=True)
    
    # Monitoring and Analytics
    enable_call_monitoring = Column(Boolean, default=True)
    enable_call_recording = Column(Boolean, default=False)
    recording_format = Column(String, default='wav')  # 'wav', 'mp3', 'gsm'
    recording_quality = Column(String, default='high')  # 'low', 'medium', 'high'
    
    # Webhook Settings
    webhook_url = Column(String)  # For incoming call notifications
    webhook_secret = Column(String)  # Webhook authentication secret
    webhook_events = Column(Text)  # JSON array of webhook events to subscribe to
    
    # API Integration
    api_endpoint = Column(String)  # API endpoint for provider
    api_key = Column(String)  # For cloud providers like Twilio
    api_secret = Column(String)  # API secret for authentication
    api_version = Column(String, default='v1')  # API version
    
    # Status and Settings
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary PBX for organization
    auto_assign_calls = Column(Boolean, default=True)
    failover_enabled = Column(Boolean, default=False)
    failover_provider_id = Column(Integer, ForeignKey('pbx_providers.id'), nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime)
    last_registration = Column(DateTime)  # Last successful registration
    registration_status = Column(String, default='unknown')  # 'registered', 'failed', 'unknown'
    
    # Relationships
    organization = relationship('Organization')
    creator = relationship('User')
    extensions = relationship('PBXExtension', back_populates='provider', cascade='all, delete-orphan')
    calls = relationship('Call', back_populates='provider')
    call_queues = relationship('CallQueue', back_populates='provider', cascade='all, delete-orphan')

class PBXExtension(Base):
    __tablename__ = 'pbx_extensions'
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey('pbx_providers.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Null for system extensions
    
    # Extension Details
    extension_number = Column(String, nullable=False)  # e.g., "1001", "2001"
    extension_name = Column(String, nullable=False)  # e.g., "John Doe", "Sales Queue"
    extension_type = Column(String, default='user')  # 'user', 'queue', 'ivr', 'conference', 'voicemail'
    
    # Technical Settings
    device_type = Column(String)  # 'sip', 'pjsip', 'iax', 'dahdi'
    device_config = Column(JSON)  # Device-specific configuration
    voicemail_enabled = Column(Boolean, default=True)
    voicemail_password = Column(String)
    
    # Call Handling
    ring_timeout = Column(Integer, default=30)  # Seconds
    max_ring_timeout = Column(Integer, default=60)  # Maximum ring time
    call_forward_enabled = Column(Boolean, default=False)
    call_forward_number = Column(String)
    call_forward_conditions = Column(JSON)  # When to forward (busy, no-answer, etc.)
    
    # Presence and Status
    presence_status = Column(String, default='available')  # available, busy, away, offline
    dnd_enabled = Column(Boolean, default=False)  # Do Not Disturb
    auto_answer = Column(Boolean, default=False)
    
    # Queue Settings (for queue extensions)
    queue_strategy = Column(String, default='ringall')  # ringall, leastrecent, fewestcalls, etc.
    queue_timeout = Column(Integer, default=30)
    queue_retry = Column(Integer, default=5)
    queue_wrapup_time = Column(Integer, default=30)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_registered = Column(Boolean, default=False)  # Registration status with PBX
    last_registered = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    provider = relationship('PBXProvider', back_populates='extensions')
    organization = relationship('Organization')
    user = relationship('User')
    calls = relationship('Call', back_populates='extension')

class Call(Base):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('pbx_providers.id'), nullable=False)
    extension_id = Column(Integer, ForeignKey('pbx_extensions.id'), nullable=True)
    
    # Call Identification
    unique_id = Column(String, unique=True, nullable=False)  # PBX unique call ID
    pbx_call_id = Column(String)  # Additional PBX-specific call identifier
    session_id = Column(String)  # Session identifier for multi-leg calls
    
    # Call Details
    caller_id = Column(String, nullable=False)  # Calling number
    caller_name = Column(String)  # Caller ID name
    called_number = Column(String, nullable=False)  # Called number
    called_name = Column(String)  # Called party name
    
    # Call Direction and Type
    direction = Column(String, nullable=False)  # 'inbound', 'outbound', 'internal'
    call_type = Column(String, default='voice')  # 'voice', 'video', 'conference'
    
    # Contact Association
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    deal_id = Column(Integer, ForeignKey('deals.id'), nullable=True)
    
    # Agent Assignment
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    queue_id = Column(Integer, ForeignKey('call_queues.id'), nullable=True)
    
    # Call Status and Timing
    status = Column(String, nullable=False)  # 'ringing', 'answered', 'busy', 'no-answer', 'failed', 'completed'
    start_time = Column(DateTime, nullable=False)
    answer_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer, default=0)  # Duration in seconds
    talk_time = Column(Integer, default=0)  # Talk time in seconds
    hold_time = Column(Integer, default=0)  # Hold time in seconds
    wait_time = Column(Integer, default=0)  # Wait time in queue
    
    # Call Quality and Recording
    quality_score = Column(Float)  # 0-100 call quality score
    recording_url = Column(String)  # URL to call recording
    recording_duration = Column(Integer)  # Recording duration in seconds
    transcription_url = Column(String)  # URL to transcription
    transcription_text = Column(Text)  # Call transcription
    
    # Call Disposition
    disposition = Column(String)  # 'answered', 'busy', 'no-answer', 'failed', 'abandoned'
    hangup_cause = Column(String)  # Technical hangup cause
    notes = Column(Text)  # Agent notes about the call
    
    # Cost Information (for outbound calls)
    cost = Column(Float, default=0.0)
    cost_currency = Column(String, default='USD')
    
    # Call Data Records
    cdr_data = Column(JSON)  # Complete CDR data from PBX
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    provider = relationship('PBXProvider', back_populates='calls')
    extension = relationship('PBXExtension', back_populates='calls')
    contact = relationship('Contact')
    lead = relationship('Lead')
    deal = relationship('Deal')
    agent = relationship('User')
    queue = relationship('CallQueue')
    call_activities = relationship('CallActivity', back_populates='call', cascade='all, delete-orphan')

class CallActivity(Base):
    __tablename__ = 'call_activities'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Activity Details
    activity_type = Column(String, nullable=False)  # 'answered', 'hold', 'transfer', 'conference', 'mute', 'unmute'
    activity_data = Column(JSON)  # Additional activity-specific data
    
    # Timing
    timestamp = Column(DateTime, nullable=False)
    duration = Column(Integer, default=0)  # Duration of this activity in seconds
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship('Call', back_populates='call_activities')
    user = relationship('User')

class CallQueue(Base):
    __tablename__ = 'call_queues'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('pbx_providers.id'), nullable=False)
    
    # Queue Details
    name = Column(String, nullable=False)  # e.g., "Sales Queue", "Support Queue"
    description = Column(Text)
    queue_number = Column(String, nullable=False)  # Queue extension number
    
    # Queue Strategy
    strategy = Column(String, default='ringall')  # ringall, leastrecent, fewestcalls, etc.
    timeout = Column(Integer, default=30)  # Ring timeout in seconds
    retry = Column(Integer, default=5)  # Number of retries
    wrapup_time = Column(Integer, default=30)  # Wrap-up time in seconds
    max_wait_time = Column(Integer, default=300)  # Maximum wait time in queue
    
    # Queue Settings
    music_on_hold = Column(String, default='default')  # MOH class
    announce_frequency = Column(Integer, default=30)  # Announcement frequency in seconds
    announce_position = Column(Boolean, default=True)  # Announce queue position
    announce_hold_time = Column(Boolean, default=True)  # Announce estimated hold time
    
    # Queue Members
    max_calls_per_agent = Column(Integer, default=1)
    join_empty = Column(Boolean, default=True)  # Join queue when no agents available
    leave_when_empty = Column(Boolean, default=False)  # Leave queue when no callers
    
    # Priority and Routing
    priority = Column(Integer, default=0)  # Queue priority
    skill_based_routing = Column(Boolean, default=False)
    required_skills = Column(JSON)  # Required skills for this queue
    
    # Status
    is_active = Column(Boolean, default=True)
    current_calls = Column(Integer, default=0)  # Current number of calls in queue
    current_agents = Column(Integer, default=0)  # Current number of logged-in agents
    
    # Statistics
    total_calls = Column(Integer, default=0)
    answered_calls = Column(Integer, default=0)
    abandoned_calls = Column(Integer, default=0)
    avg_wait_time = Column(Float, default=0.0)
    avg_talk_time = Column(Float, default=0.0)
    service_level = Column(Float, default=0.0)  # Service level percentage
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    provider = relationship('PBXProvider', back_populates='call_queues')
    queue_members = relationship('CallQueueMember', back_populates='queue', cascade='all, delete-orphan')
    calls = relationship('Call', back_populates='queue')

class CallQueueMember(Base):
    __tablename__ = 'call_queue_members'
    id = Column(Integer, primary_key=True)
    queue_id = Column(Integer, ForeignKey('call_queues.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    extension_id = Column(Integer, ForeignKey('pbx_extensions.id'), nullable=True)
    penalty = Column(Integer, default=0)  # Penalty for this member (lower = higher priority)
    paused = Column(Boolean, default=False)  # Paused from queue
    status = Column(String, default='logged_out')  # logged_in, logged_out, busy, offline
    last_call_time = Column(DateTime)
    total_calls = Column(Integer, default=0)
    answered_calls = Column(Integer, default=0)
    talk_time = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queue = relationship('CallQueue', back_populates='queue_members')
    user = relationship('User')

class CallCampaign(Base):
    __tablename__ = 'call_campaigns'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Campaign Details
    name = Column(String, nullable=False)
    description = Column(Text)
    campaign_type = Column(String, default='outbound')  # 'outbound', 'survey', 'follow_up'
    
    # Target Settings
    target_contacts = Column(JSON)  # List of contact IDs or criteria
    target_leads = Column(JSON)  # List of lead IDs or criteria
    target_segments = Column(JSON)  # List of customer segment IDs
    
    # Campaign Settings
    max_concurrent_calls = Column(Integer, default=5)
    call_timeout = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    retry_interval = Column(Integer, default=3600)  # Seconds between retries
    
    # Scheduling
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    business_hours_only = Column(Boolean, default=True)
    business_hours_start = Column(String, default='09:00')
    business_hours_end = Column(String, default='17:00')
    business_days = Column(JSON, default=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
    timezone = Column(String, default='UTC')
    
    # Call Script and Settings
    script_template = Column(Text)  # Call script template
    recording_enabled = Column(Boolean, default=True)
    transcription_enabled = Column(Boolean, default=False)
    
    # Status
    status = Column(String, default='draft')  # draft, scheduled, running, paused, completed, cancelled
    progress = Column(JSON)  # Campaign progress tracking
    
    # Results
    total_targets = Column(Integer, default=0)
    calls_made = Column(Integer, default=0)
    calls_answered = Column(Integer, default=0)
    calls_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Metadata
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    creator = relationship('User')
    campaign_calls = relationship('CampaignCall', back_populates='campaign', cascade='all, delete-orphan')

class CampaignCall(Base):
    __tablename__ = 'campaign_calls'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('call_campaigns.id'), nullable=False)
    call_id = Column(Integer, ForeignKey('calls.id'), nullable=False)
    
    # Campaign Call Details
    target_contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    target_lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    
    # Attempt Tracking
    attempt_number = Column(Integer, default=1)
    scheduled_time = Column(DateTime)
    actual_call_time = Column(DateTime)
    
    # Results
    outcome = Column(String)  # 'answered', 'no_answer', 'busy', 'failed', 'completed'
    disposition = Column(String)  # Campaign-specific disposition
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship('CallCampaign', back_populates='campaign_calls')
    call = relationship('Call')
    target_contact = relationship('Contact')
    target_lead = relationship('Lead')

class CallAnalytics(Base):
    __tablename__ = 'call_analytics'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Time Period
    period_type = Column(String, nullable=False)  # daily, weekly, monthly, quarterly, yearly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Call Volume Metrics
    total_calls = Column(Integer, default=0)
    inbound_calls = Column(Integer, default=0)
    outbound_calls = Column(Integer, default=0)
    internal_calls = Column(Integer, default=0)
    answered_calls = Column(Integer, default=0)
    missed_calls = Column(Integer, default=0)
    abandoned_calls = Column(Integer, default=0)
    
    # Performance Metrics
    answer_rate = Column(Float, default=0.0)  # Percentage
    abandonment_rate = Column(Float, default=0.0)  # Percentage
    avg_call_duration = Column(Float, default=0.0)  # Seconds
    avg_talk_time = Column(Float, default=0.0)  # Seconds
    avg_wait_time = Column(Float, default=0.0)  # Seconds
    avg_hold_time = Column(Float, default=0.0)  # Seconds
    
    # Queue Metrics
    queue_calls = Column(Integer, default=0)
    queue_answered = Column(Integer, default=0)
    queue_abandoned = Column(Integer, default=0)
    service_level = Column(Float, default=0.0)  # Percentage
    avg_queue_wait = Column(Float, default=0.0)  # Seconds
    
    # Agent Performance
    active_agents = Column(Integer, default=0)
    total_agent_time = Column(Integer, default=0)  # Seconds
    avg_agent_utilization = Column(Float, default=0.0)  # Percentage
    
    # Cost Metrics
    total_cost = Column(Float, default=0.0)
    avg_cost_per_call = Column(Float, default=0.0)
    
    # Quality Metrics
    avg_quality_score = Column(Float, default=0.0)
    recordings_count = Column(Integer, default=0)
    transcriptions_count = Column(Integer, default=0)
    
    # Breakdown by Queue/Agent
    queue_breakdown = Column(JSON)  # Per-queue statistics
    agent_breakdown = Column(JSON)  # Per-agent statistics
    hourly_breakdown = Column(JSON)  # Hour-by-hour statistics
    
    # Trends and Insights
    trends = Column(JSON)  # Trend analysis
    insights = Column(JSON)  # AI-generated insights
    recommendations = Column(JSON)  # Recommendations for improvement
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')

# Company Settings Model
class CompanySettings(Base):
    __tablename__ = 'company_settings'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False, unique=True)
    
    # Company Information
    company_name = Column(String, nullable=False)
    company_mobile = Column(String)
    city = Column(String)
    area = Column(String)
    complete_address = Column(Text)
    trn = Column(String)  # Tax Registration Number
    currency = Column(String, default='AED - UAE Dirham (د.إ)')
    timezone = Column(String, default='Dubai (UAE)')
    
    # Billing Configuration
    trial_date_enabled = Column(Boolean, default=True)
    trial_date_days = Column(Integer, default=3)
    delivery_date_enabled = Column(Boolean, default=True)
    delivery_date_days = Column(Integer, default=3)
    advance_payment_enabled = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    organization = relationship('Organization')
    creator = relationship('User')

class CallRecord(Base):
    """Call records for Retell AI conversational AI calls"""
    __tablename__ = 'call_records'
    id = Column(Integer, primary_key=True)

    # External call identification
    external_call_id = Column(String, nullable=False, unique=True)  # Retell AI call ID
    agent_id = Column(String, nullable=False)  # Retell AI agent ID

    # Call details
    to_number = Column(String, nullable=False)  # Destination number
    from_number = Column(String)  # Source number (optional)

    # Call scenario and context
    scenario = Column(String, nullable=False)  # sales_outbound, customer_support, etc.
    direction = Column(String, default='outbound')  # inbound, outbound
    status = Column(String, default='pending')  # pending, answered, completed, failed

    # Call timing
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # Duration in seconds

    # Call results
    recording_url = Column(String)  # Call recording URL
    transcript = Column(Text)  # Call transcript
    cost = Column(Float, default=0.0)  # Call cost

    # CRM associations
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who initiated

    # Metadata
    call_metadata = Column(JSON)  # Additional call metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship('Lead')
    contact = relationship('Contact')
    user = relationship('User')

# Payment Gateway Models
class PaymentMethod(Base):
    """Customer payment methods stored in Stripe"""
    __tablename__ = 'payment_methods'
    id = Column(Integer, primary_key=True)
    stripe_payment_method_id = Column(String, nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    type = Column(String, nullable=False)  # card, bank_account, etc.
    brand = Column(String)  # visa, mastercard, etc.
    last4 = Column(String)  # last 4 digits
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship('Contact')
    organization = relationship('Organization')

class StripePayment(Base):
    """Stripe payment records for invoices and subscriptions"""
    __tablename__ = 'stripe_payments'
    id = Column(Integer, primary_key=True)
    stripe_payment_intent_id = Column(String, nullable=False, unique=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=True)
    subscription_id = Column(Integer, ForeignKey('stripe_subscriptions.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    amount = Column(Float, nullable=False)  # in cents
    currency = Column(String, default='usd')
    status = Column(String, nullable=False)  # pending, succeeded, failed, canceled
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=True)
    failure_reason = Column(String)
    payment_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship('Invoice')
    subscription = relationship('StripeSubscription')
    customer = relationship('Contact')
    organization = relationship('Organization')
    payment_method = relationship('PaymentMethod')

class StripeSubscriptionPlan(Base):
    """Stripe subscription plans for recurring billing"""
    __tablename__ = 'stripe_subscription_plans'
    id = Column(Integer, primary_key=True)
    stripe_price_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)  # in cents
    currency = Column(String, default='usd')
    interval = Column(String, nullable=False)  # month, year, etc.
    interval_count = Column(Integer, default=1)
    trial_period_days = Column(Integer, default=0)
    features = Column(JSON)  # JSON list of features included
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StripeSubscription(Base):
    """Stripe customer subscriptions for recurring billing"""
    __tablename__ = 'stripe_subscriptions'
    id = Column(Integer, primary_key=True)
    stripe_subscription_id = Column(String, nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('stripe_subscription_plans.id'), nullable=False)
    status = Column(String, nullable=False)  # active, canceled, past_due, etc.
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    payment_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship('Contact')
    organization = relationship('Organization')
    plan = relationship('StripeSubscriptionPlan')
    payments = relationship('StripePayment')