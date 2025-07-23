import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import React, { useState, useEffect } from "react";

/**
 * Layout component that provides the main application structure:
 * - Sidebar on the left (responsive/collapsible)
 * - Topbar at the top of the main content area (shows hamburger menu on mobile)
 * - Renders children as the main page content
 * - Manages sidebar open/close state for mobile responsiveness
 * - Manages dark mode state and applies the 'dark' class to <html>
 */
export default function Layout({ children }: { children: React.ReactNode }) {
  // State to control sidebar visibility on small screens
  const [sidebarOpen, setSidebarOpen] = useState(false);
  // State to control dark mode
  const [darkMode, setDarkMode] = useState(false);

  // Add/remove 'dark' class on <html> when darkMode changes
  useEffect(() => {
    const html = document.documentElement;
    if (darkMode) {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
  }, [darkMode]);

  // Handler to open sidebar
  const handleOpenSidebar = () => setSidebarOpen(true);
  // Handler to close sidebar
  const handleCloseSidebar = () => setSidebarOpen(false);
  // Handler to toggle dark mode
  const handleToggleDarkMode = () => setDarkMode((d) => !d);

  return (
    // No 'dark' class here; it's managed on <html>
    <div className="flex h-screen">
      {/* Sidebar: responsive and collapsible */}
      <Sidebar open={sidebarOpen} onClose={handleCloseSidebar} />
      <div className="flex-1 flex flex-col">
        {/* Topbar: passes handler to open sidebar on mobile and toggle dark mode */}
        <Topbar onMenuClick={handleOpenSidebar} onToggleDarkMode={handleToggleDarkMode} darkMode={darkMode} />
        {/* Main content area */}
        <main className="flex-1 bg-gray-50 dark:bg-gray-900 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  );
}