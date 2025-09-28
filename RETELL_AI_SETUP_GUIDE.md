# 🎙️ Retell AI Integration Setup Guide

## 🚀 Quick Start

### 1. Get Retell AI API Key
1. Visit [https://retellai.com](https://retellai.com)
2. Sign up for an account
3. Go to API Keys section
4. Create a new API key
5. Copy the API key

### 2. Set Environment Variables
```bash
# Windows PowerShell
$env:RETELL_AI_API_KEY="your_api_key_here"
$env:WEBHOOK_BASE_URL="https://your-domain.com"  # Optional

# Windows Command Prompt
set RETELL_AI_API_KEY=your_api_key_here
set WEBHOOK_BASE_URL=https://your-domain.com

# Linux/Mac
export RETELL_AI_API_KEY="your_api_key_here"
export WEBHOOK_BASE_URL="https://your-domain.com"
```

### 3. Start the Server
```bash
python working_app.py
```

### 4. Test the Integration
Visit: http://localhost:8000/docs

## 🎯 Demo Scenarios

The system comes with 4 pre-configured demo scenarios:

### 1. Sales Outbound Call
- **Purpose**: Generate leads and qualify prospects
- **Voice**: Professional female (Sarah Chen)
- **Duration**: Up to 15 minutes
- **Features**: Lead qualification, pain point discovery

### 2. Customer Support Call
- **Purpose**: Resolve customer issues
- **Voice**: Friendly male (Alex Rodriguez)
- **Duration**: Up to 20 minutes
- **Features**: Issue resolution, step-by-step solutions

### 3. Lead Qualification Call
- **Purpose**: Qualify leads for sales follow-up
- **Voice**: Professional male (Michael Johnson)
- **Duration**: Up to 10 minutes
- **Features**: Needs assessment, budget evaluation

### 4. Appointment Booking Call
- **Purpose**: Schedule demos and meetings
- **Voice**: Professional female (Jessica Williams)
- **Duration**: Up to 5 minutes
- **Features**: Calendar scheduling, confirmation

## 🛠️ API Endpoints

### Voices
- `GET /api/conversational-ai/voices` - Get available voices
- `GET /api/conversational-ai/scenarios` - Get demo scenarios

### Agents
- `GET /api/conversational-ai/agents` - List all agents
- `POST /api/conversational-ai/agents` - Create new agent
- `GET /api/conversational-ai/agents/{agent_id}` - Get specific agent
- `PUT /api/conversational-ai/agents/{agent_id}` - Update agent
- `DELETE /api/conversational-ai/agents/{agent_id}` - Delete agent

### Calls
- `GET /api/conversational-ai/calls` - List call history
- `POST /api/conversational-ai/calls` - Create new call
- `GET /api/conversational-ai/calls/{call_id}` - Get call details

### Analytics
- `GET /api/conversational-ai/analytics` - Get call analytics

### Demo Setup
- `POST /api/conversational-ai/demo/create-agents` - Create demo agents

## 🎨 Frontend Interface

Access the conversational AI management interface at:
- Navigate to the ConversationalAI page in your frontend
- Create demo agents with one click
- Test calls with real phone numbers
- View call history and analytics

## 💰 Cost Information

- **Retell AI Pricing**: $0.07-0.08 per minute
- **Free Trial**: 60 minutes included
- **Demo Costs**: 
  - 100 demo calls (5 min avg) = ~$35-40
  - 1000 calls/month = ~$350-400

## 🔧 Configuration

### Agent Configuration
Each agent can be customized with:
- Voice selection
- System prompts
- Call duration limits
- End call phrases
- Webhook URLs

### Call Metadata
Calls can include:
- Lead/contact associations
- Custom metadata
- CRM integration
- User tracking

## 🚨 Troubleshooting

### Common Issues

1. **"RETELL_AI_API_KEY not found"**
   - Set the environment variable correctly
   - Restart the server after setting

2. **"0 voices available"**
   - Check API key is valid
   - Verify Retell AI account is active

3. **"Failed to create agent"**
   - Check API key permissions
   - Verify webhook URL is accessible

### Testing Commands

```bash
# Test the integration
python test_retell_ai.py

# Check API endpoints
curl http://localhost:8000/api/conversational-ai/voices
curl http://localhost:8000/api/conversational-ai/scenarios

# Create demo agents
curl -X POST http://localhost:8000/api/conversational-ai/demo/create-agents
```

## 📞 Demo Phone Numbers

For testing, you can use:
- Your own phone number
- Test numbers provided by Retell AI
- Twilio test numbers

## 🎯 Client Demo Script

1. **Show Available Voices** - Display professional voice options
2. **Create Demo Agents** - One-click setup of all scenarios
3. **Make Test Call** - Demonstrate real phone call
4. **Show Analytics** - Display call metrics and costs
5. **CRM Integration** - Link calls to leads/contacts

## 🔗 Useful Links

- [Retell AI Documentation](https://docs.retellai.com)
- [Retell AI Pricing](https://retellai.com/pricing)
- [API Reference](http://localhost:8000/docs)
- [Frontend Interface](http://localhost:3000) (when running)

## ✅ Success Checklist

- [ ] Retell AI API key set
- [ ] Server running without errors
- [ ] API endpoints responding
- [ ] Demo agents created
- [ ] Test call made successfully
- [ ] Frontend interface accessible
- [ ] Analytics working
- [ ] CRM integration functional
