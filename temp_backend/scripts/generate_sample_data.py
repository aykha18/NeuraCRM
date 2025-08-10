from sqlalchemy import text
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base, User, Contact, Lead, Deal, Stage, Activity, Message, Channel, Tag

# Config
DB_URL = 'postgresql+psycopg2://neura:neura25@localhost/postgres'
NUM_USERS = 15
NUM_CONTACTS = 1000
NUM_LEADS = 5000
NUM_DEALS = 200
NUM_ACTIVITIES = 2000
NUM_MESSAGES = 1000
NUM_CHANNELS = 4
NUM_TAGS = 1000

faker = Faker()
Faker.seed(42)
random.seed(42)

# Helper: random date in last month
def random_date():
    now = datetime.now()
    start = now - timedelta(days=60)
    return faker.date_time_between(start_date=start, end_date=now)

# Connect DB
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Truncate all tables
for table in [Activity, Message, Deal, Lead, Contact, User, Stage, Channel, Tag]:
    session.execute(text(f'TRUNCATE TABLE {table.__tablename__} RESTART IDENTITY CASCADE;'))
session.commit()

# Stages
stage_names = ['New', 'Contacted', 'Proposal Sent', 'Negotiation', 'Won', 'Lost']
stages = [Stage(name=name, order=i+1, wip_limit=10) for i, name in enumerate(stage_names)]
session.add_all(stages)
session.commit()

# Channels
channel_names = ['General', 'VIP Clients', 'Operations', 'AI Insights']
channels = [Channel(name=name, is_group=True, created_at=random_date()) for name in channel_names]
session.add_all(channels)
session.commit()

# Users (mix of Indian and Middle Eastern names)
user_names = [
    'Ayaan Khan', 'Fatima Al Mansoori', 'Rohan Mehra', 'Sara Al Farsi', 'Imran Patel',
    'Layla Nasser', 'Omar Al Hashimi', 'Priya Sharma', 'Yousef Al Suwaidi', 'Sneha Reddy',
    'Hassan Jaber', 'Aisha Siddiqui', 'Zainab Al Mazrouei', 'Vikram Singh', 'Mariam Al Shamsi'
]
users = [User(
    name=name,
    email=faker.unique.email(),
    password_hash='hash',
    role=random.choice(['admin', 'manager', 'agent']),
    created_at=random_date()
) for name in user_names]
session.add_all(users)
session.commit()

# Contacts
contacts = [Contact(
    name=faker.name(),
    email=faker.unique.email(),
    phone=faker.phone_number(),
    company=faker.company(),
    owner_id=random.choice(users).id,
    created_at=random_date()
) for _ in range(NUM_CONTACTS)]
session.add_all(contacts)
session.commit()

# Leads
leads = [Lead(
    title=faker.catch_phrase(),
    contact_id=random.choice(contacts).id,
    owner_id=random.choice(users).id,
    status=random.choice(['new', 'qualified', 'lost', 'converted']),
    source=random.choice(['web', 'referral', 'walk-in']),
    created_at=random_date()
) for _ in range(NUM_LEADS)]
session.add_all(leads)
session.commit()

# Deals
deals = [Deal(
    title=faker.bs().title(),
    value=random.randint(1000, 20000),
    owner_id=random.choice(users).id,
    stage_id=random.choice(stages).id,
    description=faker.text(max_nb_chars=80),
    created_at=random_date(),
    closed_at=None,
    reminder_date=random_date(),
    contact_id=random.choice(contacts).id
) for _ in range(NUM_DEALS)]
session.add_all(deals)
session.commit()

# Tags
tags = [Tag(label=faker.word().capitalize(), color=faker.hex_color()) for _ in range(NUM_TAGS)]
session.add_all(tags)
session.commit()

# Activities (with some AI-flavored)
ai_msgs = [
    'AI suggested upsell: Add Desert Safari to package.',
    'AI flagged as high conversion probability.',
    'AI-generated: Recommend upsell for Family Fun Dubai.',
    'AI Insights: Top conversion time is 2-4pm.',
    'AI-generated: Client likely to book again next month.'
]
activities = []
for i in range(NUM_ACTIVITIES):
    deal = random.choice(deals)
    user = random.choice(users)
    msg = faker.sentence()
    if i % 10 == 0:
        msg = random.choice(ai_msgs)
        typ = 'ai_suggestion'
    else:
        typ = random.choice(['comment', 'edit', 'reminder', 'status_change'])
    activities.append(Activity(
        deal_id=deal.id,
        user_id=user.id,
        type=typ,
        message=msg,
        timestamp=random_date()
    ))
session.add_all(activities)
session.commit()

# Messages (with some AI-generated)
ai_msgs_chat = [
    'AI Insights: This client is likely to convert.',
    'AI-generated: Recommend upsell for VIP package.',
    'AI flagged this lead as high value.',
    'AI: Suggest follow-up tomorrow.',
    'AI: Client responded positively to last offer.'
]
messages = []
for i in range(NUM_MESSAGES):
    sender = random.choice(users)
    channel = random.choice(channels)
    content = faker.sentence()
    if i % 10 == 0:
        content = random.choice(ai_msgs_chat)
    messages.append(Message(
        sender_id=sender.id,
        content=content,
        channel_id=channel.id,
        recipient_id=None,
        created_at=random_date(),
        read=random.choice([True, False])
    ))
session.add_all(messages)
session.commit()

print('Sample data generated successfully!') 