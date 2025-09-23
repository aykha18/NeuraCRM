import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, Users, Contact, Kanban, Bot, Settings, LogOut, MessageCircle, Mail, Brain, UserCog, BookOpen, Building2, DollarSign, Headphones, TrendingUp, ChevronDown, ChevronRight, Phone, UserCheck, CheckCircle } from "lucide-react";
import neuraLogo from "../assets/NeuraCRM.png";
import { motion } from "framer-motion";
import { useState } from "react";

// Workflow-based navigation sections
const navigationSections = [
  {
    title: "SALES CORE",
    items: [
      { name: "Dashboard", icon: <LayoutDashboard />, path: "/dashboard" },
      { name: "Leads", icon: <Users />, path: "/leads" },
      { name: "Contacts", icon: <Contact />, path: "/contacts" },
      { name: "Pipeline", icon: <Kanban />, path: "/kanban" },
    ]
  },
  {
    title: "AI INSIGHTS",
    items: [
      { name: "AI Features", icon: <Bot />, path: "/ai" },
      { name: "AI Help Guide", icon: <BookOpen />, path: "/ai-help" },
      { name: "Predictive Analytics", icon: <Brain />, path: "/predictive-analytics" },
      { name: "Sentiment Analysis", icon: <TrendingUp />, path: "/sentiment-analysis" },
      { name: "Customer Segmentation", icon: <Users />, path: "/customer-segmentation" },
      { name: "Advanced Forecasting", icon: <TrendingUp />, path: "/advanced-forecasting" },
    ]
  },
  {
    title: "AUTOMATION",
    items: [
      { name: "Email Automation", icon: <Mail />, path: "/email-automation" },
      { name: "Lead Assignment", icon: <UserCheck />, path: "/lead-assignment-rules" },
      { name: "Approval Workflows", icon: <CheckCircle />, path: "/approval-workflows" },
      { name: "Chat", icon: <MessageCircle />, path: "/chat" },
    ]
  },
  {
    title: "BUSINESS",
    items: [
      { name: "Customer Accounts", icon: <Building2 />, path: "/customer-accounts" },
      { name: "Financial Management", icon: <DollarSign />, path: "/financial-management" },
      { name: "Customer Support", icon: <Headphones />, path: "/customer-support" },
      { name: "Call Center", icon: <Phone />, path: "/telephony" },
    ]
  },
  {
    title: "ADMIN",
    items: [
      { name: "User Management", icon: <UserCog />, path: "/user-management" },
    ]
  }
];

const bottomItems = [
  { name: "Settings", icon: <Settings />, path: "/settings" },
];

/**
 * Sidebar with centered, fully rounded pill active nav item, vibrant gradient, and a small, smoothly animated dot.
 * - The dot is small, perfectly round, and smoothly transitions between active items using Framer Motion.
 * - Only one dot appears at the end of the active button.
 */
export default function Sidebar({ open: _open, onClose }: { open: boolean; onClose: () => void }) {
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(["SALES CORE", "AI INSIGHTS", "AUTOMATION", "BUSINESS", "ADMIN"])
  );

  const toggleSection = (sectionTitle: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionTitle)) {
      newExpanded.delete(sectionTitle);
    } else {
      newExpanded.add(sectionTitle);
    }
    setExpandedSections(newExpanded);
  };

  const isSectionActive = (section: typeof navigationSections[0]) => {
    return section.items.some(item => location.pathname === item.path);
  };

  return (
    <aside className="bg-[#181E36] text-white w-64 min-h-screen flex flex-col justify-between shadow-2xl relative">
      <div className="bg-[#181E36]">
        {/* Logo and subtitle (compact) */}
        <div className="flex flex-col items-center py-6">
          <div className="flex flex-col items-center mb-2">
            <img src={neuraLogo} alt="NeuraCRM logo" className="w-14 h-14 rounded-full border-2 border-pink-300 shadow" />
            <div className="text-xs text-blue-200 mt-2 text-center font-medium">Smarter Sales, Powered by AI</div>
          </div>
        </div>
        {/* Navigation (collapsible sections) */}
        <nav className="flex-1 relative px-3 bg-[#181E36]">
          {navigationSections.map((section) => {
            const isExpanded = expandedSections.has(section.title);
            const hasActiveItem = isSectionActive(section);
            
            return (
              <div key={section.title} className="mb-2 bg-[#181E36]">
                {/* Section Header */}
                <button
                  onClick={() => toggleSection(section.title)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                    hasActiveItem 
                      ? "text-fuchsia-300" 
                      : "text-gray-500 hover:text-gray-300"
                  }`}
                >
                  <span>{section.title}</span>
                  <motion.div
                    animate={{ rotate: isExpanded ? 90 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronRight className="w-3 h-3" />
                  </motion.div>
                </button>
                
                {/* Section Items */}
                <motion.div
                  initial={false}
                  animate={{
                    height: isExpanded ? "auto" : 0,
                    opacity: isExpanded ? 1 : 0,
                  }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <ul className="space-y-1">
                    {section.items.map((item) => {
                      const isActive = location.pathname === item.path;
                      return (
                        <li key={item.name} className="relative z-10">
                          <NavLink
                            to={item.path}
                            className={({ isActive }) =>
                              `flex items-center gap-3 pl-4 pr-4 py-2 my-1 font-medium text-sm transition-all duration-300 w-full relative ${
                                isActive
                                  ? "text-white font-bold bg-gradient-to-r from-fuchsia-600 to-pink-500 rounded-full shadow"
                                  : "text-gray-400 hover:text-white"
                              }`
                            }
                            onClick={onClose}
                            style={{ borderRadius: "9999px" }}
                          >
                            {item.icon}
                            <span>{item.name}</span>
                            {/* Animated small dot for active item */}
                            {isActive && (
                              <motion.span
                                layoutId="sidebar-dot"
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full"
                                transition={{ type: "spring", stiffness: 200, damping: 30, duration: 0.8 }}
                              />
                            )}
                          </NavLink>
                        </li>
                      );
                    })}
                  </ul>
                </motion.div>
              </div>
            );
          })}
        </nav>
      </div>
      {/* Bottom section (compact) */}
      <div className="mb-6 bg-[#181E36]">
        <ul>
          {bottomItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className="flex items-center gap-3 px-6 py-2 my-1 rounded-lg transition text-gray-400 hover:text-white text-base w-[90%] mx-auto"
                onClick={onClose}
                style={{ borderRadius: "9999px" }}
              >
                {item.icon}
                <span>{item.name}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
} 