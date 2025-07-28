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
  BarChart3, 
  Zap,
  Clock,
  CheckCircle,
  ArrowRight,
  X,
  Lightbulb,
  Shield,
  Activity,
  PieChart
} from "lucide-react";

interface AIFeature {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: "implemented" | "upcoming";
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
    status: "upcoming",
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
  }
];

export default function AIFeatures() {
  const [selectedFeature, setSelectedFeature] = useState<AIFeature | null>(null);
  const [filter, setFilter] = useState<"all" | "implemented" | "upcoming">("all");

  const filteredFeatures = aiFeatures.filter(feature => 
    filter === "all" || feature.status === filter
  );

  const getStatusColor = (status: string) => {
    return status === "implemented" 
      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400" 
      : "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
  };

  const getStatusIcon = (status: string) => {
    return status === "implemented" ? <CheckCircle className="w-4 h-4" /> : <Clock className="w-4 h-4" />;
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          AI Features Showcase
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
          Discover how AI is transforming your CRM experience. Explore implemented features and get a glimpse of what's coming next.
        </p>
        
        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6">
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
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {filteredFeatures.map((feature) => (
          <div
            key={feature.id}
            className="bg-white dark:bg-gray-900 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-all duration-300 cursor-pointer group"
            onClick={() => setSelectedFeature(feature)}
          >
            {/* Icon and Status */}
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl">
                {feature.icon}
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusColor(feature.status)}`}>
                {getStatusIcon(feature.status)}
                {feature.status}
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
                  <div className="p-3 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl">
                    {selectedFeature.icon}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {selectedFeature.title}
                    </h2>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedFeature.status)}`}>
                      {selectedFeature.status}
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
    </div>
  );
} 