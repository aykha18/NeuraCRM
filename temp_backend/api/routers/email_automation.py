"""
Email Automation Router
Handles email templates, campaigns, and automation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from api.db import get_db
from api.models import EmailTemplate, EmailCampaign, EmailLog, Lead, Contact, Deal, User
from api.email_automation import email_automation_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/email", tags=["Email Automation"])

# Pydantic models
class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    category: Optional[str] = None

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class EmailTemplateOut(BaseModel):
    id: int
    name: str
    subject: str
    body: str
    category: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    validation: Optional[dict] = None

    class Config:
        from_attributes = True

class EmailCampaignCreate(BaseModel):
    name: str
    template_id: int
    subject_override: Optional[str] = None
    body_override: Optional[str] = None
    target_type: str  # leads, contacts, deals, custom
    target_ids: List[int]
    scheduled_at: Optional[datetime] = None

class EmailCampaignOut(BaseModel):
    id: int
    name: str
    template_id: int
    subject_override: Optional[str]
    body_override: Optional[str]
    target_type: str
    target_ids: str
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    status: str
    created_by: Optional[int]
    created_at: datetime
    template: Optional[EmailTemplateOut] = None

    class Config:
        from_attributes = True

class EmailLogOut(BaseModel):
    id: int
    campaign_id: int
    recipient_type: Optional[str]
    recipient_id: Optional[int]
    recipient_email: str
    recipient_name: Optional[str]
    subject: str
    body: str
    sent_at: datetime
    status: str
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True

class TemplatePreviewRequest(BaseModel):
    template_id: int
    recipient_type: str  # lead, contact, deal
    recipient_id: int

# Template endpoints
@router.get("/templates", response_model=List[EmailTemplateOut])
def get_email_templates(
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all email templates"""
    query = db.query(EmailTemplate)
    
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    if active_only:
        query = query.filter(EmailTemplate.is_active == True)
    
    templates = query.all()
    
    # Add validation info to each template
    result = []
    for template in templates:
        template_dict = EmailTemplateOut.model_validate(template).model_dump()
        template_dict['validation'] = email_automation_service.validate_template(template.body)
        result.append(template_dict)
    
    return result

@router.post("/templates", response_model=EmailTemplateOut)
def create_email_template(
    template_data: EmailTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    # Validate template
    validation = email_automation_service.validate_template(template_data.body)
    
    template = EmailTemplate(
        name=template_data.name,
        subject=template_data.subject,
        body=template_data.body,
        category=template_data.category,
        created_by=1  # TODO: Get from auth
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    result = EmailTemplateOut.model_validate(template).model_dump()
    result['validation'] = validation
    return result

@router.put("/templates/{template_id}", response_model=EmailTemplateOut)
def update_email_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an email template"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update fields
    if template_data.name is not None:
        template.name = template_data.name
    if template_data.subject is not None:
        template.subject = template_data.subject
    if template_data.body is not None:
        template.body = template_data.body
    if template_data.category is not None:
        template.category = template_data.category
    if template_data.is_active is not None:
        template.is_active = template_data.is_active
    
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    result = EmailTemplateOut.model_validate(template).model_dump()
    result['validation'] = email_automation_service.validate_template(template.body)
    return result

@router.delete("/templates/{template_id}")
def delete_email_template(template_id: int, db: Session = Depends(get_db)):
    """Delete an email template"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}

@router.post("/templates/preview")
def preview_template(request: TemplatePreviewRequest, db: Session = Depends(get_db)):
    """Preview a template with actual data"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == request.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get recipient data based on type
    if request.recipient_type == "lead":
        recipient = db.query(Lead).filter(Lead.id == request.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Lead not found")
        context = email_automation_service.get_context_for_lead(recipient, db)
    elif request.recipient_type == "contact":
        recipient = db.query(Contact).filter(Contact.id == request.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Contact not found")
        context = email_automation_service.get_context_for_contact(recipient, db)
    elif request.recipient_type == "deal":
        recipient = db.query(Deal).filter(Deal.id == request.recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Deal not found")
        context = email_automation_service.get_context_for_deal(recipient, db)
    else:
        raise HTTPException(status_code=400, detail="Invalid recipient type")
    
    # Personalize template
    personalized = email_automation_service.personalize_template(template, context)
    
    return {
        "subject": personalized['subject'],
        "body": personalized['body'],
        "context": context
    }

@router.post("/templates/sample")
def create_sample_templates(db: Session = Depends(get_db)):
    """Create sample email templates"""
    sample_templates = email_automation_service.get_sample_templates()
    created_templates = []
    
    for sample in sample_templates:
        template = EmailTemplate(
            name=sample['name'],
            subject=sample['subject'],
            body=sample['body'],
            category=sample['category'],
            created_by=1  # TODO: Get from auth
        )
        db.add(template)
        created_templates.append(template)
    
    db.commit()
    
    return {"message": f"Created {len(created_templates)} sample templates"}

# Campaign endpoints
@router.get("/campaigns", response_model=List[EmailCampaignOut])
def get_email_campaigns(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all email campaigns"""
    query = db.query(EmailCampaign)
    
    if status:
        query = query.filter(EmailCampaign.status == status)
    
    campaigns = query.all()
    return [EmailCampaignOut.model_validate(campaign) for campaign in campaigns]

@router.post("/campaigns", response_model=EmailCampaignOut)
def create_email_campaign(
    campaign_data: EmailCampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a new email campaign"""
    # Verify template exists
    template = db.query(EmailTemplate).filter(EmailTemplate.id == campaign_data.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    campaign = EmailCampaign(
        name=campaign_data.name,
        template_id=campaign_data.template_id,
        subject_override=campaign_data.subject_override,
        body_override=campaign_data.body_override,
        target_type=campaign_data.target_type,
        target_ids=json.dumps(campaign_data.target_ids),
        scheduled_at=campaign_data.scheduled_at,
        created_by=1  # TODO: Get from auth
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return EmailCampaignOut.model_validate(campaign)

@router.post("/campaigns/{campaign_id}/send")
def send_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Send an email campaign"""
    campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Campaign can only be sent from draft status")
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == campaign.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    target_ids = json.loads(campaign.target_ids)
    sent_count = 0
    
    # Get recipients based on target type
    if campaign.target_type == "leads":
        recipients = db.query(Lead).filter(Lead.id.in_(target_ids)).all()
        for lead in recipients:
            if lead.contact and lead.contact.email:
                context = email_automation_service.get_context_for_lead(lead, db)
                personalized = email_automation_service.personalize_template(template, context)
                
                # Create email log (simulating email send)
                recipient_data = {
                    'type': 'lead',
                    'id': lead.id,
                    'email': lead.contact.email,
                    'name': lead.contact.name
                }
                email_automation_service.create_email_log(campaign, template, recipient_data, personalized, db)
                sent_count += 1
    
    elif campaign.target_type == "contacts":
        recipients = db.query(Contact).filter(Contact.id.in_(target_ids)).all()
        for contact in recipients:
            if contact.email:
                context = email_automation_service.get_context_for_contact(contact, db)
                personalized = email_automation_service.personalize_template(template, context)
                
                recipient_data = {
                    'type': 'contact',
                    'id': contact.id,
                    'email': contact.email,
                    'name': contact.name
                }
                email_automation_service.create_email_log(campaign, template, recipient_data, personalized, db)
                sent_count += 1
    
    elif campaign.target_type == "deals":
        recipients = db.query(Deal).filter(Deal.id.in_(target_ids)).all()
        for deal in recipients:
            if deal.contact and deal.contact.email:
                context = email_automation_service.get_context_for_deal(deal, db)
                personalized = email_automation_service.personalize_template(template, context)
                
                recipient_data = {
                    'type': 'deal',
                    'id': deal.id,
                    'email': deal.contact.email,
                    'name': deal.contact.name
                }
                email_automation_service.create_email_log(campaign, template, recipient_data, personalized, db)
                sent_count += 1
    
    # Update campaign status
    campaign.status = "completed"
    campaign.sent_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Campaign sent successfully",
        "sent_count": sent_count,
        "total_recipients": len(target_ids)
    }

# Email logs endpoints
@router.get("/logs", response_model=List[EmailLogOut])
def get_email_logs(
    campaign_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """Get email logs"""
    query = db.query(EmailLog)
    
    if campaign_id:
        query = query.filter(EmailLog.campaign_id == campaign_id)
    
    if status:
        query = query.filter(EmailLog.status == status)
    
    logs = query.order_by(EmailLog.sent_at.desc()).limit(limit).all()
    return [EmailLogOut.model_validate(log) for log in logs]

@router.get("/logs/analytics")
def get_email_analytics(db: Session = Depends(get_db)):
    """Get email analytics"""
    total_sent = db.query(EmailLog).filter(EmailLog.status == "sent").count()
    total_opened = db.query(EmailLog).filter(EmailLog.opened_at.isnot(None)).count()
    total_clicked = db.query(EmailLog).filter(EmailLog.clicked_at.isnot(None)).count()
    
    open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
    click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
    
    return {
        "total_sent": total_sent,
        "total_opened": total_opened,
        "total_clicked": total_clicked,
        "open_rate": round(open_rate, 2),
        "click_rate": round(click_rate, 2)
    } 