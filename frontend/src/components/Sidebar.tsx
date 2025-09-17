import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, Users, Contact, Kanban, Bot, Settings, LogOut, MessageCircle, Mail, Brain, UserCog, BookOpen, Building2 } from "lucide-react";
import neuraLogo from "../assets/NeuraCRM.png";
import { motion } from "framer-motion";

const navItems = [
  { name: "Dashboard", icon: <LayoutDashboard />, path: "/dashboard" },
  { name: "Leads", icon: <Users />, path: "/leads" },
  { name: "Contacts", icon: <Contact />, path: "/contacts" },
  { name: "Pipeline", icon: <Kanban />, path: "/kanban" },
  { name: "Chat", icon: <MessageCircle />, path: "/chat" },
  { name: "AI Features", icon: <Bot />, path: "/ai" },
  { name: "AI Help Guide", icon: <BookOpen />, path: "/ai-help" },
  { name: "Predictive Analytics", icon: <Brain />, path: "/predictive-analytics" },
  { name: "Email Automation", icon: <Mail />, path: "/email-automation" },
  { name: "Customer Accounts", icon: <Building2 />, path: "/customer-accounts" },
  { name: "User Management", icon: <UserCog />, path: "/user-management" },
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

  return (
    <aside className="bg-[#181E36] text-white w-64 min-h-screen flex flex-col justify-between shadow-2xl relative">
      <div>
        {/* Logo and subtitle (compact) */}
        <div className="flex flex-col items-center py-6">
          <div className="flex flex-col items-center mb-2">
            <img src={neuraLogo} alt="NeuraCRM logo" className="w-14 h-14 rounded-full border-2 border-pink-300 shadow" />
            <div className="text-xs text-blue-200 mt-2 text-center font-medium">Smarter Sales, Powered by AI</div>
          </div>
        </div>
        {/* Navigation (centered pill for active) */}
        <nav className="flex-1 relative">
          <ul className="relative">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.name} className="relative z-10">
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-3 pl-6 pr-6 py-2 my-1 font-medium text-base transition-all duration-300 w-[90%] mx-auto relative ${
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
        </nav>
      </div>
      {/* Bottom section (compact) */}
      <div className="mb-6">
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