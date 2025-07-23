import { Bell, Sun, Moon, Search } from "lucide-react";
import React from "react";

/**
 * Topbar component with a modern, welcoming look.
 * - Gradient/soft background, large heading, subtitle, search bar, notification/profile icons, dark mode toggle.
 */
export default function Topbar({ onMenuClick, onToggleDarkMode, darkMode }) {
  return (
    <header className="bg-gradient-to-r from-blue-800 to-indigo-900 px-10 py-6 flex flex-col md:flex-row md:items-center md:justify-between shadow">
      <div>
        <div className="text-2xl font-extrabold text-white mb-1">Welcome back, Alex!</div>
        <div className="text-blue-200 text-sm">Your AI assistant is ready to help</div>
      </div>
      <div className="flex items-center gap-4 mt-4 md:mt-0">
        {/* Search bar */}
        <div className="relative">
          <input
            type="text"
            placeholder="Ask AI anything..."
            className="rounded-full px-4 py-2 bg-white/20 text-white placeholder:text-blue-200 focus:outline-none focus:ring-2 focus:ring-pink-400 w-64"
          />
          <Search className="absolute right-3 top-2.5 w-5 h-5 text-blue-200" />
        </div>
        {/* Dark mode toggle */}
        <button
          className="p-2 rounded-full bg-white/20 hover:bg-white/30 transition"
          onClick={onToggleDarkMode}
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="w-6 h-6 text-yellow-300" /> : <Moon className="w-6 h-6 text-blue-200" />}
        </button>
        {/* Notifications */}
        <button className="relative p-2 rounded-full bg-white/20 hover:bg-white/30 transition">
          <Bell className="w-6 h-6 text-blue-200" />
          <span className="absolute top-1 right-1 flex items-center justify-center w-4 h-4 bg-pink-500 text-xs text-white rounded-full">
            2
          </span>
        </button>
        {/* Profile */}
        <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
          AK
        </div>
      </div>
    </header>
  );
} 