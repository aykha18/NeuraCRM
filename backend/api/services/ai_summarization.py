"""
AI Summarization Service for Support Tickets
Uses OpenAI GPT models to generate concise summaries of support tickets and their comments.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AISummarizationService:
    """Service for AI-powered summarization of support tickets"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "500"))

        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.openai_api_key)

    async def summarize_support_ticket(
        self,
        ticket_data: Dict[str, Any],
        comments: List[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Generate an AI summary of a support ticket including its description and comments.

        Args:
            ticket_data: Dictionary containing ticket information
            comments: List of comment dictionaries

        Returns:
            AI-generated summary or None if summarization fails
        """
        if not self.client:
            logger.error("OpenAI client not initialized - missing API key")
            return None

        try:
            # Build the content to summarize
            content_parts = []

            # Add ticket information
            ticket_info = f"""
Ticket #{ticket_data.get('ticket_number', 'Unknown')}
Title: {ticket_data.get('title', 'No title')}
Priority: {ticket_data.get('priority', 'medium')}
Category: {ticket_data.get('category', 'general')}
Status: {ticket_data.get('status', 'open')}

Description:
{ticket_data.get('description', 'No description provided')}
"""
            content_parts.append(ticket_info)

            # Add comments if available
            if comments and len(comments) > 0:
                content_parts.append("\nComments:")
                for i, comment in enumerate(comments, 1):
                    author = comment.get('author_name', 'Unknown')
                    content = comment.get('content', '').strip()
                    if content:
                        content_parts.append(f"\n{i}. {author}: {content}")

            full_content = "\n".join(content_parts)

            # Create the summarization prompt
            prompt = f"""
Please provide a concise summary of this customer support ticket. Focus on:

1. The main issue or problem reported
2. Key details and context provided
3. Any solutions attempted or suggested
4. Current status and next steps
5. Customer sentiment (if evident)

Keep the summary under 200 words and make it actionable for support agents.

Ticket Content:
{full_content}
"""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert support ticket analyst. Provide clear, concise summaries that help support teams understand and resolve customer issues efficiently."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent summaries
            )

            summary = response.choices[0].message.content.strip()

            if summary:
                logger.info(f"Successfully generated AI summary for ticket #{ticket_data.get('ticket_number')}")
                return summary
            else:
                logger.warning("OpenAI returned empty summary")
                return None

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            return None
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in AI summarization: {str(e)}")
            return None

    async def update_ticket_summary(
        self,
        ticket_id: int,
        db_session
    ) -> bool:
        """
        Update the AI summary for a specific ticket by fetching current data and generating a new summary.

        Args:
            ticket_id: The ID of the ticket to summarize
            db_session: Database session

        Returns:
            True if summary was updated successfully, False otherwise
        """
        try:
            from api.models import SupportTicket, SupportComment

            # Fetch ticket data
            ticket = db_session.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
            if not ticket:
                logger.error(f"Ticket {ticket_id} not found")
                return False

            # Fetch comments for this ticket
            comments = db_session.query(SupportComment).filter(
                SupportComment.ticket_id == ticket_id
            ).order_by(SupportComment.created_at.asc()).all()

            # Convert to dictionaries for the summarization function
            ticket_data = {
                'ticket_number': ticket.ticket_number,
                'title': ticket.title,
                'priority': ticket.priority,
                'category': ticket.category,
                'status': ticket.status,
                'description': ticket.description
            }

            comments_data = []
            for comment in comments:
                comments_data.append({
                    'author_name': comment.author_name,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat() if comment.created_at else None
                })

            # Generate summary
            summary = await self.summarize_support_ticket(ticket_data, comments_data)

            if summary:
                # Update the ticket with the new summary
                ticket.ai_summary = summary
                ticket.ai_summary_generated_at = datetime.utcnow()
                ticket.ai_summary_model = self.model

                db_session.commit()
                logger.info(f"Updated AI summary for ticket {ticket.ticket_number}")
                return True
            else:
                logger.warning(f"Failed to generate summary for ticket {ticket.ticket_number}")
                return False

        except Exception as e:
            logger.error(f"Error updating ticket summary: {str(e)}")
            db_session.rollback()
            return False

    async def summarize_support_ticket_by_id(
        self,
        ticket_id: int,
        db_session
    ) -> Optional[str]:
        """
        Generate an AI summary for a support ticket by ID.

        Args:
            ticket_id: The ID of the ticket to summarize
            db_session: Database session

        Returns:
            AI-generated summary or None if summarization fails
        """
        try:
            from api.models import SupportTicket, SupportComment

            # Fetch ticket data
            ticket = db_session.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
            if not ticket:
                logger.error(f"Ticket {ticket_id} not found")
                return None

            # Fetch comments for this ticket
            comments = db_session.query(SupportComment).filter(
                SupportComment.ticket_id == ticket_id
            ).order_by(SupportComment.created_at.asc()).all()

            # Convert to dictionaries for the summarization function
            ticket_data = {
                'ticket_number': ticket.ticket_number,
                'title': ticket.title,
                'priority': ticket.priority,
                'category': ticket.category,
                'status': ticket.status,
                'description': ticket.description
            }

            comments_data = []
            for comment in comments:
                comments_data.append({
                    'author_name': comment.author_name,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat() if comment.created_at else None
                })

            # Generate summary
            summary = await self.summarize_support_ticket(ticket_data, comments_data)

            if summary:
                # Update the ticket with the new summary
                ticket.ai_summary = summary
                ticket.ai_summary_generated_at = datetime.utcnow()
                ticket.ai_summary_model = self.model

                db_session.commit()
                logger.info(f"Successfully generated and saved AI summary for ticket {ticket.ticket_number}")
                return summary
            else:
                logger.warning(f"Failed to generate summary for ticket {ticket.ticket_number}")
                return None

        except Exception as e:
            logger.error(f"Error summarizing ticket by ID: {str(e)}")
            db_session.rollback()
            return None

    def is_available(self) -> bool:
        """Check if the AI summarization service is available"""
        return self.client is not None

    def get_service_status(self) -> Dict[str, Any]:
        """Get the current status of the AI summarization service"""
        return {
            "available": self.is_available(),
            "model": self.model,
            "max_tokens": self.max_tokens,
            "has_api_key": self.openai_api_key is not None
        }


# Global instance
ai_summarization_service = AISummarizationService()