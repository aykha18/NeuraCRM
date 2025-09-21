#!/usr/bin/env python3
"""
NeuraCRM Test Data Management System
Manages test data generation, cleanup, and validation
"""

import json
import os
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

@dataclass
class TestUser:
    """Test user data structure"""
    id: str
    name: str
    email: str
    password: str
    role: str
    organization_id: str
    created_at: str

@dataclass
class TestLead:
    """Test lead data structure"""
    id: str
    name: str
    email: str
    company: str
    phone: str
    status: str
    source: str
    score: int
    created_at: str
    owner_id: str

@dataclass
class TestContact:
    """Test contact data structure"""
    id: str
    name: str
    email: str
    phone: str
    company: str
    position: str
    created_at: str
    owner_id: str

@dataclass
class TestDeal:
    """Test deal data structure"""
    id: str
    title: str
    value: float
    stage: str
    probability: int
    close_date: str
    lead_id: str
    owner_id: str
    created_at: str

class TestDataManager:
    """Manages test data generation and cleanup"""
    
    def __init__(self, data_dir: str = "tests/data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # Sample data pools
        self.first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily",
            "James", "Jessica", "William", "Ashley", "Richard", "Amanda", "Joseph",
            "Jennifer", "Thomas", "Michelle", "Christopher", "Kimberly"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]
        
        self.companies = [
            "Acme Corp", "Tech Solutions Inc", "Global Industries", "Innovation Labs",
            "Digital Dynamics", "Future Systems", "Smart Technologies", "NextGen Corp",
            "Advanced Solutions", "Premier Services", "Elite Enterprises", "Proactive Inc",
            "Strategic Partners", "Dynamic Solutions", "Creative Technologies"
        ]
        
        self.industries = [
            "Technology", "Healthcare", "Finance", "Manufacturing", "Retail",
            "Education", "Real Estate", "Consulting", "Marketing", "Automotive"
        ]
        
        self.lead_sources = [
            "Website", "Referral", "Cold Call", "Email Campaign", "Social Media",
            "Trade Show", "Advertisement", "Partner", "Webinar", "Content Marketing"
        ]
        
        self.lead_statuses = [
            "new", "contacted", "qualified", "proposal", "negotiation", "closed-won", "closed-lost"
        ]
        
        self.deal_stages = [
            "prospecting", "qualification", "proposal", "negotiation", "closed-won", "closed-lost"
        ]
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/generated", exist_ok=True)
        os.makedirs(f"{self.data_dir}/fixtures", exist_ok=True)
    
    def generate_random_string(self, length: int = 8) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def generate_email(self, first_name: str, last_name: str, domain: str = "test.com") -> str:
        """Generate test email"""
        return f"{first_name.lower()}.{last_name.lower()}@{domain}"
    
    def generate_phone(self) -> str:
        """Generate test phone number"""
        return f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def generate_test_user(self, role: str = "agent") -> TestUser:
        """Generate test user data"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        email = self.generate_email(first_name, last_name)
        
        return TestUser(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password="TestPassword123!",
            role=role,
            organization_id="test-org-001",
            created_at=datetime.now().isoformat()
        )
    
    def generate_test_lead(self, owner_id: str) -> TestLead:
        """Generate test lead data"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        email = self.generate_email(first_name, last_name)
        company = random.choice(self.companies)
        
        return TestLead(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            company=company,
            phone=self.generate_phone(),
            status=random.choice(self.lead_statuses),
            source=random.choice(self.lead_sources),
            score=random.randint(0, 100),
            created_at=datetime.now().isoformat(),
            owner_id=owner_id
        )
    
    def generate_test_contact(self, owner_id: str) -> TestContact:
        """Generate test contact data"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        name = f"{first_name} {last_name}"
        email = self.generate_email(first_name, last_name)
        company = random.choice(self.companies)
        
        positions = [
            "CEO", "CTO", "VP Sales", "Marketing Director", "Sales Manager",
            "Product Manager", "Business Analyst", "Account Executive", "Operations Manager"
        ]
        
        return TestContact(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=self.generate_phone(),
            company=company,
            position=random.choice(positions),
            created_at=datetime.now().isoformat(),
            owner_id=owner_id
        )
    
    def generate_test_deal(self, lead_id: str, owner_id: str) -> TestDeal:
        """Generate test deal data"""
        titles = [
            "Software License Agreement", "Consulting Services", "Product Implementation",
            "Support Contract", "Training Services", "Custom Development", "Integration Project"
        ]
        
        close_date = datetime.now() + timedelta(days=random.randint(30, 180))
        
        return TestDeal(
            id=str(uuid.uuid4()),
            title=random.choice(titles),
            value=random.uniform(10000, 500000),
            stage=random.choice(self.deal_stages),
            probability=random.randint(10, 90),
            close_date=close_date.isoformat(),
            lead_id=lead_id,
            owner_id=owner_id,
            created_at=datetime.now().isoformat()
        )
    
    def generate_test_dataset(self, 
                            num_users: int = 5,
                            num_leads_per_user: int = 10,
                            num_contacts_per_user: int = 8,
                            num_deals_per_user: int = 5) -> Dict[str, Any]:
        """Generate complete test dataset"""
        dataset = {
            "users": [],
            "leads": [],
            "contacts": [],
            "deals": [],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "num_users": num_users,
                "num_leads_per_user": num_leads_per_user,
                "num_contacts_per_user": num_contacts_per_user,
                "num_deals_per_user": num_deals_per_user
            }
        }
        
        # Generate users
        roles = ["admin", "manager", "agent", "viewer"]
        for i in range(num_users):
            user = self.generate_test_user(role=random.choice(roles))
            dataset["users"].append(asdict(user))
            
            # Generate leads for this user
            for j in range(num_leads_per_user):
                lead = self.generate_test_lead(user.id)
                dataset["leads"].append(asdict(lead))
            
            # Generate contacts for this user
            for j in range(num_contacts_per_user):
                contact = self.generate_test_contact(user.id)
                dataset["contacts"].append(asdict(contact))
            
            # Generate deals for this user (using some of the leads)
            user_leads = [lead for lead in dataset["leads"] if lead["owner_id"] == user.id]
            for j in range(min(num_deals_per_user, len(user_leads))):
                deal = self.generate_test_deal(user_leads[j]["id"], user.id)
                dataset["deals"].append(asdict(deal))
        
        return dataset
    
    def save_test_dataset(self, dataset: Dict[str, Any], filename: str = None) -> str:
        """Save test dataset to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_dataset_{timestamp}.json"
        
        filepath = f"{self.data_dir}/generated/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return filepath
    
    def load_test_dataset(self, filename: str) -> Dict[str, Any]:
        """Load test dataset from file"""
        filepath = f"{self.data_dir}/generated/{filename}"
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def create_fixture_data(self) -> Dict[str, Any]:
        """Create fixture data for specific test scenarios"""
        fixtures = {
            "valid_login_user": {
                "email": "nodeit@node.com",
                "password": "NodeIT2024!",
                "name": "Test User",
                "role": "admin"
            },
            "invalid_login_credentials": [
                {"email": "invalid@example.com", "password": "wrongpassword"},
                {"email": "nodeit@node.com", "password": "wrongpassword"},
                {"email": "", "password": "NodeIT2024!"},
                {"email": "nodeit@node.com", "password": ""}
            ],
            "lead_creation_data": {
                "valid_lead": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "company": "Acme Corp",
                    "phone": "+1-555-0123",
                    "status": "new",
                    "source": "website"
                },
                "invalid_lead": {
                    "name": "",
                    "email": "invalid-email",
                    "company": "",
                    "phone": "invalid-phone"
                }
            },
            "contact_creation_data": {
                "valid_contact": {
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "phone": "+1-555-0456",
                    "company": "Tech Solutions Inc",
                    "position": "CEO"
                }
            },
            "deal_creation_data": {
                "valid_deal": {
                    "title": "Software License Agreement",
                    "value": 50000,
                    "stage": "proposal",
                    "probability": 75,
                    "close_date": "2025-06-15"
                }
            }
        }
        
        return fixtures
    
    def save_fixture_data(self, fixtures: Dict[str, Any]) -> str:
        """Save fixture data to file"""
        filepath = f"{self.data_dir}/fixtures/test_fixtures.json"
        
        with open(filepath, 'w') as f:
            json.dump(fixtures, f, indent=2)
        
        return filepath
    
    def load_fixture_data(self) -> Dict[str, Any]:
        """Load fixture data from file"""
        filepath = f"{self.data_dir}/fixtures/test_fixtures.json"
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default fixtures if file doesn't exist
            fixtures = self.create_fixture_data()
            self.save_fixture_data(fixtures)
            return fixtures
    
    def cleanup_test_data(self, dataset: Dict[str, Any]) -> Dict[str, int]:
        """Cleanup test data (simulate API calls to delete data)"""
        cleanup_stats = {
            "deals_deleted": len(dataset.get("deals", [])),
            "contacts_deleted": len(dataset.get("contacts", [])),
            "leads_deleted": len(dataset.get("leads", [])),
            "users_deleted": len(dataset.get("users", []))
        }
        
        # In a real implementation, this would make API calls to delete the data
        # For now, we just return the cleanup statistics
        
        return cleanup_stats
    
    def validate_test_data(self, dataset: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate test data integrity"""
        validation_results = {
            "errors": [],
            "warnings": []
        }
        
        # Validate users
        users = dataset.get("users", [])
        for user in users:
            if not user.get("email") or "@" not in user["email"]:
                validation_results["errors"].append(f"Invalid email for user: {user.get('name', 'Unknown')}")
            
            if not user.get("name"):
                validation_results["errors"].append(f"Missing name for user: {user.get('email', 'Unknown')}")
        
        # Validate leads
        leads = dataset.get("leads", [])
        for lead in leads:
            if not lead.get("email") or "@" not in lead["email"]:
                validation_results["errors"].append(f"Invalid email for lead: {lead.get('name', 'Unknown')}")
            
            if not lead.get("owner_id"):
                validation_results["errors"].append(f"Missing owner_id for lead: {lead.get('name', 'Unknown')}")
            
            # Check if owner exists
            owner_exists = any(user["id"] == lead["owner_id"] for user in users)
            if not owner_exists:
                validation_results["warnings"].append(f"Lead {lead.get('name', 'Unknown')} has invalid owner_id")
        
        # Validate deals
        deals = dataset.get("deals", [])
        for deal in deals:
            if not deal.get("lead_id"):
                validation_results["errors"].append(f"Missing lead_id for deal: {deal.get('title', 'Unknown')}")
            
            if deal.get("value", 0) <= 0:
                validation_results["warnings"].append(f"Deal {deal.get('title', 'Unknown')} has invalid value")
        
        return validation_results
    
    def get_test_data_summary(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary statistics of test data"""
        summary = {
            "total_users": len(dataset.get("users", [])),
            "total_leads": len(dataset.get("leads", [])),
            "total_contacts": len(dataset.get("contacts", [])),
            "total_deals": len(dataset.get("deals", [])),
            "leads_by_status": {},
            "deals_by_stage": {},
            "users_by_role": {}
        }
        
        # Count leads by status
        for lead in dataset.get("leads", []):
            status = lead.get("status", "unknown")
            summary["leads_by_status"][status] = summary["leads_by_status"].get(status, 0) + 1
        
        # Count deals by stage
        for deal in dataset.get("deals", []):
            stage = deal.get("stage", "unknown")
            summary["deals_by_stage"][stage] = summary["deals_by_stage"].get(stage, 0) + 1
        
        # Count users by role
        for user in dataset.get("users", []):
            role = user.get("role", "unknown")
            summary["users_by_role"][role] = summary["users_by_role"].get(role, 0) + 1
        
        return summary

def main():
    """Main function to demonstrate test data management"""
    manager = TestDataManager()
    
    print("🧪 NeuraCRM Test Data Manager")
    print("=" * 50)
    
    # Generate test dataset
    print("Generating test dataset...")
    dataset = manager.generate_test_dataset(
        num_users=3,
        num_leads_per_user=5,
        num_contacts_per_user=4,
        num_deals_per_user=3
    )
    
    # Save dataset
    filepath = manager.save_test_dataset(dataset)
    print(f"Test dataset saved: {filepath}")
    
    # Create and save fixtures
    fixtures = manager.create_fixture_data()
    fixture_path = manager.save_fixture_data(fixtures)
    print(f"Fixture data saved: {fixture_path}")
    
    # Validate data
    validation = manager.validate_test_data(dataset)
    print(f"\nValidation Results:")
    print(f"Errors: {len(validation['errors'])}")
    print(f"Warnings: {len(validation['warnings'])}")
    
    if validation["errors"]:
        print("Errors found:")
        for error in validation["errors"]:
            print(f"  - {error}")
    
    if validation["warnings"]:
        print("Warnings found:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    # Get summary
    summary = manager.get_test_data_summary(dataset)
    print(f"\nTest Data Summary:")
    print(f"Users: {summary['total_users']}")
    print(f"Leads: {summary['total_leads']}")
    print(f"Contacts: {summary['total_contacts']}")
    print(f"Deals: {summary['total_deals']}")
    
    print(f"\nLeads by Status:")
    for status, count in summary["leads_by_status"].items():
        print(f"  {status}: {count}")
    
    print(f"\nDeals by Stage:")
    for stage, count in summary["deals_by_stage"].items():
        print(f"  {stage}: {count}")
    
    print(f"\nUsers by Role:")
    for role, count in summary["users_by_role"].items():
        print(f"  {role}: {count}")

if __name__ == "__main__":
    main()
