import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from backend.ai.sales_assistant_optimized import OptimizedSalesAssistant
from backend.ai.providers.openai_provider import OpenAIProvider
from sqlalchemy.orm import Session

class MockCRMDataAccess:
    """Mock CRM data access layer for testing"""
    def get_lead_context(self, lead_id: int):
        return {
            "id": lead_id,
            "name": "Test Lead",
            "value": 50000,
            "status": "qualified",
            "last_contact": datetime.now().isoformat()
        }

    def get_deal_context(self, deal_id: int):
        return {
            "id": deal_id,
            "value": 100000,
            "stage": "negotiation",
            "decision_date": (datetime.now() + timedelta(days=7)).isoformat()
        }

    def get_pipeline_summary(self):
        return {
            "total_value": 1500000,
            "stages": {
                "prospect": 5,
                "qualification": 3,
                "negotiation": 2,
                "closed_won": 1
            }
        }

    def search_entities(self, query: str, entity_types: list):
        return {
            "contacts": [{"id": 1, "name": "Test Contact"}],
            "leads": [{"id": 123, "name": "Test Lead"}],
            "deals": [{"id": 456, "name": "Test Deal"}]
        }

    def get_email_templates(self, category: str = None):
        return [{
            "id": 789,
            "name": "Follow-Up Template",
            "subject": "Follow up on your inquiry",
            "body": "Dear {{name}}, following up...",
            "category": "follow-up"
        }]

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def assistant(mock_db):
    provider = OpenAIProvider()
    provider.chat_completion = AsyncMock()
    return OptimizedSalesAssistant(
        db=mock_db,
        user_id=1,
        organization_id=1,
        provider=provider
    )

@pytest.mark.asyncio
async def test_lead_qualification(assistant):
    # Test lead qualification conversation flow
    response = await assistant.process_message(
        "Update me on lead 123's status and suggest next steps"
    )
    
    assert "function_calls" in response
    assert any(fc["function"] == "get_lead_details" 
              for fc in response["function_calls"])
    assert "next steps" in response["response"].lower()

@pytest.mark.asyncio
async def test_email_generation(assistant):
    # Test email template generation
    response = await assistant.process_message(
        "Generate a follow-up email for deal 456 using template 789"
    )
    
    assert "generate_email" in [fc["function"] 
                               for fc in response["function_calls"]]
    assert "subject" in response["response"].lower()
    assert "@" in response["response"]  # Check for email format

@pytest.mark.asyncio
async def test_pipeline_analysis(assistant):
    # Test pipeline analysis request
    response = await assistant.process_message(
        "Give me a breakdown of our sales pipeline"
    )
    
    assert "analyze_pipeline" in [fc["function"] 
                                 for fc in response["function_calls"]]
    assert "total value" in response["response"].lower()