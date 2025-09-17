/**
 * AI Features Showcase Page
 * - Displays implemented and upcoming AI features in card format
 * - 4 cards per row with detailed modals
 * - Shows how each feature works and benefits business
 */
import { useState } from "react";
import { 
  Brain, 
  Target, 
  MessageSquare, 
  Mail, 
  TrendingUp, 
  Users, 
  // BarChart3, 
  Zap,
  Clock,
  CheckCircle,
  ArrowRight,
  X,
  Lightbulb,
  Shield,
  Activity,
  PieChart,
  Crown,
  Mic,
  FileText,
  Globe,
  BarChart,
  BrainCircuit,
  Bot,
  Sparkles
} from "lucide-react";
import AIChat from "../components/AIChat";

interface AIFeature {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: "implemented" | "upcoming" | "premium";
  category: "lead-management" | "communication" | "analytics" | "automation";
  details: {
    howItWorks: string;
    businessBenefits: string[];
    technicalDetails: string;
    useCases: string[];
  };
}

const aiFeatures: AIFeature[] = [
  {
    id: "lead-scoring",
    title: "AI Lead Scoring",
    description: "Automatically score leads based on behavior, engagement, and company data to prioritize high-value prospects.",
    icon: <Target className="w-8 h-8" />,
    status: "implemented",
    category: "lead-management",
    details: {
      howItWorks: "Our AI analyzes multiple data points including email engagement, website activity, company size, industry, and interaction patterns to assign a score from 0-100. The algorithm learns from your historical conversion data to improve accuracy over time.",
      businessBenefits: [
        "Focus sales efforts on high-probability leads",
        "Reduce time spent on low-value prospects",
        "Improve conversion rates by 40-60%",
        "Better resource allocation and forecasting"
      ],
      technicalDetails: "Uses machine learning models trained on your CRM data, integrates with email tracking, website analytics, and company databases. Updates scores in real-time as new data becomes available.",
      useCases: [
        "Prioritizing daily lead follow-ups",
        "Segmenting leads for different sales approaches",
        "Identifying upsell opportunities",
        "Predicting deal closure probability"
      ]
    }
  },
  {
    id: "email-automation",
    title: "Smart Email Automation",
    description: "AI-powered email campaigns with personalization, timing optimization, and behavioral triggers.",
    icon: <Mail className="w-8 h-8" />,
    status: "implemented",
    category: "automation",
    details: {
      howItWorks: "The system analyzes recipient behavior patterns, optimal sending times, and content preferences to automatically send personalized emails. It uses A/B testing to optimize subject lines, content, and timing for maximum engagement.",
      businessBenefits: [
        "Increase email open rates by 25-35%",
        "Reduce manual email management by 80%",
        "Improve lead nurturing efficiency",
        "Scale personalized communication"
      ],
      technicalDetails: "Integrates with email providers, uses natural language processing for content personalization, machine learning for timing optimization, and behavioral analytics for trigger-based automation.",
      useCases: [
        "Welcome series for new leads",
        "Follow-up sequences after meetings",
        "Re-engagement campaigns for cold leads",
        "Product announcement campaigns"
      ]
    }
  },
  {
    id: "chat-assistant",
    title: "AI Chat Assistant",
    description: "Intelligent chatbot that handles customer inquiries, qualifies leads, and provides instant support.",
    icon: <MessageSquare className="w-8 h-8" />,
    status: "implemented",
    category: "communication",
    details: {
      howItWorks: "The AI assistant uses natural language processing to understand customer queries and provide relevant responses. It can qualify leads, schedule meetings, answer FAQs, and escalate complex issues to human agents.",
      businessBenefits: [
        "Provide 24/7 customer support",
        "Qualify leads automatically",
        "Reduce response time to seconds",
        "Handle multiple conversations simultaneously"
      ],
      technicalDetails: "Built on advanced language models, integrates with your CRM, calendar, and knowledge base. Continuously learns from conversations to improve accuracy and response quality.",
      useCases: [
        "Website live chat support",
        "Lead qualification and scheduling",
        "FAQ handling and troubleshooting",
        "Meeting scheduling and reminders"
      ]
    }
  },
  {
    id: "predictive-analytics",
    title: "Predictive Analytics",
    description: "Forecast sales trends, identify opportunities, and predict customer behavior using AI algorithms.",
    icon: <TrendingUp className="w-8 h-8" />,
    status: "implemented",
    category: "analytics",
    details: {
      howItWorks: "Advanced machine learning models analyze historical sales data, customer behavior patterns, market trends, and external factors to predict future outcomes. The system provides actionable insights and recommendations.",
      businessBenefits: [
        "Accurate sales forecasting",
        "Identify at-risk customers early",
        "Optimize pricing strategies",
        "Improve inventory management"
      ],
      technicalDetails: "Uses time-series analysis, regression models, and deep learning algorithms. Integrates with multiple data sources including CRM, ERP, and external market data for comprehensive predictions.",
      useCases: [
        "Monthly/quarterly sales forecasting",
        "Customer churn prediction",
        "Revenue optimization",
        "Market opportunity identification"
      ]
    }
  },
  {
    id: "sentiment-analysis",
    title: "Sentiment Analysis",
    description: "Analyze customer emotions and satisfaction levels from emails, chats, and social media interactions.",
    icon: <Brain className="w-8 h-8" />,
    status: "upcoming",
    category: "analytics",
    details: {
      howItWorks: "Natural language processing algorithms analyze text content to determine emotional tone, sentiment polarity, and customer satisfaction levels. Provides real-time insights into customer mood and satisfaction.",
      businessBenefits: [
        "Identify unhappy customers early",
        "Improve customer satisfaction scores",
        "Optimize communication tone",
        "Reduce customer churn"
      ],
      technicalDetails: "Uses transformer-based models trained on customer communication data. Analyzes emails, chat transcripts, social media mentions, and survey responses for comprehensive sentiment tracking.",
      useCases: [
        "Customer satisfaction monitoring",
        "Support ticket prioritization",
        "Product feedback analysis",
        "Brand reputation monitoring"
      ]
    }
  },
  {
    id: "smart-scheduling",
    title: "AI Meeting Scheduler",
    description: "Intelligent scheduling that optimizes meeting times based on availability, time zones, and preferences.",
    icon: <Clock className="w-8 h-8" />,
    status: "upcoming",
    category: "automation",
    details: {
      howItWorks: "The AI analyzes calendar availability, time zone differences, meeting preferences, and historical scheduling patterns to suggest optimal meeting times. Automatically handles scheduling conflicts and sends reminders.",
      businessBenefits: [
        "Reduce scheduling back-and-forth by 90%",
        "Optimize meeting attendance rates",
        "Save 2-3 hours per week on scheduling",
        "Improve customer experience"
      ],
      technicalDetails: "Integrates with major calendar platforms (Google Calendar, Outlook), uses machine learning for preference learning, and provides smart conflict resolution and time zone handling.",
      useCases: [
        "Sales meeting scheduling",
        "Customer discovery calls",
        "Team meeting coordination",
        "Client consultation booking"
      ]
    }
  },
  {
    id: "competitor-analysis",
    title: "Competitor Intelligence",
    description: "AI-powered competitive analysis that monitors competitors' activities, pricing, and market positioning.",
    icon: <Shield className="w-8 h-8" />,
    status: "upcoming",
    category: "analytics",
    details: {
      howItWorks: "Continuously monitors competitor websites, social media, pricing changes, and market activities. Uses web scraping, social media analysis, and market data to provide actionable competitive insights.",
      businessBenefits: [
        "Stay ahead of competitor moves",
        "Optimize pricing strategies",
        "Identify market opportunities",
        "Improve competitive positioning"
      ],
      technicalDetails: "Uses web scraping, social media APIs, price monitoring tools, and machine learning for pattern recognition. Provides real-time alerts and comprehensive competitive reports.",
      useCases: [
        "Pricing strategy optimization",
        "Market positioning analysis",
        "Product feature comparison",
        "Marketing campaign monitoring"
      ]
    }
  },
  {
    id: "sales-coaching",
    title: "AI Sales Coach",
    description: "Personalized coaching and training recommendations based on sales performance and conversation analysis.",
    icon: <Users className="w-8 h-8" />,
    status: "upcoming",
    category: "lead-management",
    details: {
      howItWorks: "Analyzes sales calls, emails, and performance metrics to identify improvement areas. Provides personalized coaching tips, conversation suggestions, and training recommendations for each sales rep.",
      businessBenefits: [
        "Improve sales team performance by 30%",
        "Reduce training time and costs",
        "Standardize best practices",
        "Accelerate new hire ramp-up"
      ],
      technicalDetails: "Uses speech-to-text, conversation analysis, performance tracking, and machine learning to provide personalized insights and recommendations for each sales representative.",
      useCases: [
        "New hire training and onboarding",
        "Performance improvement coaching",
        "Best practice identification",
        "Sales methodology optimization"
      ]
    }
  },
  // Premium Features
  {
    id: "conversation-intelligence",
    title: "Conversation Intelligence",
    description: "Real-time analysis of sales calls and customer interactions to extract insights and improve performance.",
    icon: <Mic className="w-8 h-8" />,
    status: "premium",
    category: "analytics",
    details: {
      howItWorks: "Advanced speech recognition and natural language processing analyze sales calls in real-time, extracting key insights, objection patterns, and conversation quality metrics. Provides instant feedback and coaching recommendations.",
      businessBenefits: [
        "Improve sales conversion rates by 25-40%",
        "Identify winning conversation patterns",
        "Reduce training time for new reps",
        "Optimize sales scripts and approaches"
      ],
      technicalDetails: "Uses real-time speech-to-text, sentiment analysis, keyword extraction, and machine learning to analyze call patterns. Integrates with CRM and provides detailed conversation analytics.",
      useCases: [
        "Sales call analysis and coaching",
        "Objection handling improvement",
        "Script optimization",
        "Performance benchmarking"
      ]
    }
  },
  {
    id: "smart-nurturing",
    title: "Smart Nurturing",
    description: "Automated lead nurturing sequences that adapt based on behavior, engagement, and conversion probability.",
    icon: <BrainCircuit className="w-8 h-8" />,
    status: "premium",
    category: "automation",
    details: {
      howItWorks: "AI-driven nurturing campaigns that automatically adapt content, timing, and channels based on lead behavior, engagement levels, and conversion signals. Creates personalized journeys for each prospect.",
      businessBenefits: [
        "Increase lead-to-customer conversion by 50%",
        "Reduce manual nurturing tasks by 90%",
        "Improve lead engagement rates",
        "Scale personalized communication"
      ],
      technicalDetails: "Uses behavioral analytics, machine learning for journey optimization, multi-channel automation, and real-time decision making to create dynamic nurturing sequences.",
      useCases: [
        "Lead nurturing campaigns",
        "Customer onboarding sequences",
        "Re-engagement programs",
        "Upsell/cross-sell automation"
      ]
    }
  },
  {
    id: "document-processing",
    title: "Document Processing",
    description: "OCR and AI-powered data extraction from contracts, forms, and business documents with intelligent classification.",
    icon: <FileText className="w-8 h-8" />,
    status: "premium",
    category: "automation",
    details: {
      howItWorks: "Advanced OCR and natural language processing extract key information from contracts, invoices, forms, and other business documents. Automatically classifies documents and populates CRM fields.",
      businessBenefits: [
        "Reduce manual data entry by 80%",
        "Improve data accuracy and consistency",
        "Accelerate document processing",
        "Enhance compliance and audit trails"
      ],
      technicalDetails: "Uses state-of-the-art OCR, document classification, entity extraction, and machine learning to process various document types and extract structured data automatically.",
      useCases: [
        "Contract analysis and data extraction",
        "Invoice processing and approval",
        "Form data capture and validation",
        "Document classification and routing"
      ]
    }
  },
  {
    id: "voice-intelligence",
    title: "Voice Intelligence",
    description: "Advanced call analysis with emotion detection, speaker identification, and real-time insights.",
    icon: <Mic className="w-8 h-8" />,
    status: "premium",
    category: "analytics",
    details: {
      howItWorks: "Real-time voice analysis detects emotions, speaker identification, call quality metrics, and provides instant insights during and after calls. Identifies patterns and opportunities for improvement.",
      businessBenefits: [
        "Improve call quality and outcomes",
        "Identify customer emotions and satisfaction",
        "Optimize sales team performance",
        "Enhance customer experience"
      ],
      technicalDetails: "Uses voice biometrics, emotion recognition, speaker diarization, and real-time analytics to provide comprehensive call intelligence and actionable insights.",
      useCases: [
        "Sales call quality analysis",
        "Customer service optimization",
        "Emotion detection and response",
        "Call center performance monitoring"
      ]
    }
  },
  {
    id: "market-intelligence",
    title: "Market Intelligence",
    description: "External data integration and market analysis to identify opportunities and competitive threats.",
    icon: <Globe className="w-8 h-8" />,
    status: "premium",
    category: "analytics",
    details: {
      howItWorks: "Integrates external data sources including market reports, social media, news, and industry databases to provide comprehensive market insights and competitive intelligence.",
      businessBenefits: [
        "Identify new market opportunities",
        "Stay ahead of industry trends",
        "Optimize pricing and positioning",
        "Improve strategic decision making"
      ],
      technicalDetails: "Uses data aggregation, natural language processing, trend analysis, and machine learning to process multiple external data sources and provide actionable market intelligence.",
      useCases: [
        "Market opportunity identification",
        "Competitive threat monitoring",
        "Industry trend analysis",
        "Strategic planning and forecasting"
      ]
    }
  },
  {
    id: "advanced-forecasting",
    title: "Advanced Forecasting",
    description: "ML-powered sales forecasting with multiple models and scenario planning for accurate predictions.",
    icon: <BarChart className="w-8 h-8" />,
    status: "premium",
    category: "analytics",
    details: {
      howItWorks: "Advanced machine learning models analyze historical data, market conditions, seasonality, and external factors to provide accurate sales forecasts with confidence intervals and scenario planning.",
      businessBenefits: [
        "Improve forecast accuracy by 30-50%",
        "Better resource planning and allocation",
        "Identify revenue risks and opportunities",
        "Optimize sales strategies"
      ],
      technicalDetails: "Uses ensemble learning, time series analysis, external data integration, and scenario modeling to provide comprehensive forecasting with multiple prediction horizons.",
      useCases: [
        "Sales pipeline forecasting",
        "Revenue planning and budgeting",
        "Resource allocation optimization",
        "Risk assessment and mitigation"
      ]
    }
  }
];

export default function AIFeatures() {
  const [selectedFeature, setSelectedFeature] = useState<AIFeature | null>(null);
  const [filter, setFilter] = useState<"all" | "implemented" | "upcoming" | "premium">("all");
  const [showAIChat, setShowAIChat] = useState(false);

  const filteredFeatures = aiFeatures.filter(feature => 
    filter === "all" || feature.status === filter
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "implemented":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
      case "upcoming":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
      case "premium":
        return "bg-gradient-to-r from-amber-100 to-yellow-100 text-amber-800 dark:from-amber-900/30 dark:to-yellow-900/30 dark:text-amber-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "implemented":
        return <CheckCircle className="w-4 h-4" />;
      case "upcoming":
        return <Clock className="w-4 h-4" />;
      case "premium":
        return <Crown className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          AI Features Showcase
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
          Discover how AI is transforming your CRM experience. Explore implemented features, upcoming capabilities, and premium features available on request.
        </p>
        
        {/* AI Assistant Button */}
        <div className="flex gap-4 items-center mb-6">
          <button
            onClick={() => setShowAIChat(true)}
            className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 transform hover:scale-105 shadow-lg"
          >
            <Bot className="h-5 w-5" />
            <span className="font-medium">Try AI Assistant</span>
            <Sparkles className="h-4 w-4" />
          </button>
          <p className="text-sm text-gray-500">
            Chat with our AI assistant to get personalized sales insights
          </p>
        </div>
        
        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 rounded-full font-medium transition ${
              filter === "all"
                ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white"
                : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            All Features
          </button>
          <button
            onClick={() => setFilter("implemented")}
            className={`px-4 py-2 rounded-full font-medium transition ${
              filter === "implemented"
                ? "bg-gradient-to-r from-green-600 to-emerald-600 text-white"
                : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            Implemented
          </button>
          <button
            onClick={() => setFilter("upcoming")}
            className={`px-4 py-2 rounded-full font-medium transition ${
              filter === "upcoming"
                ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white"
                : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            Upcoming
          </button>
          <button
            onClick={() => setFilter("premium")}
            className={`px-4 py-2 rounded-full font-medium transition ${
              filter === "premium"
                ? "bg-gradient-to-r from-amber-500 to-yellow-500 text-white"
                : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            Premium Features
          </button>
        </div>

        {/* Premium Features Notice */}
        {filter === "premium" && (
          <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border border-amber-200 dark:border-amber-700 rounded-lg">
            <div className="flex items-center gap-3">
              <Crown className="w-6 h-6 text-amber-600" />
              <div>
                <h3 className="font-semibold text-amber-800 dark:text-amber-300">Premium Features Available on Request</h3>
                <p className="text-amber-700 dark:text-amber-400 text-sm">
                  These advanced AI features are available for custom development. Contact us to discuss implementation options and pricing.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {filteredFeatures.map((feature) => (
          <div
            key={feature.id}
            className={`bg-white dark:bg-gray-900 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300 cursor-pointer group ${
              feature.status === "premium" ? "ring-2 ring-amber-200 dark:ring-amber-700" : ""
            }`}
            onClick={() => setSelectedFeature(feature)}
          >
            {/* Icon and Status */}
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl ${
                feature.status === "premium" 
                  ? "bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30"
                  : "bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30"
              }`}>
                {feature.icon}
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusColor(feature.status)}`}>
                {getStatusIcon(feature.status)}
                {feature.status === "premium" ? "Premium" : feature.status}
              </span>
            </div>

            {/* Content */}
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition">
              {feature.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
              {feature.description}
            </p>

            {/* Learn More Button */}
            <div className="flex items-center text-purple-600 dark:text-purple-400 font-medium text-sm group-hover:gap-2 transition-all">
              Learn More
              <ArrowRight className="w-4 h-4" />
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredFeatures.length === 0 && (
        <div className="text-center py-12">
          <Lightbulb className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No features found</h3>
          <p className="text-gray-600 dark:text-gray-300">Try adjusting your filter to see more features.</p>
        </div>
      )}

      {/* Feature Detail Modal */}
      {selectedFeature && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl ${
                    selectedFeature.status === "premium" 
                      ? "bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30"
                      : "bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30"
                  }`}>
                    {selectedFeature.icon}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {selectedFeature.title}
                    </h2>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedFeature.status)}`}>
                      {selectedFeature.status === "premium" ? "Premium Feature" : selectedFeature.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedFeature(null)}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Premium Feature Notice */}
              {selectedFeature.status === "premium" && (
                <div className="p-4 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border border-amber-200 dark:border-amber-700 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Crown className="w-5 h-5 text-amber-600" />
                    <div>
                      <h4 className="font-semibold text-amber-800 dark:text-amber-300">Premium Feature</h4>
                      <p className="text-amber-700 dark:text-amber-400 text-sm">
                        This feature is available for custom development. Contact our team to discuss implementation options, pricing, and timeline.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Description */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Overview</h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedFeature.description}</p>
              </div>

              {/* How It Works */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-purple-600" />
                  How It Works
                </h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedFeature.details.howItWorks}</p>
              </div>

              {/* Business Benefits */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  Business Benefits
                </h3>
                <ul className="space-y-2">
                  {selectedFeature.details.businessBenefits.map((benefit, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-600 dark:text-gray-300">{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Use Cases */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-600" />
                  Use Cases
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedFeature.details.useCases.map((useCase, index) => (
                    <div key={index} className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                      <span className="text-gray-700 dark:text-gray-300 text-sm">{useCase}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technical Details */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-orange-600" />
                  Technical Details
                </h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedFeature.details.technicalDetails}</p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
              <button
                onClick={() => setSelectedFeature(null)}
                className="px-6 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Chat Modal */}
      {showAIChat && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">AI Sales Assistant</h2>
              <button
                onClick={() => setShowAIChat(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <AIChat />
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 