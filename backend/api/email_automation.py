"""
Email Automation Service
Handles email templates, personalization, and campaign management
"""
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from api.models import EmailTemplate, EmailCampaign, EmailLog, Lead, Contact, Deal, User

class EmailAutomationService:
    def __init__(self):
        # Available template variables
        self.variables = {
            'contact': ['name', 'email', 'phone', 'company'],
            'lead': ['title', 'status', 'source', 'score'],
            'deal': ['title', 'value', 'stage'],
            'user': ['name', 'email'],
            'system': ['current_date', 'current_time']
        }
    
    def get_template_variables(self, template_body: str) -> List[str]:
        """Extract all variables from template body"""
        pattern = r'\{\{(\w+(?:\.\w+)*)\}\}'
        return re.findall(pattern, template_body)
    
    def validate_template(self, template_body: str) -> Dict[str, Any]:
        """Validate template and return available/missing variables"""
        variables = self.get_template_variables(template_body)
        available_vars = []
        missing_vars = []
        
        for var in variables:
            if self._is_variable_available(var):
                available_vars.append(var)
            else:
                missing_vars.append(var)
        
        return {
            'valid': len(missing_vars) == 0,
            'available_variables': available_vars,
            'missing_variables': missing_vars,
            'total_variables': len(variables)
        }
    
    def _is_variable_available(self, variable: str) -> bool:
        """Check if a variable is supported"""
        parts = variable.split('.')
        if len(parts) < 2:
            return False
        
        category = parts[0]
        field = parts[1]
        
        return category in self.variables and field in self.variables[category]
    
    def personalize_template(self, template: EmailTemplate, context: Dict[str, Any]) -> Dict[str, str]:
        """Personalize template with context data"""
        subject = template.subject
        body = template.body
        
        # Replace variables in subject and body
        subject = self._replace_variables(subject, context)
        body = self._replace_variables(body, context)
        
        return {
            'subject': subject,
            'body': body
        }
    
    def _replace_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Replace template variables with actual values"""
        def replace_var(match):
            var_name = match.group(1)
            return self._get_variable_value(var_name, context)
        
        pattern = r'\{\{(\w+(?:\.\w+)*)\}\}'
        return re.sub(pattern, replace_var, text)
    
    def _get_variable_value(self, variable: str, context: Dict[str, Any]) -> str:
        """Get the actual value for a variable from context"""
        parts = variable.split('.')
        if len(parts) < 2:
            return f"{{{{{variable}}}}}"
        
        category = parts[0]
        field = parts[1]
        
        if category not in context:
            return f"{{{{{variable}}}}}"
        
        data = context[category]
        if not isinstance(data, dict):
            return f"{{{{{variable}}}}}"
        
        value = data.get(field, f"{{{{{variable}}}}}")
        
        # Handle special cases
        if field == 'current_date':
            return datetime.now().strftime('%B %d, %Y')
        elif field == 'current_time':
            return datetime.now().strftime('%I:%M %p')
        elif field == 'value' and isinstance(value, (int, float)):
            return f"${value:,.2f}"
        elif field == 'created_at' and value:
            try:
                date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return date_obj.strftime('%B %d, %Y')
            except:
                return str(value)
        
        return str(value) if value is not None else ""
    
    def get_context_for_lead(self, lead: Lead, db: Session) -> Dict[str, Any]:
        """Get context data for a lead"""
        context = {
            'system': {
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_time': datetime.now().strftime('%H:%M:%S')
            }
        }
        
        # Add lead data
        if lead:
            context['lead'] = {
                'title': lead.title,
                'status': lead.status,
                'source': lead.source,
                'score': lead.score,
                'created_at': lead.created_at.isoformat() if lead.created_at else None
            }
        
        # Add contact data
        if lead and lead.contact:
            context['contact'] = {
                'name': lead.contact.name,
                'email': lead.contact.email,
                'phone': lead.contact.phone,
                'company': lead.contact.company
            }
        
        # Add owner data
        if lead and lead.owner:
            context['user'] = {
                'name': lead.owner.name,
                'email': lead.owner.email
            }
        
        return context
    
    def get_context_for_contact(self, contact: Contact, db: Session) -> Dict[str, Any]:
        """Get context data for a contact"""
        context = {
            'system': {
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_time': datetime.now().strftime('%H:%M:%S')
            }
        }
        
        # Add contact data
        if contact:
            context['contact'] = {
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'company': contact.company
            }
        
        # Add owner data
        if contact and contact.owner:
            context['user'] = {
                'name': contact.owner.name,
                'email': contact.owner.email
            }
        
        return context
    
    def get_context_for_deal(self, deal: Deal, db: Session) -> Dict[str, Any]:
        """Get context data for a deal"""
        context = {
            'system': {
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_time': datetime.now().strftime('%H:%M:%S')
            }
        }
        
        # Add deal data
        if deal:
            context['deal'] = {
                'title': deal.title,
                'value': deal.value,
                'stage': deal.stage.name if deal.stage else None,
                'created_at': deal.created_at.isoformat() if deal.created_at else None
            }
        
        # Add contact data
        if deal and deal.contact:
            context['contact'] = {
                'name': deal.contact.name,
                'email': deal.contact.email,
                'phone': deal.contact.phone,
                'company': deal.contact.company
            }
        
        # Add owner data
        if deal and deal.owner:
            context['user'] = {
                'name': deal.owner.name,
                'email': deal.owner.email
            }
        
        return context
    
    def create_email_log(self, campaign: EmailCampaign, template: EmailTemplate, 
                        recipient_data: Dict[str, Any], personalized_content: Dict[str, str],
                        db: Session) -> EmailLog:
        """Create an email log entry"""
        email_log = EmailLog(
            campaign_id=campaign.id,
            recipient_type=recipient_data.get('type'),
            recipient_id=recipient_data.get('id'),
            recipient_email=recipient_data.get('email'),
            recipient_name=recipient_data.get('name'),
            subject=personalized_content['subject'],
            body=personalized_content['body'],
            status='sent'
        )
        
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        
        return email_log
    
    def get_sample_templates(self) -> List[Dict[str, Any]]:
        """Get sample email templates"""
        return [
            {
                'name': 'Welcome Email',
                'category': 'welcome',
                'subject': 'Welcome to {{contact.company}}, {{contact.name}}!',
                'body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Welcome {{contact.name}}!</h2>
                    <p>Thank you for your interest in our services. We're excited to work with you and {{contact.company}}.</p>
                    <p>Your dedicated account manager, {{user.name}}, will be reaching out to you shortly to discuss your needs.</p>
                    <p>Best regards,<br>The {{contact.company}} Team</p>
                </div>
                '''
            },
            {
                'name': 'Follow-up Email',
                'category': 'follow_up',
                'subject': 'Following up on your {{lead.title}}',
                'body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Hi {{contact.name}},</h2>
                    <p>I wanted to follow up on your interest in {{lead.title}}.</p>
                    <p>Based on your {{lead.source}} inquiry, I believe we can help {{contact.company}} achieve great results.</p>
                    <p>Would you be available for a quick call this week to discuss your specific needs?</p>
                    <p>Best regards,<br>{{user.name}}</p>
                </div>
                '''
            },
            {
                'name': 'Deal Update',
                'category': 'deal_update',
                'subject': 'Update on your {{deal.title}}',
                'body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Hi {{contact.name}},</h2>
                    <p>I wanted to provide you with an update on your {{deal.title}}.</p>
                    <p>Current Status: {{deal.stage}}<br>
                    Deal Value: {{deal.value}}</p>
                    <p>We're making great progress and I'll keep you updated on any developments.</p>
                    <p>Best regards,<br>{{user.name}}</p>
                </div>
                '''
            },
            {
                'name': 'Lead Score Notification',
                'category': 'notification',
                'subject': 'Your lead {{lead.title}} has been scored',
                'body': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Hi {{contact.name}},</h2>
                    <p>Great news! We've analyzed your lead "{{lead.title}}" and given it a score of {{lead.score}}/100.</p>
                    <p>This indicates a {{lead.score >= 80 ? 'high' : lead.score >= 60 ? 'good' : 'moderate'}} level of interest and potential.</p>
                    <p>I'll be reaching out soon to discuss next steps.</p>
                    <p>Best regards,<br>{{user.name}}</p>
                </div>
                '''
            }
        ]

# Global instance
email_automation_service = EmailAutomationService() 