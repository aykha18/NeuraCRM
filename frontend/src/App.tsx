import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Contacts from "./pages/Contacts";
import Kanban from "./pages/Kanban";
import Chat from "./pages/Chat";
import Ai from "./pages/Ai";

/**
 * App component sets up the main routing for the CRM application.
 * - Uses React Router for client-side navigation
 * - Wraps all pages in the Layout component (sidebar + topbar)
 * - Defines routes for Dashboard, Leads, Contacts, Kanban, and Chat pages
 */
function App() {
  return (
    // Router provides navigation context for the app
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
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
