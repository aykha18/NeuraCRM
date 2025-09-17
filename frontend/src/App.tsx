import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Leads from "./pages/Leads";
import Contacts from "./pages/contaxt";
import Kanban from "./pages/Kanban";
import Chat from "./pages/Chat";
import Ai from "./pages/Ai";
import AIHelpGuide from "./pages/AIHelpGuide";
import EmailAutomation from "./pages/EmailAutomation";
import PredictiveAnalytics from "./pages/PredictiveAnalytics";
import UserManagement from "./pages/UserManagement";
import Landing from "./pages/Landing";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/SignIn";
import Logout from "./pages/Logout";
import OrganizationSignup from "./pages/OrganizationSignup";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";
import { UserProvider } from "./contexts/UserContext";

/**
 * App component sets up the main routing for the CRM application.
 * - Uses React Router for client-side navigation
 * - Wraps all pages in the Layout component (sidebar + topbar)
 * - Defines routes for Dashboard, Leads, Contacts, Kanban, and Chat pages
 */
function App() {
  return (
    // AuthProvider provides authentication context for the app
    <AuthProvider>
      <UserProvider>
        <Router>
          {/* Routes define which page component to render for each path */}
          <Routes>
            {/* Public routes (no layout) */}
            <Route path="/" element={<Landing />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/organization-signup" element={<OrganizationSignup />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/logout" element={<Logout />} />
            
            {/* Protected routes (with layout) */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/leads" element={
              <ProtectedRoute>
                <Layout>
                  <Leads />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/contacts" element={
              <ProtectedRoute>
                <Layout>
                  <Contacts />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/kanban" element={
              <ProtectedRoute>
                <Layout>
                  <Kanban />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/chat" element={
              <ProtectedRoute>
                <Layout>
                  <Chat />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/ai" element={
              <ProtectedRoute>
                <Layout>
                  <Ai />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/ai-help" element={
              <ProtectedRoute>
                <Layout>
                  <AIHelpGuide />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/email-automation" element={
              <ProtectedRoute>
                <Layout>
                  <EmailAutomation />
                </Layout>
              </ProtectedRoute>
            } />
            <Route path="/predictive-analytics" element={
              <ProtectedRoute>
                <Layout>
                  <PredictiveAnalytics />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/user-management" element={
              <ProtectedRoute>
                <Layout>
                  <UserManagement />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Catch-all route for unknown paths */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </UserProvider>
    </AuthProvider>
  );
}

export default App;
