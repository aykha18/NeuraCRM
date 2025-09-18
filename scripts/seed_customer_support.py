"""Seed dummy data for Customer Support: tickets, KB articles, SLAs, surveys."""
import os
import sys
from datetime import datetime, timedelta
import random

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api.db import get_db, get_engine
from backend.api import models


def get_or_create_user(db, name: str, email: str, password: str, org_id: int):
    # Ensure organization  exists with the requested id
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        org = models.Organization(id=org_id, name=f"Org {org_id}")
        db.add(org)
        db.flush()
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        # Align org and password
        user.organization_id = org_id
        user.password_hash = password
        db.commit()
        return user
    user = models.User(name=name, email=email, password_hash=password, organization_id=org_id)
    db.add(user)
    db.commit()
    return user


def seed_sla(db, organization_id):
    if db.query(models.SupportSLA).count() > 0:
        return
    slas = [
        models.SupportSLA(organization_id=organization_id, name="Standard", priority="medium", first_response_time=24, resolution_time=48),
        models.SupportSLA(organization_id=organization_id, name="Premium", priority="high", first_response_time=8, resolution_time=24),
    ]
    db.add_all(slas)


def seed_kb(db, user, organization_id):
    if db.query(models.KnowledgeBaseArticle).count() > 0:
        return
    articles = [
        models.KnowledgeBaseArticle(
            organization_id=organization_id,
            title="Getting Started with NeuraCRM",
            slug="getting-started",
            content="Step-by-step guide to get started...",
            summary="Onboarding basics",
            category="getting_started",
            tags=["onboarding", "setup"],
            status="published",
            visibility="public",
            featured=True,
            author_id=user.id,
            published_at=datetime.utcnow(),
        ),
        models.KnowledgeBaseArticle(
            organization_id=organization_id,
            title="Troubleshooting Login Issues",
            slug="troubleshooting-login",
            content="If you can't login, check...",
            summary="Common login issues",
            category="troubleshooting",
            tags=["auth", "login"],
            status="published",
            visibility="public",
            featured=False,
            author_id=user.id,
            published_at=datetime.utcnow(),
        ),
    ]
    db.add_all(articles)


def seed_tickets(db, user, organization_id):
    if db.query(models.SupportTicket).count() > 0:
        return
    now = datetime.utcnow()
    tickets = []
    priorities = ["low", "medium", "high", "urgent"]
    categories = ["technical", "billing", "feature_request", "bug_report", "general"]
    for i in range(6):
        ticket = models.SupportTicket(
            ticket_number=f"TKT-{organization_id:03d}-{i+1:06d}",
            organization_id=organization_id,
            title=f"Sample ticket #{i+1}",
            description="This is a sample support request.",
            priority=random.choice(priorities),
            status=random.choice(["open", "in_progress", "pending_customer", "resolved"]),
            category=random.choice(categories),
            customer_name=f"Customer {i+1}",
            customer_email=f"customer{i+1}@example.com",
            sla_deadline=now + timedelta(hours=24),
            resolution_deadline=now + timedelta(hours=48),
            created_by=user.id,
        )
        tickets.append(ticket)
    db.add_all(tickets)
    db.flush()

    # Add a few comments per ticket
    for t in tickets:
        db.add(models.SupportComment(
            ticket_id=t.id,
            author_id=user.id,
            author_name=user.name,
            author_email=user.email,
            author_type="agent",
            content="Thanks for reaching out, we're looking into this.",
            is_internal=False,
        ))


def seed_surveys(db, organization_id):
    # Create surveys for resolved tickets
    tickets = db.query(models.SupportTicket).filter(models.SupportTicket.status == "resolved").all()
    for t in tickets:
        if db.query(models.CustomerSatisfactionSurvey).filter(models.CustomerSatisfactionSurvey.ticket_id == t.id).first():
            continue
        db.add(models.CustomerSatisfactionSurvey(
            ticket_id=t.id,
            organization_id=organization_id,
            survey_type="post_resolution",
            rating=random.randint(3, 5),
            nps_score=random.choice([20, 40, 60]),
            overall_satisfaction=random.randint(3, 5),
            response_time_rating=random.randint(3, 5),
            resolution_quality_rating=random.randint(3, 5),
            agent_knowledge_rating=random.randint(3, 5),
            communication_rating=random.randint(3, 5),
            what_went_well="Quick response and helpful guidance.",
            what_could_improve="More detailed docs.",
            additional_comments="Great support overall!",
            customer_name=t.customer_name,
            customer_email=t.customer_email,
        ))


def main():
    # Ensure tables exist
    engine = get_engine()
    models.Base.metadata.create_all(bind=engine)
    # Seed
    db = next(get_db())
    try:
        # Use provided test credentials and target org_id 8
        user = get_or_create_user(db, name="Node IT", email="nodeit@node.com", password="NodeIT2024!", org_id=8)
        organization_id = user.organization_id or 8
        seed_sla(db, organization_id)
        seed_kb(db, user, organization_id)
        seed_tickets(db, user, organization_id)
        seed_surveys(db, organization_id)
        db.commit()
        print("Seeded customer support data")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


