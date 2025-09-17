import React, { useState, useEffect } from 'react';
import { 
  Sparkles as SparklesIcon,
  MessagesSquare as ChatBubbleLeftRightIcon,
  Lightbulb as LightBulbIcon,
  Rocket as RocketLaunchIcon,
  Search as MagnifyingGlassIcon,
  FileText as DocumentTextIcon,
  Play as PlayIcon,
  CheckCircle as CheckCircleIcon,
  ArrowRight as ArrowRightIcon,
  Clipboard as ClipboardDocumentIcon,
  Eye as EyeIcon,
  Code as CodeBracketIcon
} from 'lucide-react';

interface PromptCategory {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  color: string;
  prompts: PromptExample[];
}

interface PromptExample {
  id: string;
  title: string;
  description: string;
  prompt: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
}

const AIHelpGuide: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<string>('overview');
  const [selectedPrompt, setSelectedPrompt] = useState<PromptExample | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCopySuccess, setShowCopySuccess] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const categories: PromptCategory[] = [
    {
      id: 'overview',
      title: 'Getting Started',
      description: 'Master the basics of AI prompting',
      icon: RocketLaunchIcon,
      color: 'from-blue-500 to-purple-600',
      prompts: [
        {
          id: 'basic-pipeline',
          title: 'Pipeline Overview',
          description: 'Get a quick overview of your sales pipeline',
          prompt: 'Analyze my pipeline and tell me which 3 deals need immediate attention and why',
          category: 'overview',
          difficulty: 'beginner',
          tags: ['pipeline', 'analysis', 'priority']
        },
        {
          id: 'basic-email',
          title: 'Simple Email Generation',
          description: 'Generate a personalized email quickly',
          prompt: 'Create a personalized email for [Contact Name] about [Topic] that references our last conversation',
          category: 'overview',
          difficulty: 'beginner',
          tags: ['email', 'personalization', 'communication']
        }
      ]
    },
    {
      id: 'leads',
      title: 'Lead Management',
      description: 'Qualify, nurture, and convert leads',
      icon: LightBulbIcon,
      color: 'from-green-500 to-teal-600',
      prompts: [
        {
          id: 'lead-qualification',
          title: 'Lead Qualification Analysis',
          description: 'Comprehensive lead assessment and scoring',
          prompt: 'Analyze lead [Lead Name] and provide a comprehensive qualification assessment including: current lead score and factors, qualification status (Hot/Warm/Cold) with reasoning, buying signals and purchase intent indicators, risk factors and potential obstacles, specific next steps to advance the lead, expected sales cycle timeline, required resources to close',
          category: 'leads',
          difficulty: 'intermediate',
          tags: ['qualification', 'scoring', 'analysis', 'strategy']
        },
        {
          id: 'lead-nurturing',
          title: 'Lead Nurturing Strategy',
          description: 'Develop a nurturing sequence for leads',
          prompt: 'Develop a lead nurturing strategy for [Lead Name] including: content strategy and communication cadence, channel mix (email, social, phone, events), personalization approach for each touchpoint, value delivery at each stage, progression triggers and handoff criteria, success metrics to track effectiveness',
          category: 'leads',
          difficulty: 'intermediate',
          tags: ['nurturing', 'strategy', 'content', 'engagement']
        },
        {
          id: 'lead-conversion',
          title: 'Lead to Deal Conversion',
          description: 'Convert qualified leads to active deals',
          prompt: 'Help me convert lead [Lead Name] to a deal by: identifying the best conversion approach, creating a compelling value proposition, addressing potential objections, setting up the deal structure, planning the next steps',
          category: 'leads',
          difficulty: 'intermediate',
          tags: ['conversion', 'strategy', 'objection-handling', 'value-proposition']
        }
      ]
    },
    {
      id: 'deals',
      title: 'Deal Strategy',
      description: 'Win more deals with strategic planning',
      icon: SparklesIcon,
      color: 'from-purple-500 to-pink-600',
      prompts: [
        {
          id: 'deal-strategy',
          title: 'Deal Strategy Development',
          description: 'Create comprehensive deal strategies',
          prompt: 'Create a comprehensive strategy for deal [Deal Name]: current status and position in sales process, key stakeholders and decision makers, competitive advantages and differentiators, value proposition for this specific prospect, anticipated objections and response strategies, closing strategy and tactics, critical milestones and timeline, risk mitigation plans',
          category: 'deals',
          difficulty: 'advanced',
          tags: ['strategy', 'stakeholders', 'competitive', 'closing']
        },
        {
          id: 'deal-progression',
          title: 'Deal Advancement',
          description: 'Move deals to the next stage',
          prompt: 'Help me advance deal [Deal Name] to the next stage by: identifying what\'s needed to move forward, creating a compelling business case, planning stakeholder engagement, addressing any blockers or concerns, setting up next steps and timeline',
          category: 'deals',
          difficulty: 'intermediate',
          tags: ['progression', 'business-case', 'stakeholders', 'timeline']
        },
        {
          id: 'deal-risk',
          title: 'Deal Risk Assessment',
          description: 'Identify and mitigate deal risks',
          prompt: 'Assess the risk level for deal [Deal Name] and provide: risk factors and their impact, probability of closing, mitigation strategies, early warning indicators, contingency plans',
          category: 'deals',
          difficulty: 'intermediate',
          tags: ['risk-assessment', 'mitigation', 'probability', 'contingency']
        }
      ]
    },
    {
      id: 'communication',
      title: 'Email & Communication',
      description: 'Master personalized communication',
      icon: ChatBubbleLeftRightIcon,
      color: 'from-orange-500 to-red-600',
      prompts: [
        {
          id: 'email-personalization',
          title: 'Advanced Email Personalization',
          description: 'Create highly personalized emails',
          prompt: 'Generate a personalized email for [Contact Name] about [Topic/Purpose]: use a professional but warm tone, reference specific interactions or data points, include relevant value propositions, create appropriate urgency, provide clear call-to-action, strengthen the relationship',
          category: 'communication',
          difficulty: 'intermediate',
          tags: ['email', 'personalization', 'tone', 'value-proposition']
        },
        {
          id: 'follow-up-strategy',
          title: 'Follow-up Strategy',
          description: 'Create effective follow-up sequences',
          prompt: 'Create a follow-up strategy for [Contact/Deal Name]: optimal timing for follow-up, best communication channel, key message points, value to provide in follow-up, clear next steps for the prospect, escalation plan if needed',
          category: 'communication',
          difficulty: 'intermediate',
          tags: ['follow-up', 'timing', 'channels', 'escalation']
        },
        {
          id: 'objection-handling',
          title: 'Objection Handling',
          description: 'Handle sales objections effectively',
          prompt: 'Help me handle this objection: "[Objection Text]" for deal [Deal Name]: analyze the root cause of the objection, provide response strategy and talking points, include proof points and examples, suggest alternative approaches, plan follow-up actions, prevent similar objections in future',
          category: 'communication',
          difficulty: 'advanced',
          tags: ['objections', 'response-strategy', 'proof-points', 'prevention']
        }
      ]
    },
    {
      id: 'analytics',
      title: 'Pipeline & Analytics',
      description: 'Data-driven sales insights',
      icon: MagnifyingGlassIcon,
      color: 'from-indigo-500 to-blue-600',
      prompts: [
        {
          id: 'pipeline-analysis',
          title: 'Pipeline Health Check',
          description: 'Comprehensive pipeline analysis',
          prompt: 'Analyze my sales pipeline and provide insights on: overall pipeline health and strength, stage-by-stage bottlenecks and opportunities, revenue forecasting and projections, conversion rates between stages, deal velocity and time in each stage, resource allocation recommendations, risk assessment and mitigation strategies',
          category: 'analytics',
          difficulty: 'advanced',
          tags: ['pipeline', 'health', 'forecasting', 'conversion-rates']
        },
        {
          id: 'sales-forecasting',
          title: 'Sales Forecasting',
          description: 'Predict revenue and outcomes',
          prompt: 'Provide a sales forecast based on my current pipeline: revenue projections by time period, deal probability assessments, timeline predictions for closures, risk factors that could impact forecast, confidence levels for predictions, scenario planning (best/worst/most likely), gap analysis against targets',
          category: 'analytics',
          difficulty: 'advanced',
          tags: ['forecasting', 'revenue', 'probability', 'scenarios']
        },
        {
          id: 'performance-analysis',
          title: 'Performance Analysis',
          description: 'Analyze and improve performance',
          prompt: 'Analyze my sales performance and provide: key performance indicators and trends, strengths and areas for improvement, comparison with team/organization metrics, goal achievement status, recommendations for improvement, action items to boost performance',
          category: 'analytics',
          difficulty: 'intermediate',
          tags: ['performance', 'kpis', 'improvement', 'benchmarking']
        }
      ]
    },
    {
      id: 'competitive',
      title: 'Competitive Intelligence',
      description: 'Outmaneuver the competition',
      icon: EyeIcon,
      color: 'from-red-500 to-orange-600',
      prompts: [
        {
          id: 'competitive-analysis',
          title: 'Competitive Analysis',
          description: 'Analyze competitive landscape',
          prompt: 'Analyze the competitive landscape for deal [Deal Name]: identify key competitors in this deal, our advantages and differentiators, competitor weaknesses to exploit, battle cards and talking points, proof points of our superiority, risk mitigation against competitor advantages, win strategy against competition',
          category: 'competitive',
          difficulty: 'advanced',
          tags: ['competitive', 'analysis', 'differentiators', 'battle-cards']
        },
        {
          id: 'market-positioning',
          title: 'Market Positioning',
          description: 'Position against specific competitors',
          prompt: 'Help me position our solution against [Competitor Name] by: highlighting our key differentiators, creating compelling value propositions, developing proof points and case studies, addressing competitor claims, pricing strategy and positioning, win themes and messaging',
          category: 'competitive',
          difficulty: 'intermediate',
          tags: ['positioning', 'differentiators', 'value-proposition', 'messaging']
        }
      ]
    }
  ];

  const allPrompts = categories.flatMap(cat => cat.prompts);

  const filteredPrompts = allPrompts.filter(prompt => 
    prompt.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    prompt.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const copyToClipboard = async (text: string, promptId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setShowCopySuccess(promptId);
      setTimeout(() => setShowCopySuccess(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '🟢';
      case 'intermediate': return '🟡';
      case 'advanced': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative px-6 py-16 sm:px-8 lg:px-12">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-white/20 backdrop-blur-sm rounded-2xl">
                <SparklesIcon className="h-12 w-12 text-white" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
              AI Sales Assistant
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
              Master the art of AI prompting to unlock the full power of your CRM
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-white/80">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5" />
                <span>430+ Expert Prompts</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5" />
                <span>8 Categories</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5" />
                <span>Interactive Examples</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Search and Controls */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search prompts, categories, or tags..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white shadow-sm"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-indigo-100 text-indigo-600' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Category Navigation */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={`flex items-center gap-3 px-6 py-3 rounded-xl transition-all duration-200 ${
                    activeCategory === category.id
                      ? `bg-gradient-to-r ${category.color} text-white shadow-lg transform scale-105`
                      : 'bg-white text-gray-700 hover:bg-gray-50 shadow-sm hover:shadow-md'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{category.title}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Prompts List */}
          <div className="lg:col-span-2">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {searchTerm ? `Search Results (${filteredPrompts.length})` : categories.find(c => c.id === activeCategory)?.title}
              </h2>
              <p className="text-gray-600">
                {searchTerm 
                  ? `Found ${filteredPrompts.length} prompts matching "${searchTerm}"`
                  : categories.find(c => c.id === activeCategory)?.description
                }
              </p>
            </div>

            <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
              {(searchTerm ? filteredPrompts : categories.find(c => c.id === activeCategory)?.prompts || []).map((prompt) => (
                <div
                  key={prompt.id}
                  className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 hover:border-indigo-200 cursor-pointer group"
                  onClick={() => setSelectedPrompt(prompt)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
                          {prompt.title}
                        </h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(prompt.difficulty)}`}>
                          {getDifficultyIcon(prompt.difficulty)} {prompt.difficulty}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-3">{prompt.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {prompt.tags.slice(0, 3).map((tag) => (
                          <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                            {tag}
                          </span>
                        ))}
                        {prompt.tags.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                            +{prompt.tags.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                    <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-indigo-500 transition-colors" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Prompt Detail Panel */}
          <div className="lg:col-span-1">
            {selectedPrompt ? (
              <div className="sticky top-8 bg-white rounded-xl p-6 shadow-lg border border-gray-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">{selectedPrompt.title}</h3>
                  <button
                    onClick={() => copyToClipboard(selectedPrompt.prompt, selectedPrompt.id)}
                    className="flex items-center gap-2 px-3 py-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors"
                  >
                    {showCopySuccess === selectedPrompt.id ? (
                      <>
                        <CheckCircleIcon className="h-4 w-4" />
                        <span className="text-sm">Copied!</span>
                      </>
                    ) : (
                      <>
                        <ClipboardDocumentIcon className="h-4 w-4" />
                        <span className="text-sm">Copy</span>
                      </>
                    )}
                  </button>
                </div>
                
                <p className="text-gray-600 mb-4">{selectedPrompt.description}</p>
                
                <div className="mb-4">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(selectedPrompt.difficulty)}`}>
                    {getDifficultyIcon(selectedPrompt.difficulty)} {selectedPrompt.difficulty}
                  </span>
                </div>

                <div className="mb-6">
                  <h4 className="font-medium text-gray-900 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPrompt.tags.map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-md">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Prompt Template</h4>
                  <div className="bg-gray-50 rounded-lg p-4 border">
                    <code className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                      {selectedPrompt.prompt}
                    </code>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start gap-3">
                    <LightBulbIcon className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <h5 className="font-medium text-blue-900 mb-1">Pro Tip</h5>
                      <p className="text-blue-700 text-sm">
                        Replace placeholders like [Contact Name] and [Deal Name] with actual data from your CRM for best results.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="sticky top-8 bg-white rounded-xl p-6 shadow-lg border border-gray-200 text-center">
                <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Select a Prompt</h3>
                <p className="text-gray-600">
                  Click on any prompt from the list to see the full template and copy it to your clipboard.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Start Section */}
        <div className="mt-16 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white">
          <div className="text-center">
            <RocketLaunchIcon className="h-12 w-12 mx-auto mb-4" />
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Try these top-rated prompts to see the AI assistant in action
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
              {[
                "Analyze my pipeline and tell me which 3 deals need immediate attention and why",
                "Create a personalized email for [Contact Name] about [Topic] that references our last conversation",
                "Develop a strategy to advance [Deal Name] from [Current Stage] to [Next Stage] within [Timeline]"
              ].map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => copyToClipboard(prompt, `quick-start-${index}`)}
                  className="p-4 bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20 transition-all duration-200 text-left group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white/80">Quick Start #{index + 1}</span>
                    {showCopySuccess === `quick-start-${index}` ? (
                      <CheckCircleIcon className="h-4 w-4 text-green-400" />
                    ) : (
                      <ClipboardDocumentIcon className="h-4 w-4 text-white/60 group-hover:text-white" />
                    )}
                  </div>
                  <p className="text-sm text-white/90">{prompt}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIHelpGuide;
