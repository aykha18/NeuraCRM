/**
 * Dashboard page: Header, AI Insights card, Metrics cards, Analytics charts, and Activity Feed
 * - Uses Recharts for real charts with data from backend
 * - Custom dot style for line chart
 * - Pie chart slices pop out on hover
 * - Integrated with React Query for data fetching
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Users, CheckCircle, DollarSign, Brain, Zap, MessageCircle, Plus, UserPlus, Clock } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from "recharts";
import { fetchDashboardData } from "../services/dashboard";
import type { DashboardData } from "../services/dashboard";
import { useAuth } from "../contexts/AuthContext";
import Button from "../components/Button";

// Icon mapping for activity feed
const iconMap: Record<string, React.ReactNode> = {
  CheckCircle: <CheckCircle className="w-4 h-4 text-yellow-500" />,
  Plus: <Plus className="w-4 h-4 text-green-500" />,
  UserPlus: <UserPlus className="w-4 h-4 text-blue-500" />,
  Clock: <Clock className="w-4 h-4 text-orange-500" />,
  MessageCircle: <MessageCircle className="w-4 h-4 text-blue-500" />,
  Zap: <Zap className="w-4 h-4 text-pink-500" />
};

// Custom dot for each line
const CustomDot = (color: string) => (props: any) => {
  const { cx, cy, index } = props;
  return (
    <circle
      key={`dot-${index}`}
      cx={cx}
      cy={cy}
      r={7}
      stroke="#fff"
      strokeWidth={3}
      fill={color}
      style={{ filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.10))" }}
    />
  );
};

// Custom active shape for pop-out pie slice using Sector
// const renderActiveShape = (props: any) => {
//   const {
//     cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill
//   } = props;
//   return (
//     <g>
//       <Sector
//         cx={cx}
//         cy={cy}
//         innerRadius={innerRadius}
//         outerRadius={outerRadius + 12} // pop out by 12px
//         startAngle={startAngle}
//         endAngle={endAngle}
//         fill={fill}
//         stroke="#fff"
//         strokeWidth={2}
//       />
//     </g>
//   );
// };

// Small custom tooltip for pie chart
const CustomPieTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const entry = payload[0];
    return (
      <div
        className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-md px-2 py-1 text-xs flex items-center gap-2 shadow"
        style={{ minWidth: 0, minHeight: 0 }}
      >
        <span
          className="inline-block w-2 h-2 rounded-full"
          style={{ background: entry.color || entry.payload.color }}
        />
        <span className="font-semibold">{entry.name}:</span>
        <span>{entry.value}%</span>
      </div>
    );
  }
  return null;
};

// CompactTooltip for LineChart
const CompactTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || !payload.length) return null;
  return (
    <div style={{
      background: "#fff",
      border: "1px solid #eee",
      borderRadius: 4,
      padding: "2px 8px",
      fontSize: 12,
      color: "#222",
      boxShadow: "0 1px 4px rgba(0,0,0,0.04)"
    }}>
      {label && <div style={{ fontWeight: 600 }}>{label}</div>}
      {payload.map((entry: any, idx: number) => (
        <div key={idx}>
          <span style={{ color: entry.color, fontWeight: 600 }}>{entry.name}:</span> {entry.value}
        </div>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const { user } = useAuth();
  
  // Fetch dashboard data using React Query
  const { data: dashboardData, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: fetchDashboardData,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Error loading dashboard</div>
          <div className="text-gray-600">Please check your connection and try again</div>
        </div>
      </div>
    );
  }

  // Use fallback data if no data is available
  const data = dashboardData || {
    metrics: {
      active_leads: 0,
      closed_deals: 0,
      total_revenue: 0,
      ai_score: 0,
      lead_quality_score: 0,
      conversion_rate: 0,
      target_achievement: 0
    },
    performance: [],
    lead_quality: [],
    activity_feed: []
  };

  // Format revenue for display
  const formatRevenue = (revenue: number) => {
    if (revenue >= 1000000) {
      return `$${(revenue / 1000000).toFixed(1)}M`;
    } else if (revenue >= 1000) {
      return `$${(revenue / 1000).toFixed(0)}K`;
    }
    return `$${revenue.toFixed(0)}`;
  };

  return (
    <div>
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-1">AI-Powered Dashboard</h1>
          <div className="text-lg text-gray-500 dark:text-gray-300">Intelligent insights for smarter decisions</div>
        </div>
        <div className="flex gap-3 mt-4 md:mt-0">
          {/* AI Insights button */}
          <Button variant="pink" size="md" icon={Brain}>
            AI Insights
          </Button>
          {/* Quick Action button */}
          <Button variant="blue" size="md" icon={Zap}>
            Quick Action
          </Button>
        </div>
      </div>

      {/* AI Insights Card */}
      <div className="bg-white dark:bg-gray-900 border border-purple-300 dark:border-purple-700 rounded-2xl shadow-lg p-6 mb-8 relative">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-2xl">✨</span>
          <span className="font-bold text-xl text-gray-900 dark:text-white">AI Insights</span>
          <span className="ml-auto text-xs text-green-500 font-semibold">● Live Analysis</span>
        </div>
        {/* Insights grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Insight 1 */}
          <div className="rounded-xl bg-pink-50 dark:bg-pink-900/40 border-l-4 border-pink-400 p-4 flex flex-col">
            <div className="font-semibold text-pink-700 dark:text-pink-300 mb-1">High-Value Lead Detected</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-2">Enterprise client showing 89% conversion probability</div>
            <a href="#" className="text-pink-600 dark:text-pink-300 text-sm font-medium hover:underline">Schedule demo →</a>
          </div>
          {/* Insight 2 */}
          <div className="rounded-xl bg-yellow-50 dark:bg-yellow-900/40 border-l-4 border-yellow-400 p-4 flex flex-col">
            <div className="font-semibold text-yellow-700 dark:text-yellow-200 mb-1">Deal at Risk</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-2">TechCorp deal inactive for 7 days</div>
            <a href="#" className="text-yellow-700 dark:text-yellow-200 text-sm font-medium hover:underline">Send follow-up →</a>
          </div>
          {/* Insight 3 */}
          <div className="rounded-xl bg-green-50 dark:bg-green-900/40 border-l-4 border-green-400 p-4 flex flex-col">
            <div className="font-semibold text-green-700 dark:text-green-200 mb-1">Optimal Contact Time</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-2">Best time to call prospects: 2-4 PM today</div>
            <a href="#" className="text-green-700 dark:text-green-200 text-sm font-medium hover:underline">Start calling →</a>
          </div>
        </div>
      </div>

      {/* Metrics Cards Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Active Leads */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-full mb-3">
            <Users className="w-7 h-7 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-blue-600 dark:text-blue-400 mb-1">{data.metrics.active_leads}</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Active Leads</div>
          <div className="text-xs text-purple-500">Quality score: {data.metrics.lead_quality_score}/10</div>
        </div>
        {/* Deals Closed */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full mb-3">
            <CheckCircle className="w-7 h-7 text-green-600 dark:text-green-400" />
          </div>
          <div className="text-3xl font-extrabold text-green-600 dark:text-green-400 mb-1">{data.metrics.closed_deals}</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Deals Closed</div>
          <div className="text-xs text-pink-500">Conversion rate: {data.metrics.conversion_rate}%</div>
        </div>
        {/* Revenue */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-full mb-3">
            <DollarSign className="w-7 h-7 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="text-3xl font-extrabold text-purple-600 dark:text-purple-400 mb-1">{formatRevenue(data.metrics.total_revenue)}</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Revenue</div>
          <div className="text-xs text-blue-500">Above target by {data.metrics.target_achievement}%</div>
        </div>
        {/* AI Score */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-orange-100 dark:bg-orange-900 p-3 rounded-full mb-3">
            <Brain className="w-7 h-7 text-orange-600 dark:text-orange-400" />
          </div>
          <div className="text-3xl font-extrabold text-orange-600 dark:text-orange-400 mb-1">{data.metrics.ai_score}</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">AI Score</div>
          <div className="text-xs text-green-500">Performance excellent</div>
        </div>
      </div>

      {/* Analytics and Activity Feed Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Performance Analytics (Line Chart) */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col">
          <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Performance Analytics</div>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.performance} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="month" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip content={<CompactTooltip />} />
                <Legend />
                <Line type="monotone" dataKey="leads" stroke="#3b82f6" strokeWidth={3} dot={CustomDot("#3b82f6")} name="Leads" />
                <Line type="monotone" dataKey="deals" stroke="#a21caf" strokeWidth={3} dot={CustomDot("#a21caf")} name="Deals" />
                <Line type="monotone" dataKey="revenue" stroke="#22c55e" strokeWidth={3} dot={CustomDot("#22c55e")} name="Revenue" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* Lead Quality (Pie Chart) */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Lead Quality</div>
          <div className="w-full h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.lead_quality}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  fill="#8884d8"
                  label
                >
                  {data.lead_quality.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-4 w-full text-sm">
            {data.lead_quality.map((item) => (
              <li key={item.name} className="flex items-center justify-between mb-1">
                <span className="flex items-center gap-2">
                  <span className="inline-block w-3 h-3 rounded-full" style={{ background: item.color }}></span>
                  {item.name}
                </span>
                <span className="font-semibold">{item.value}%</span>
              </li>
            ))}
          </ul>
        </div>
        {/* Smart Activity Feed */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col">
          <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-pink-500" /> Smart Activity Feed
          </div>
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {data.activity_feed.length > 0 ? (
              data.activity_feed.map((item, idx) => (
                <li key={idx} className="flex items-center gap-3 py-3">
                  <span className={`flex items-center justify-center rounded-full ${item.color} w-8 h-8`}>
                    {iconMap[item.icon] || <MessageCircle className="w-4 h-4 text-blue-500" />}
                  </span>
                  <div className="flex-1">
                    <div className="text-gray-900 dark:text-white text-sm font-medium">{item.title}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{item.time}</div>
                  </div>
                </li>
              ))
            ) : (
              <li className="py-3 text-gray-500 dark:text-gray-400 text-sm">No recent activity</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
} 