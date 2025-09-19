/**
 * Customer Segmentation Page
 * Displays AI-generated customer segments with insights and analytics
 */
import { useState, useEffect } from "react";
import { 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  Target, 
  RefreshCw,
  Eye,
  BarChart3,
  Users2,
  DollarSign,
  Activity,
  Zap,
  Brain
} from "lucide-react";
import { apiRequest } from "../utils/api";

interface CustomerSegment {
  id: number;
  name: string;
  description: string;
  segment_type: string;
  customer_count: number;
  total_deal_value: number;
  avg_deal_value: number;
  conversion_rate: number;
  insights: any;
  recommendations: string[] | any;
  risk_score: number;
  opportunity_score: number;
  is_active: boolean;
  last_updated: string;
  created_at: string;
}

interface SegmentMember {
  id: number;
  contact_id: number;
  contact_name: string;
  contact_email: string;
  contact_company: string;
  membership_score: number;
  segment_engagement_score: number;
  added_at: string;
}

export default function CustomerSegmentation() {
  const [segments, setSegments] = useState<CustomerSegment[]>([]);
  const [selectedSegment, setSelectedSegment] = useState<CustomerSegment | null>(null);
  const [segmentMembers, setSegmentMembers] = useState<SegmentMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState<number | null>(null);

  useEffect(() => {
    fetchSegments();
  }, []);

  const fetchSegments = async () => {
    try {
      setLoading(true);
      const response = await apiRequest("/api/customer-segments") as CustomerSegment[];
      setSegments(response);
    } catch (error) {
      console.error("Error fetching segments:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSegmentMembers = async (segmentId: number) => {
    try {
      const response = await apiRequest(`/api/customer-segments/${segmentId}/members`) as SegmentMember[];
      setSegmentMembers(response);
    } catch (error) {
      console.error("Error fetching segment members:", error);
    }
  };

  const refreshSegment = async (segmentId: number) => {
    try {
      setRefreshing(segmentId);
      await apiRequest(`/api/customer-segments/${segmentId}/refresh`, 'POST');
      await fetchSegments();
      if (selectedSegment?.id === segmentId) {
        await fetchSegmentMembers(segmentId);
      }
    } catch (error) {
      console.error("Error refreshing segment:", error);
    } finally {
      setRefreshing(null);
    }
  };

  const handleSegmentClick = async (segment: CustomerSegment) => {
    setSelectedSegment(segment);
    await fetchSegmentMembers(segment.id);
  };

  const getSegmentTypeColor = (type: string) => {
    switch (type) {
      case "behavioral":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
      case "demographic":
        return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
      case "transactional":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
      case "predictive":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
    }
  };

  const getRiskColor = (score: number) => {
    if (score < 30) return "text-green-600";
    if (score < 70) return "text-yellow-600";
    return "text-red-600";
  };

  const getOpportunityColor = (score: number) => {
    if (score > 70) return "text-green-600";
    if (score > 40) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl">
            <Users className="w-8 h-8 text-purple-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Customer Segmentation
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Automatically segment customers based on behavior, value, and engagement patterns
            </p>
          </div>
        </div>

        {/* AI Insights Banner */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-purple-600" />
            <div>
              <h3 className="font-semibold text-purple-800 dark:text-purple-300">
                AI-Powered Segmentation
              </h3>
              <p className="text-purple-700 dark:text-purple-400 text-sm">
                Our AI continuously analyzes customer data to create meaningful segments with actionable insights and recommendations.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Segments List */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Customer Segments
              </h2>
              <div className="text-sm text-gray-500">
                {segments.length} segments
              </div>
            </div>

            <div className="space-y-4">
              {segments.map((segment) => (
                <div
                  key={segment.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                    selectedSegment?.id === segment.id
                      ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600"
                  }`}
                  onClick={() => handleSegmentClick(segment)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg">
                        <Users2 className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {segment.name}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {segment.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSegmentTypeColor(segment.segment_type)}`}>
                        {segment.segment_type}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          refreshSegment(segment.id);
                        }}
                        disabled={refreshing === segment.id}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded transition-colors"
                      >
                        <RefreshCw className={`w-4 h-4 ${refreshing === segment.id ? 'animate-spin' : ''}`} />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {segment.customer_count}
                      </div>
                      <div className="text-gray-500">Customers</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        ${segment.avg_deal_value.toLocaleString()}
                      </div>
                      <div className="text-gray-500">Avg Deal</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        {segment.conversion_rate.toFixed(1)}%
                      </div>
                      <div className="text-gray-500">Conversion</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-gray-900 dark:text-white">
                        ${segment.total_deal_value.toLocaleString()}
                      </div>
                      <div className="text-gray-500">Total Value</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Segment Details */}
        <div className="lg:col-span-1">
          {selectedSegment ? (
            <div className="space-y-6">
              {/* Segment Overview */}
              <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Segment Overview
                </h3>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Risk Score</span>
                    <span className={`font-semibold ${getRiskColor(selectedSegment.risk_score)}`}>
                      {selectedSegment.risk_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Opportunity Score</span>
                    <span className={`font-semibold ${getOpportunityColor(selectedSegment.opportunity_score)}`}>
                      {selectedSegment.opportunity_score.toFixed(0)}/100
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-300">Last Updated</span>
                    <span className="text-sm text-gray-500">
                      {new Date(selectedSegment.last_updated).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* AI Insights */}
              {selectedSegment.insights && (
                <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-600" />
                    AI Insights
                  </h3>
                  
                  <div className="space-y-3">
                    {selectedSegment.insights.key_characteristics && (
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="font-medium text-blue-800 dark:text-blue-300">
                          Key Characteristics:
                        </div>
                        <div className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                          {selectedSegment.insights.key_characteristics}
                        </div>
                      </div>
                    )}
                    {selectedSegment.insights.performance_summary && (
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="font-medium text-green-800 dark:text-green-300">
                          Performance Summary:
                        </div>
                        <div className="text-sm text-green-700 dark:text-green-300 mt-1">
                          {selectedSegment.insights.performance_summary}
                        </div>
                      </div>
                    )}
                    {selectedSegment.insights.trends && Array.isArray(selectedSegment.insights.trends) && (
                      <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                        <div className="font-medium text-purple-800 dark:text-purple-300">
                          Trends:
                        </div>
                        <ul className="text-sm text-purple-700 dark:text-purple-300 mt-1 space-y-1">
                          {selectedSegment.insights.trends.map((trend: string, index: number) => (
                            <li key={index}>• {trend}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selectedSegment.recommendations && selectedSegment.recommendations.length > 0 && (
                <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-yellow-600" />
                    Recommendations
                  </h3>
                  
                  <ul className="space-y-2">
                    {selectedSegment.recommendations.map((recommendation: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                        <span className="text-sm text-gray-600 dark:text-gray-300">
                          {recommendation}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Segment Members */}
              <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <Eye className="w-5 h-5 text-blue-600" />
                  Segment Members ({segmentMembers.length})
                </h3>
                
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {segmentMembers.map((member) => (
                    <div key={member.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {member.contact_name}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-300">
                            {member.contact_company}
                          </div>
                          <div className="text-xs text-gray-500">
                            {member.contact_email}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {(member.membership_score * 100).toFixed(0)}%
                          </div>
                          <div className="text-xs text-gray-500">Match</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-900 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a segment to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
