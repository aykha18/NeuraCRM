"""
Specialized Sales Assistant Prompts
Optimized prompts for different sales scenarios and use cases
"""

class SalesPrompts:
    """Collection of optimized prompts for sales assistant"""
    
    @staticmethod
    def get_system_prompt(org_name: str, user_name: str, user_role: str) -> str:
        """Get the main system prompt for the sales assistant"""
        return f"""You are an advanced AI Sales Assistant for {org_name}. You are helping {user_name}, a {user_role}.

## Your Expertise
- Lead qualification and scoring
- Deal progression and pipeline management
- Email personalization and automation
- Sales strategy and tactics
- Customer relationship management
- Revenue optimization

## Your Capabilities
- Access to comprehensive CRM data (contacts, leads, deals, activities)
- Email template generation and personalization
- Pipeline analysis and forecasting
- Lead scoring and qualification
- Follow-up scheduling and reminders
- Sales insights and recommendations

## Your Approach
1. **Data-Driven**: Always base recommendations on actual CRM data
2. **Proactive**: Suggest actions and identify opportunities
3. **Personalized**: Tailor responses to the specific user and context
4. **Actionable**: Provide specific, implementable recommendations
5. **Strategic**: Think beyond immediate tasks to long-term success

## Response Guidelines
- Be conversational but professional
- Provide specific examples and data points
- Suggest concrete next steps
- Ask clarifying questions when needed
- Use available functions to gather detailed information
- Generate personalized emails when appropriate

## Context Awareness
- Consider the user's role and permissions
- Respect organizational boundaries
- Focus on relevant metrics and KPIs
- Prioritize high-value opportunities

You have access to all CRM functions. Use them to provide the most helpful and accurate assistance possible."""

    @staticmethod
    def get_lead_qualification_prompt() -> str:
        """Prompt for lead qualification analysis"""
        return """Analyze this lead and provide a comprehensive qualification assessment:

Lead Data: {lead_data}

Provide:
1. **Lead Score Analysis**: Current score and factors
2. **Qualification Status**: Hot/Warm/Cold with reasoning
3. **Buying Signals**: Indicators of purchase intent
4. **Risk Factors**: Potential obstacles or concerns
5. **Next Steps**: Specific actions to advance the lead
6. **Timeline Estimate**: Expected sales cycle length
7. **Resource Requirements**: What's needed to close

Be specific and data-driven in your analysis."""

    @staticmethod
    def get_deal_strategy_prompt() -> str:
        """Prompt for deal strategy development"""
        return """Develop a comprehensive strategy for this deal:

Deal Data: {deal_data}

Provide:
1. **Current Status**: Where the deal stands in the sales process
2. **Key Stakeholders**: Decision makers and influencers
3. **Competitive Position**: Strengths and weaknesses vs competitors
4. **Value Proposition**: Key benefits for this specific prospect
5. **Objection Handling**: Anticipated objections and responses
6. **Closing Strategy**: Specific tactics to move to close
7. **Timeline**: Critical milestones and deadlines
8. **Risk Mitigation**: Potential deal risks and mitigation plans

Focus on actionable strategies that increase win probability."""

    @staticmethod
    def get_email_personalization_prompt() -> str:
        """Prompt for email personalization"""
        return """Create a highly personalized email based on this context:

Template: {template}
Recipient: {recipient_data}
Deal/Lead Context: {entity_data}
Recent Activities: {activities}

Personalization Guidelines:
1. **Tone Matching**: Match the recipient's communication style
2. **Context Awareness**: Reference specific interactions or data points
3. **Value Focus**: Emphasize relevant benefits and outcomes
4. **Urgency Creation**: Include appropriate urgency without being pushy
5. **Call-to-Action**: Clear, specific next steps
6. **Relationship Building**: Strengthen the professional relationship

Make the email feel like it was written specifically for this person and situation."""

    @staticmethod
    def get_pipeline_analysis_prompt() -> str:
        """Prompt for pipeline analysis"""
        return """Analyze this sales pipeline and provide strategic insights:

Pipeline Data: {pipeline_data}
User Performance: {user_performance}
Organization Metrics: {org_metrics}

Analysis Areas:
1. **Pipeline Health**: Overall strength and weaknesses
2. **Stage Analysis**: Bottlenecks and opportunities at each stage
3. **Revenue Forecasting**: Realistic revenue projections
4. **Conversion Rates**: Stage-to-stage conversion analysis
5. **Deal Velocity**: Average time in each stage
6. **Resource Allocation**: Where to focus efforts
7. **Risk Assessment**: Deals at risk and mitigation strategies
8. **Growth Opportunities**: Areas for pipeline expansion

Provide specific, actionable recommendations for improvement."""

    @staticmethod
    def get_follow_up_strategy_prompt() -> str:
        """Prompt for follow-up strategy development"""
        return """Develop an optimal follow-up strategy for this entity:

Entity Data: {entity_data}
Last Interaction: {last_interaction}
Context: {context}

Strategy Components:
1. **Timing**: When to follow up (immediate, 24h, 48h, 1 week)
2. **Channel**: Email, phone, LinkedIn, in-person
3. **Message**: Key points to communicate
4. **Value Add**: What value to provide in the follow-up
5. **Next Steps**: Clear action items for the prospect
6. **Escalation**: When and how to escalate if needed
7. **Documentation**: What to track and record

Consider the prospect's preferences, buying stage, and recent interactions."""

    @staticmethod
    def get_objection_handling_prompt() -> str:
        """Prompt for objection handling"""
        return """Help handle this sales objection:

Objection: {objection}
Deal Context: {deal_data}
Prospect Profile: {prospect_data}

Provide:
1. **Objection Analysis**: Root cause and underlying concerns
2. **Response Strategy**: How to address the objection
3. **Talking Points**: Specific points to make
4. **Proof Points**: Data, case studies, or examples to use
5. **Alternative Approaches**: Different ways to address the concern
6. **Follow-up Actions**: Next steps after handling the objection
7. **Prevention**: How to avoid this objection in future deals

Be empathetic and solution-focused in your approach."""

    @staticmethod
    def get_upsell_opportunity_prompt() -> str:
        """Prompt for identifying upsell opportunities"""
        return """Identify upsell opportunities for this customer:

Customer Data: {customer_data}
Current Products/Services: {current_products}
Usage Data: {usage_data}
Organization Context: {org_context}

Analysis:
1. **Current Value**: What the customer is currently getting
2. **Growth Potential**: Areas where they could expand
3. **Pain Points**: Problems that additional products could solve
4. **Budget Indicators**: Signs of available budget
5. **Decision Makers**: Who would be involved in upsell decisions
6. **Timing**: When to approach with upsell
7. **Value Proposition**: Benefits of the additional products
8. **Approach Strategy**: How to present the upsell opportunity

Focus on genuine value addition, not just revenue generation."""

    @staticmethod
    def get_competitor_analysis_prompt() -> str:
        """Prompt for competitive analysis"""
        return """Analyze the competitive landscape for this deal:

Deal Context: {deal_data}
Known Competitors: {competitors}
Our Position: {our_position}

Analysis:
1. **Competitive Landscape**: Who we're competing against
2. **Our Advantages**: Key differentiators and strengths
3. **Competitor Weaknesses**: Areas where competitors fall short
4. **Battle Cards**: Key talking points against each competitor
5. **Proof Points**: Evidence of our superiority
6. **Risk Mitigation**: How to counter competitor advantages
7. **Win Strategy**: Specific tactics to win against competition
8. **Pricing Strategy**: How to position on price vs value

Be honest about our position while highlighting our strengths."""

    @staticmethod
    def get_sales_forecasting_prompt() -> str:
        """Prompt for sales forecasting"""
        return """Provide a sales forecast based on this data:

Pipeline Data: {pipeline_data}
Historical Performance: {historical_data}
Market Conditions: {market_conditions}
Seasonal Factors: {seasonal_factors}

Forecast Components:
1. **Revenue Forecast**: Expected revenue by time period
2. **Deal Probability**: Likelihood of closing each deal
3. **Timeline Predictions**: When deals are likely to close
4. **Risk Factors**: What could impact the forecast
5. **Confidence Levels**: How confident we are in predictions
6. **Scenario Planning**: Best case, worst case, most likely
7. **Action Items**: What to do to improve forecast accuracy
8. **Gap Analysis**: Difference between forecast and targets

Use data-driven analysis with appropriate confidence intervals."""

    @staticmethod
    def get_customer_success_prompt() -> str:
        """Prompt for customer success and retention"""
        return """Develop a customer success strategy for this account:

Customer Data: {customer_data}
Usage Metrics: {usage_metrics}
Satisfaction Indicators: {satisfaction_data}
Renewal Timeline: {renewal_timeline}

Strategy Elements:
1. **Health Score**: Overall customer health assessment
2. **Success Metrics**: Key indicators of customer success
3. **Risk Factors**: Potential churn indicators
4. **Engagement Plan**: How to increase customer engagement
5. **Value Realization**: Ensuring customer gets full value
6. **Expansion Opportunities**: Growth within the account
7. **Retention Tactics**: Specific actions to improve retention
8. **Success Stories**: How to leverage this customer for references

Focus on long-term customer value and success."""

    @staticmethod
    def get_meeting_preparation_prompt() -> str:
        """Prompt for meeting preparation"""
        return """Prepare for this sales meeting:

Meeting Details: {meeting_details}
Attendees: {attendees}
Deal Context: {deal_context}
Previous Interactions: {previous_interactions}

Preparation Checklist:
1. **Meeting Objectives**: Clear goals for the meeting
2. **Agenda**: Suggested meeting structure
3. **Key Questions**: Important questions to ask
4. **Talking Points**: Main points to cover
5. **Materials Needed**: Documents, demos, or resources
6. **Objection Preparation**: Anticipated objections and responses
7. **Next Steps**: Desired outcomes and follow-up actions
8. **Success Metrics**: How to measure meeting success

Be thorough and strategic in your preparation."""

    @staticmethod
    def get_lead_nurturing_prompt() -> str:
        """Prompt for lead nurturing strategy"""
        return """Develop a lead nurturing strategy for this lead:

Lead Profile: {lead_profile}
Engagement History: {engagement_history}
Content Preferences: {content_preferences}
Buying Stage: {buying_stage}

Nurturing Plan:
1. **Content Strategy**: What content to share and when
2. **Communication Cadence**: How often to reach out
3. **Channel Mix**: Email, social, phone, events
4. **Personalization**: How to make each touchpoint relevant
5. **Value Delivery**: What value to provide at each stage
6. **Progression Triggers**: What indicates readiness to advance
7. **Handoff Criteria**: When to pass to sales
8. **Success Metrics**: How to measure nurturing effectiveness

Focus on building relationships and providing value over time."""
