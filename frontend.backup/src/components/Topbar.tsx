import { Bell, Sun, Moon, Search, Bot, Menu } from "lucide-react";
import { useUser } from "../contexts/UserContext";

interface TopbarProps {
  onMenuClick: () => void;
  onToggleDarkMode: () => void;
  darkMode: boolean;
  onToggleAI: () => void;
  aiSidebarOpen: boolean;
}

/**
 * Topbar component with a modern, welcoming look.
 * - Gradient/soft background, large heading, subtitle, search bar, notification/profile icons, dark mode toggle.
 * - AI assistant toggle button for opening the AI sidebar.
 */
export default function Topbar({ onMenuClick, onToggleDarkMode, darkMode, onToggleAI, aiSidebarOpen }: TopbarProps) {
  const { user } = useUser();
  
  return (
    <header className="bg-gradient-to-r from-blue-800 to-indigo-900 px-10 py-6 flex flex-col md:flex-row md:items-center md:justify-between shadow">
      <div className="flex items-center gap-4">
        {/* Mobile menu button */}
        <button
          className="md:hidden p-2 rounded-full bg-white/20 hover:bg-white/30 transition"
          onClick={onMenuClick}
          aria-label="Open menu"
        >
          <Menu className="w-6 h-6 text-blue-200" />
        </button>
        
        <div>
          <div className="text-2xl font-extrabold text-white mb-1">
            Welcome back, {user?.name?.split(' ')[0] || 'User'}!
          </div>
          <div className="text-blue-200 text-sm">Your AI assistant is ready to help</div>
        </div>
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
        
        {/* AI Assistant toggle */}
        <button
          className={`p-2 rounded-full transition-all duration-200 ${
            aiSidebarOpen 
              ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg' 
              : 'bg-white/20 hover:bg-white/30 text-blue-200'
          }`}
          onClick={onToggleAI}
          aria-label="Toggle AI assistant"
        >
          <Bot className="w-6 h-6" />
        </button>
        
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
          {user?.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
} 