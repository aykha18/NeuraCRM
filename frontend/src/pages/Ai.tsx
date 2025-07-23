import { Link } from "react-router-dom";
// Minimal sample deals and getNextStepSuggestion for demo
const sampleDeals = [
  { id: "deal-1", title: "Acme Corp - Website Redesign", stage: "New" },
  { id: "deal-2", title: "Globex - CRM Migration", stage: "Qualified" },
  { id: "deal-3", title: "Initech - Support Contract", stage: "Proposal" },
  { id: "deal-4", title: "Umbrella - Security Audit", stage: "Won" },
  { id: "deal-5", title: "Wayne Enterprises - App Dev", stage: "Lost" },
];
function getNextStepSuggestion(deal: { stage: string }) {
  switch (deal.stage) {
    case "New": return "Qualify the lead";
    case "Qualified": return "Schedule a call or meeting";
    case "Proposal": return "Send proposal or follow up";
    case "Won": return "Onboard client";
    case "Lost": return "Review lost reason";
    default: return "Review deal";
  }
}
// Mock data for comments, attachments, and activity
const mockComments: Record<string, number[]> = {
  "deal-1": [1, 2],
  "deal-2": [1],
  "deal-3": [1, 2, 3],
  "deal-4": [],
  "deal-5": [1],
};
const mockAttachments: Record<string, number[]> = {
  "deal-1": [1],
  "deal-2": [],
  "deal-3": [1, 2],
  "deal-4": [1],
  "deal-5": [],
};
const mockActivity: Record<string, { timestamp: string }[]> = {
  "deal-1": [{ timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }], // 2 days ago
  "deal-2": [{ timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString() }], // 5 days ago
  "deal-3": [{ timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() }], // 1 day ago
  "deal-4": [],
  "deal-5": [{ timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString() }], // 10 days ago
};
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);
function getDealSummary(deal: { id: string; stage: string }, activity: Array<any> = [], comments: Array<any> = [], attachments: Array<any> = []) {
  const lastActivity = activity[0]?.timestamp ? dayjs(activity[0].timestamp).fromNow() : "No activity yet";
  return `${comments.length} comments, ${attachments.length} attachments, last activity ${lastActivity}, current stage: ${deal.stage}`;
}

// Chat/Chat Realtime feature list for demo
const chatFeatures = [
  { title: "1:1 Direct Messaging", desc: "Users can chat privately with other users" },
  { title: "Group Chat", desc: "Teams can collaborate in channels or group threads" },
  { title: "Message Storage", desc: "Chat messages are stored in the database with sender, content, and timestamp" },
  { title: "Real-Time Delivery", desc: "Messages are delivered instantly via WebSockets or Supabase Realtime" },
  { title: "Typing Indicators", desc: "Show when someone is typing (optional)" },
  { title: "Read Receipts", desc: "Show if a message was read (optional)" },
  { title: "Message History", desc: "Scroll to load old messages, infinite scroll or pagination" },
  { title: "Mentions", desc: "Use @username to ping a user (optional MVP+)" },
  { title: "Attachments", desc: "Upload images, files, or audio clips (optional MVP+)" },
  { title: "Presence Indicator", desc: "Show online/offline status (optional MVP+)" },
];

export default function Ai() {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      {/* Chat / Chat Realtime Feature Section */}
      <div className="mb-10 p-6 rounded-2xl bg-gradient-to-r from-blue-50 to-purple-100 dark:from-gray-800 dark:to-gray-900 shadow border border-blue-200 dark:border-gray-700">
        <h1 className="text-2xl font-extrabold mb-2 text-blue-700 dark:text-blue-300">Chat / Chat Realtime</h1>
        <ul className="list-disc pl-6 text-gray-800 dark:text-gray-100">
          {chatFeatures.map((f, idx) => (
            <li key={f.title + idx} className="mb-1">
              <span className="font-semibold text-blue-600 dark:text-blue-300">{f.title}:</span> {f.desc}
            </li>
          ))}
        </ul>
      </div>
      <h1 className="text-3xl font-extrabold mb-4 text-gray-900 dark:text-white">AI Features (Demo)</h1>
      <p className="mb-6 text-gray-700 dark:text-gray-200">
        This page showcases upcoming AI-powered features for your CRM:
      </p>
      <ul className="list-disc pl-6 mb-6 text-gray-800 dark:text-gray-100">
        <li className="mb-2"><span className="font-bold text-blue-600 dark:text-blue-300">AI Deal Scoring:</span> Predicts the likelihood of closing each deal based on deal data, stage, and activity.</li>
        <li className="mb-2"><span className="font-bold text-pink-600 dark:text-pink-300">AI Next Step Suggestions:</span> Recommends the most effective next action for each deal.</li>
        <li className="mb-2"><span className="font-bold text-green-600 dark:text-green-300">AI Summaries:</span> Summarizes deal history and activity for quick review.</li>
      </ul>
      <div className="mb-8">
        <p className="text-gray-600 dark:text-gray-400">You can see these features in action on the <Link to="/kanban" className="text-blue-500 underline">Kanban Board</Link>.</p>
      </div>
      {/* Demo Table for Next Step Suggestions */}
      <div className="mb-10">
        <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Demo: Next Step Suggestions</h2>
        <table className="min-w-full bg-white dark:bg-gray-800 rounded shadow overflow-hidden">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Deal Title</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Stage</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Next Step Suggestion</th>
            </tr>
          </thead>
          <tbody>
            {sampleDeals.map(deal => (
              <tr key={deal.id} className="border-b border-gray-200 dark:border-gray-700">
                <td className="px-4 py-2 text-gray-900 dark:text-white">{deal.title}</td>
                <td className="px-4 py-2 text-gray-700 dark:text-gray-300">{deal.stage}</td>
                <td className="px-4 py-2 text-pink-600 dark:text-pink-300 font-semibold">{getNextStepSuggestion(deal)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Demo Table for AI Summaries */}
      <div className="mb-10">
        <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">Demo: AI Summaries</h2>
        <table className="min-w-full bg-white dark:bg-gray-800 rounded shadow overflow-hidden">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Deal Title</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">AI Summary</th>
            </tr>
          </thead>
          <tbody>
            {sampleDeals.map(deal => (
              <tr key={deal.id + '-summary'} className="border-b border-gray-200 dark:border-gray-700">
                <td className="px-4 py-2 text-gray-900 dark:text-white">{deal.title}</td>
                <td className="px-4 py-2 text-green-700 dark:text-green-300 font-semibold">{getDealSummary(deal, mockActivity[deal.id], mockComments[deal.id], mockAttachments[deal.id])}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-10 text-center">
        <Link to="/kanban" className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition">Back to Kanban</Link>
      </div>
    </div>
  );
} 