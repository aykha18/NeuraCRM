#!/usr/bin/env python3
"""
Seed knowledge base articles for testing
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.db import get_db
from api.models import User, Organization, KnowledgeBaseArticle

def seed_knowledge_base():
    """Create sample knowledge base articles"""
    db = next(get_db())
    
    try:
        # Get organization and user
        org = db.query(Organization).filter(Organization.id == 8).first()
        user = db.query(User).filter(User.email == 'nodeit@node.com').first()
        
        if not org or not user:
            print("Organization or user not found. Please run the main seed script first.")
            return
        
        # Check if articles already exist
        existing_count = db.query(KnowledgeBaseArticle).filter(
            KnowledgeBaseArticle.organization_id == org.id
        ).count()
        
        if existing_count > 0:
            print(f"Found {existing_count} existing knowledge base articles. Skipping seed.")
            return
        
        # Create sample articles
        articles = [
            KnowledgeBaseArticle(
                organization_id=org.id,
                title="Getting Started with NeuraCRM",
                slug="getting-started-neuracrm",
                content="""
# Getting Started with NeuraCRM

Welcome to NeuraCRM! This guide will help you get up and running quickly.

## Initial Setup

1. **Login**: Use your provided credentials to access the system
2. **Profile Setup**: Complete your profile information
3. **Organization Settings**: Configure your organization details

## Key Features

- **Lead Management**: Track and manage potential customers
- **Deal Pipeline**: Visualize your sales process with Kanban boards
- **Customer Support**: Handle tickets and provide excellent service
- **Financial Management**: Track invoices, payments, and revenue
- **Analytics**: Get insights into your business performance

## Next Steps

1. Import your existing contacts
2. Set up your sales pipeline stages
3. Create your first lead
4. Explore the dashboard

Need help? Contact our support team!
                """,
                summary="Complete guide to getting started with NeuraCRM",
                category="getting_started",
                subcategory="onboarding",
                tags=["onboarding", "setup", "getting-started"],
                status="published",
                visibility="public",
                featured=True,
                meta_description="Learn how to get started with NeuraCRM in minutes",
                author_id=user.id,
                published_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                organization_id=org.id,
                title="Troubleshooting Login Issues",
                slug="troubleshooting-login-issues",
                content="""
# Troubleshooting Login Issues

Having trouble logging in? Here are the most common solutions:

## Common Issues

### 1. Forgot Password
- Click "Forgot Password" on the login page
- Check your email for reset instructions
- Follow the link to create a new password

### 2. Account Locked
- Too many failed login attempts
- Wait 15 minutes or contact support
- Ensure you're using the correct email address

### 3. Browser Issues
- Clear your browser cache and cookies
- Try a different browser
- Disable browser extensions temporarily

### 4. Network Issues
- Check your internet connection
- Try accessing from a different network
- Contact your IT department if on corporate network

## Still Having Issues?

Contact our support team with:
- Your email address
- Browser type and version
- Error message (if any)
- Steps you've already tried
                """,
                summary="Solutions for common login problems",
                category="troubleshooting",
                subcategory="authentication",
                tags=["login", "authentication", "troubleshooting"],
                status="published",
                visibility="public",
                featured=True,
                meta_description="Fix login issues with these troubleshooting steps",
                author_id=user.id,
                published_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                organization_id=org.id,
                title="Managing Your Sales Pipeline",
                slug="managing-sales-pipeline",
                content="""
# Managing Your Sales Pipeline

Learn how to effectively manage your sales process using NeuraCRM's Kanban board.

## Pipeline Stages

### 1. New Leads
- Fresh prospects that need initial contact
- Qualify and gather basic information
- Move to "Contacted" when first contact is made

### 2. Contacted
- Initial contact has been made
- Schedule follow-up meetings
- Gather detailed requirements

### 3. Qualified
- Lead meets your criteria
- Budget and authority confirmed
- Move to "Proposal" when ready to present

### 4. Proposal
- Formal proposal sent
- Track proposal status
- Follow up on decision timeline

### 5. Negotiation
- Active discussions on terms
- Handle objections
- Work towards agreement

### 6. Won/Lost
- Deal outcome determined
- Update final details
- Move to customer management

## Best Practices

- **Regular Updates**: Keep deal information current
- **Follow-up Reminders**: Set reminders for next actions
- **Document Everything**: Add notes to each deal
- **Track Activities**: Log all customer interactions
                """,
                summary="Complete guide to managing your sales pipeline",
                category="features",
                subcategory="sales",
                tags=["pipeline", "sales", "kanban", "deals"],
                status="published",
                visibility="public",
                featured=False,
                meta_description="Master your sales pipeline with these proven techniques",
                author_id=user.id,
                published_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                organization_id=org.id,
                title="Billing and Payment Management",
                slug="billing-payment-management",
                content="""
# Billing and Payment Management

Manage your invoices, payments, and revenue with NeuraCRM's financial tools.

## Creating Invoices

1. **Navigate to Financial Management**
2. **Click "Create Invoice"**
3. **Select Customer Account**
4. **Choose Associated Deal** (if applicable)
5. **Enter Invoice Details**:
   - Description of services/products
   - Quantity and unit price
   - Tax rate
   - Due date

## Payment Tracking

### Recording Payments
1. Go to the Payments tab
2. Click "Record Payment"
3. Select the invoice
4. Enter payment details:
   - Amount paid
   - Payment method
   - Payment date
   - Reference number

### Payment Status
- **Pending**: Invoice created, no payment received
- **Partial**: Some payment received
- **Paid**: Full payment received
- **Overdue**: Past due date, no payment

## Revenue Recognition

Track when revenue should be recognized:
1. **Immediate**: Revenue recognized when payment received
2. **Deferred**: Revenue recognized over time
3. **Milestone**: Revenue recognized at project milestones

## Best Practices

- **Clear Descriptions**: Use detailed invoice descriptions
- **Timely Invoicing**: Send invoices promptly
- **Follow-up**: Track overdue payments
- **Documentation**: Keep all payment records
                """,
                summary="Complete guide to billing and payment management",
                category="features",
                subcategory="billing",
                tags=["billing", "invoices", "payments", "revenue"],
                status="published",
                visibility="public",
                featured=False,
                meta_description="Master billing and payment management in NeuraCRM",
                author_id=user.id,
                published_at=datetime.utcnow()
            ),
            KnowledgeBaseArticle(
                organization_id=org.id,
                title="Customer Support Best Practices",
                slug="customer-support-best-practices",
                content="""
# Customer Support Best Practices

Deliver exceptional customer service using NeuraCRM's support tools.

## Ticket Management

### Creating Tickets
1. **Gather Information**: Get all relevant details
2. **Categorize Properly**: Use correct category and priority
3. **Assign Appropriately**: Route to the right agent
4. **Set Expectations**: Communicate response times

### Ticket Lifecycle
1. **Open**: New ticket received
2. **In Progress**: Agent is working on it
3. **Pending Customer**: Waiting for customer response
4. **Resolved**: Issue fixed, awaiting confirmation
5. **Closed**: Ticket completed

## Communication Guidelines

### Response Times
- **Critical**: 1 hour
- **High**: 4 hours
- **Medium**: 24 hours
- **Low**: 72 hours

### Communication Style
- **Professional**: Use clear, professional language
- **Empathetic**: Show understanding of customer concerns
- **Actionable**: Provide clear next steps
- **Follow-up**: Check back to ensure satisfaction

## Knowledge Base Integration

- **Search First**: Check knowledge base before responding
- **Create Articles**: Document solutions for future use
- **Link Resources**: Reference relevant articles in responses
- **Update Content**: Keep knowledge base current

## Escalation Procedures

### When to Escalate
- Customer requests manager
- Technical issues beyond scope
- Billing disputes
- SLA at risk

### Escalation Process
1. Document the issue thoroughly
2. Attempt resolution first
3. Escalate with context
4. Follow up on resolution
                """,
                summary="Best practices for customer support excellence",
                category="support",
                subcategory="best-practices",
                tags=["support", "customer-service", "tickets", "best-practices"],
                status="published",
                visibility="public",
                featured=True,
                meta_description="Deliver exceptional customer support with these proven techniques",
                author_id=user.id,
                published_at=datetime.utcnow()
            )
        ]
        
        db.add_all(articles)
        db.commit()
        
        print(f"✅ Created {len(articles)} knowledge base articles successfully!")
        for article in articles:
            print(f"  - {article.title} ({article.status})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating knowledge base articles: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_knowledge_base()
