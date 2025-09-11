import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Contacts from "./pages/contaxt";
import Kanban from "./pages/Kanban";
import Chat from "./pages/Chat";
import Ai from "./pages/Ai";
import EmailAutomation from "./pages/EmailAutomation";
import { UserProvider } from "./contexts/UserContext";

/**
 * App component sets up the main routing for the CRM application.
 * - Uses React Router for client-side navigation
 * - Wraps all pages in the Layout component (sidebar + topbar)
 * - Defines routes for Dashboard, Leads, Contacts, Kanban, and Chat pages
 */
function App() {
  return (
    // Router provides navigation context for the app
    <UserProvider>
      <Router>
        {/* Layout provides sidebar and topbar for all pages */}
        <Layout>
          {/* Routes define which page component to render for each path */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/contacts" element={<Contacts />} />
            <Route path="/kanban" element={<Kanban />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/ai" element={<Ai />} />
            <Route path="/email-automation" element={<EmailAutomation />} />
          </Routes>
        </Layout>
      </Router>
    </UserProvider>
  );
}

export default App;
