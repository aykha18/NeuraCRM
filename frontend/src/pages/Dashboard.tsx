/**
 * Dashboard page: Header, AI Insights card, Metrics cards, Analytics charts, and Activity Feed
 * - Uses Recharts for real charts with sample data
 * - Custom dot style for line chart
 * - Pie chart slices pop out on hover
 */
import React, { useState } from "react";
import { Users, CheckCircle, DollarSign, Brain, Zap, MessageCircle } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, Sector
} from "recharts";

const performanceData = [
  { month: "Jan", leads: 195, deals: 65, revenue: 30 },
  { month: "Feb", leads: 210, deals: 70, revenue: 35 },
  { month: "Mar", leads: 225, deals: 75, revenue: 40 },
  { month: "Apr", leads: 240, deals: 80, revenue: 45 },
  { month: "May", leads: 250, deals: 85, revenue: 50 },
  { month: "Jun", leads: 260, deals: 90, revenue: 55 },
];

const leadQualityData = [
  { name: "Qualified", value: 45, color: "#22c55e" },
  { name: "Nurturing", value: 30, color: "#fbbf24" },
  { name: "Cold", value: 15, color: "#64748b" },
  { name: "Hot", value: 10, color: "#a21caf" },
];

const activityFeed = [
  {
    icon: <Zap className="w-4 h-4 text-pink-500" />, color: "bg-pink-100", title: "AI identified high-value prospect: TechCorp Inc.", time: "2 min ago"
  },
  {
    icon: <CheckCircle className="w-4 h-4 text-yellow-500" />, color: "bg-yellow-100", title: 'Deal "Enterprise Package" moved to final stage', time: "15 min ago"
  },
  {
    icon: <MessageCircle className="w-4 h-4 text-blue-500" />, color: "bg-blue-100", title: "Message from John Doe", time: "1 hour ago"
  },
];

// Custom dot for each line
const CustomDot = (color: string) => (props: any) => {
  const { cx, cy } = props;
  return (
    <circle
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
const renderActiveShape = (props: any) => {
  const {
    cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill
  } = props;
  return (
    <g>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius + 12} // pop out by 12px
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
        stroke="#fff"
        strokeWidth={2}
      />
    </g>
  );
};

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
  // State for hovered pie slice
  const [activePieIndex, setActivePieIndex] = useState<number | null>(null);

  return (
    <div>
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-1">AI-Powered Dashboard</h1>
          <div className="text-lg text-gray-500 dark:text-gray-300">Intelligent insights for smarter decisions</div>
        </div>
        <div className="flex gap-3 mt-4 md:mt-0">
          {/* AI Insights button (gradient) */}
          <button className="px-5 py-2 rounded-full bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white font-semibold shadow hover:from-fuchsia-700 hover:to-pink-600 transition">AI Insights</button>
          {/* Quick Action button (solid) */}
          <button className="px-5 py-2 rounded-full bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition">Quick Action</button>
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
          <div className="text-3xl font-extrabold text-blue-600 dark:text-blue-400 mb-1">247</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Active Leads</div>
          <div className="text-xs text-purple-500">Quality score: 8.4/10</div>
        </div>
        {/* Deals Closed */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full mb-3">
            <CheckCircle className="w-7 h-7 text-green-600 dark:text-green-400" />
          </div>
          <div className="text-3xl font-extrabold text-green-600 dark:text-green-400 mb-1">34</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Deals Closed</div>
          <div className="text-xs text-pink-500">Conversion rate: 13.8%</div>
        </div>
        {/* Revenue */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-full mb-3">
            <DollarSign className="w-7 h-7 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="text-3xl font-extrabold text-purple-600 dark:text-purple-400 mb-1">$847K</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Revenue</div>
          <div className="text-xs text-blue-500">Above target by 12%</div>
        </div>
        {/* AI Score */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-orange-100 dark:bg-orange-900 p-3 rounded-full mb-3">
            <Brain className="w-7 h-7 text-orange-600 dark:text-orange-400" />
          </div>
          <div className="text-3xl font-extrabold text-orange-600 dark:text-orange-400 mb-1">94</div>
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
              <LineChart data={performanceData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
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
                  data={leadQualityData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  fill="#8884d8"
                  label
                  {...({
                    activeIndex: activePieIndex ?? 0,
                    activeShape: renderActiveShape,
                    onMouseEnter: (_: any, index: number) => setActivePieIndex(index),
                    onMouseLeave: () => setActivePieIndex(null),
                  } as any)}
                >
                  {leadQualityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <ul className="mt-4 w-full text-sm">
            {leadQualityData.map((item) => (
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
            {activityFeed.map((item, idx) => (
              <li key={idx} className="flex items-center gap-3 py-3">
                <span className={`flex items-center justify-center rounded-full ${item.color} w-8 h-8`}>{item.icon}</span>
                <div className="flex-1">
                  <div className="text-gray-900 dark:text-white text-sm font-medium">{item.title}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{item.time}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
} 