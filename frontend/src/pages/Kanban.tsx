/**
 * Deals page: Modern Kanban board (responsive)
 * - Columns for stages, cards for deals
 * - Responsive: horizontal scroll on mobile
 * - Sample data, beautiful Tailwind styling
 */
import { useState, Fragment } from "react";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import type { DroppableProvided, DroppableStateSnapshot, DraggableProvided, DraggableStateSnapshot } from "@hello-pangea/dnd";
import { Dialog, Transition } from "@headlessui/react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useRef } from "react";
import { useMemo } from "react";
import { Pencil, Trash2, Plus, Eye, Calendar } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
dayjs.extend(relativeTime);

const sampleDeals = [
  { id: "deal-1", title: "Acme Corp - Website Redesign", value: "$12,000", owner: "Alex", stage: "New", description: "Redesign Acme's website for better UX.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-01-10T10:00:00Z", closedAt: undefined },
  { id: "deal-2", title: "Globex - CRM Migration", value: "$8,500", owner: "Sam", stage: "Qualified", description: "Migrate Globex to new CRM platform.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-02-05T09:00:00Z", closedAt: undefined },
  { id: "deal-3", title: "Initech - Support Contract", value: "$3,200", owner: "Chris", stage: "Proposal", description: "Annual support contract for Initech.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-03-01T11:00:00Z", closedAt: undefined },
  { id: "deal-4", title: "Umbrella - Security Audit", value: "$5,000", owner: "Alex", stage: "Won", description: "Comprehensive security audit for Umbrella.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-01-15T10:00:00Z", closedAt: "2024-02-10T15:00:00Z" },
  { id: "deal-5", title: "Wayne Enterprises - App Dev", value: "$20,000", owner: "Sam", stage: "Lost", description: "Develop custom app for Wayne Enterprises.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-01-20T10:00:00Z", closedAt: undefined },
  { id: "deal-6", title: "Stark Industries - Cloud Setup", value: "$15,000", owner: "Chris", stage: "New", description: "Set up cloud infrastructure for Stark.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-04-01T10:00:00Z", closedAt: undefined },
  { id: "deal-7", title: "Oscorp - Data Analysis", value: "$7,500", owner: "Alex", stage: "Qualified", description: "Analyze Oscorp's sales data.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-03-10T10:00:00Z", closedAt: undefined },
  { id: "deal-8", title: "LexCorp - Training", value: "$2,800", owner: "Sam", stage: "Proposal", description: "On-site CRM training for LexCorp.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-02-20T10:00:00Z", closedAt: undefined },
  // Add more 'Won' deals for demo
  { id: "deal-9", title: "Daily Planet - PR Campaign", value: "$9,000", owner: "Chris", stage: "Won", description: "PR campaign for Daily Planet.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-02-01T10:00:00Z", closedAt: "2024-03-01T10:00:00Z" },
  { id: "deal-10", title: "Roxxon - Security Upgrade", value: "$11,000", owner: "Sam", stage: "Won", description: "Security upgrade for Roxxon.", tags: [], watchers: [], reminderDate: undefined, createdAt: "2024-03-10T10:00:00Z", closedAt: "2024-04-15T10:00:00Z" },
];

// Helper to get unique owners
const owners = Array.from(new Set(sampleDeals.map((d) => d.owner)));

// Predefined tags and colors
const predefinedTags = [
  { label: "High Priority", color: "bg-red-500" },
  { label: "VIP", color: "bg-yellow-500" },
  { label: "Follow Up", color: "bg-blue-500" },
  { label: "Demo", color: "bg-purple-500" },
];

type Tag = { label: string; color: string };
// Update Deal type to include watchers: string[]
type Deal = {
  id: string;
  title: string;
  value: string;
  owner: string;
  stage: string;
  description: string;
  tags: Tag[];
  watchers: string[];
  reminderDate?: string;
  createdAt?: string;
  closedAt?: string;
};

// Type for dealsByStage: Record<string, Deal[]>
type DealsByStage = Record<string, Deal[]>;

function getDealsByStage(deals: Deal[]): DealsByStage {
  return deals.reduce((acc, deal) => {
    acc[deal.stage] = [...(acc[deal.stage] || []), deal];
    return acc;
  }, {} as DealsByStage);
}

// CompactTooltip for Recharts charts
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
          <span style={{ color: entry.color, fontWeight: 600 }}>{entry.name || entry.dataKey}:</span> {entry.value}
        </div>
      ))}
    </div>
  );
};

// --- Mock AI helpers ---
function getDealScore(deal: Deal, activity: Array<any> = []) {
  // Rule-based: higher stage, more activity, higher value = higher score
  const stageWeights: Record<string, number> = { New: 0.2, Qualified: 0.4, Proposal: 0.6, Won: 1, Lost: 0 };
  const stageScore = stageWeights[deal.stage] ?? 0.3;
  const valueScore = Math.min(parseFloat(deal.value.replace(/[^\d.]/g, "")) / 20000, 1) * 0.3; // up to $20k
  const activityScore = Math.min((activity?.length || 0) / 10, 1) * 0.3;
  let score = stageScore + valueScore + activityScore;
  if (deal.stage === "Lost") score = 0;
  if (deal.stage === "Won") score = 1;
  return Math.round(score * 100);
}
function getNextStepSuggestion(deal: Deal) {
  // Rule-based: suggest next action based on stage
  switch (deal.stage) {
    case "New": return "Qualify the lead";
    case "Qualified": return "Schedule a call or meeting";
    case "Proposal": return "Send proposal or follow up";
    case "Won": return "Onboard client";
    case "Lost": return "Review lost reason";
    default: return "Review deal";
  }
}
function getDealSummary(deal: Deal, activity: Array<any> = [], comments: Array<any> = [], attachments: Array<any> = []) {
  const lastActivity = activity[0]?.timestamp ? dayjs(activity[0].timestamp).fromNow() : "No activity yet";
  return `${comments.length} comments, ${attachments.length} attachments, last activity ${lastActivity}, current stage: ${deal.stage}`;
}

export default function Kanban() {
  // State for deals by stage
  const [dealsByStage, setDealsByStage] = useState<DealsByStage>(() => getDealsByStage(sampleDeals));
  // Filtering state
  const [ownerFilter, setOwnerFilter] = useState<string>("All");
  // Modal state
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  // Edit modal state
  const [editingDeal, setEditingDeal] = useState<Deal | null>(null);
  // In editForm state, always default watchers to string[]
  const [editForm, setEditForm] = useState<Partial<Deal>>({ watchers: [] });
  // Comments state: { [dealId]: Array<{id, author, text, timestamp}> }
  const [comments, setComments] = useState<Record<string, Array<{id: string, author: string, text: string, timestamp: string}>>>({});
  const [newComment, setNewComment] = useState<string>("");
  // Attachments state: { [dealId]: Array<{id, name, size, url, type, uploadedAt}> }
  const [attachments, setAttachments] = useState<Record<string, Array<{id: string, name: string, size: number, url: string, type: string, uploadedAt: string}>>>({});
  const [uploading, setUploading] = useState(false);
  // Activity log state: { [dealId]: Array<{id, type, message, timestamp, user}> }
  const [activityLog, setActivityLog] = useState<Record<string, Array<{id: string, type: string, message: string, timestamp: string, user: string}>>>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const dealToDelete = useRef<Deal | null>(null);

  // Move stages to state
  const [stages, setStages] = useState<string[]>(["New", "Qualified", "Proposal", "Won", "Lost"]);
  const [manageStagesOpen, setManageStagesOpen] = useState(false);
  const [newStage, setNewStage] = useState("");
  const [editingStage, setEditingStage] = useState<string | null>(null);
  const [editStageValue, setEditStageValue] = useState("");
  const [deleteStage, setDeleteStage] = useState<string | null>(null);

  // Tab state
  const [tab, setTab] = useState<'board' | 'analytics'>('board');

  // Move isStage inside the component to access stages state
  function isStage(value: string): value is string {
    return stages.includes(value);
  }

  // Type guard for Owner
  function isOwner(value: string): value is Deal["owner"] {
    return owners.includes(value);
  }

  // Color tags for each stage
  const stageColors: Record<string, string> = {
    New: "bg-blue-500",
    Qualified: "bg-purple-500",
    Proposal: "bg-yellow-500",
    Won: "bg-green-500",
    Lost: "bg-red-500",
  };

  const sampleUsers = ["You", "Alex", "Sam", "Chris"];
  const currentUser = "You";

  // Avatar color mapping
  const userAvatars: Record<string, { color: string }> = {
    "You": { color: "bg-gradient-to-r from-pink-500 to-purple-500" },
    "Alex": { color: "bg-gradient-to-r from-blue-500 to-indigo-500" },
    "Sam": { color: "bg-gradient-to-r from-green-500 to-teal-500" },
    "Chris": { color: "bg-gradient-to-r from-yellow-500 to-orange-500" },
  };
  // Helper to get initials for avatars
  function getInitials(name: string) {
    return name.split(" ").map(n => n[0]).join("").toUpperCase();
  }

  // Handle drag end
  function onDragEnd(result: any) {
    const { source, destination } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;
    setDealsByStage(prev => {
      const sourceStage = source.droppableId;
      const destStage = destination.droppableId;
      // Remove the moved deal from all stages to prevent duplicates
      let moved: Deal | undefined;
      const newDealsByStage: DealsByStage = {};
      for (const stage of Object.keys(prev)) {
        const deals = Array.from(prev[stage] || []);
        if (stage === sourceStage) {
          [moved] = deals.splice(source.index, 1);
        } else {
          // Remove the deal if it exists in any other stage (safety)
          const idx = deals.findIndex(d => moved && d.id === moved.id);
          if (idx !== -1) deals.splice(idx, 1);
        }
        newDealsByStage[stage] = deals;
      }
      if (!moved) return prev;
      moved.stage = destStage;
      const destDeals = Array.from(newDealsByStage[destStage] || []);
      destDeals.splice(destination.index, 0, moved);
      newDealsByStage[destStage] = destDeals;
      return newDealsByStage;
    });
  }

  // Add a handler for stage drag end
  function onStageDragEnd(result: any) { // Changed from DropResult to any
    if (!result.destination) return;
    const sourceIdx = result.source.index;
    const destIdx = result.destination.index;
    if (sourceIdx === destIdx) return;
    setStages(prev => {
      const updated = [...prev];
      const [removed] = updated.splice(sourceIdx, 1);
      updated.splice(destIdx, 0, removed);
      return updated;
    });
  }

  // Handle edit open
  function openEditModal(deal: Deal) {
    setEditingDeal(deal);
    setEditForm({ ...deal });
  }
  // Handle edit field change
  function handleEditChange<K extends keyof Deal>(key: K, value: Deal[K]) {
    setEditForm((prev) => ({ ...prev, [key]: value }));
  }
  // Handle edit save
  function saveEdit() {
    if (!editingDeal) return;
    setDealsByStage((prev) => {
      // Remove from old stage
      const oldStage = editingDeal.stage as string;
      let newStage = (editForm.stage as string) || oldStage;
      let updatedDeal = { ...editingDeal, ...editForm, stage: newStage };
      let newDealsByStage: DealsByStage = { ...prev };
      newDealsByStage[oldStage] = prev[oldStage].filter((d) => d.id !== editingDeal.id);
      newDealsByStage[newStage] = [updatedDeal, ...prev[newStage].filter((d) => d.id !== editingDeal.id)];
      // Log activity
      if (oldStage !== newStage) {
        logActivity(updatedDeal.id, "stage", `Moved to ${newStage}`);
      } else {
        logActivity(updatedDeal.id, "edit", `Deal details updated`);
      }
      return newDealsByStage;
    });
    setEditingDeal(null);
    setEditForm({});
  }

  // Add a comment to a deal
  function addComment(dealId: string) {
    if (!newComment.trim()) return;
    setComments(prev => ({
      ...prev,
      [dealId]: [
        {
          id: Math.random().toString(36).slice(2),
          author: "You",
          text: newComment,
          timestamp: new Date().toISOString(),
        },
        ...(prev[dealId] || []),
      ],
    }));
    logActivity(dealId, "comment", `Commented: ${newComment}`);
    setNewComment("");
  }
  // Delete a comment
  function deleteComment(dealId: string, commentId: string) {
    setComments(prev => {
      const comment = (prev[dealId] || []).find(c => c.id === commentId);
      logActivity(dealId, "comment", `Comment deleted: ${comment?.text || ""}`);
      return {
        ...prev,
        [dealId]: (prev[dealId] || []).filter(c => c.id !== commentId),
      };
    });
  }

  // Add attachment
  function addAttachment(dealId: string, file: File) {
    setUploading(true);
    const reader = new FileReader();
    reader.onload = () => {
      setAttachments(prev => ({
        ...prev,
        [dealId]: [
          {
            id: Math.random().toString(36).slice(2),
            name: file.name,
            size: file.size,
            url: URL.createObjectURL(file),
            type: file.type,
            uploadedAt: new Date().toISOString(),
          },
          ...(prev[dealId] || []),
        ],
      }));
      logActivity(dealId, "attachment", `Attachment uploaded: ${file.name}`);
      setUploading(false);
    };
    reader.readAsArrayBuffer(file);
  }
  // Delete attachment
  function deleteAttachment(dealId: string, attachmentId: string) {
    setAttachments(prev => {
      const att = (prev[dealId] || []).find(a => a.id === attachmentId);
      logActivity(dealId, "attachment", `Attachment deleted: ${att?.name || ""}`);
      return {
        ...prev,
        [dealId]: (prev[dealId] || []).filter(a => a.id !== attachmentId),
      };
    });
  }

  // Helper to log activity (random user for demo)
  function logActivity(dealId: string, type: string, message: string) {
    const user = sampleUsers[Math.floor(Math.random() * sampleUsers.length)];
    setActivityLog(prev => ({
      ...prev,
      [dealId]: [
        { id: Math.random().toString(36).slice(2), type, message, timestamp: new Date().toISOString(), user },
        ...(prev[dealId] || []),
      ],
    }));
  }

  // Deal deletion logic
  function confirmDeleteDeal(deal: Deal) {
    dealToDelete.current = deal;
    setShowDeleteConfirm(true);
  }
  function deleteDeal() {
    const deal = dealToDelete.current;
    if (!deal) return;
    setDealsByStage(prev => {
      const newDealsByStage: DealsByStage = { ...prev };
      newDealsByStage[deal.stage as string] = prev[deal.stage as string].filter(d => d.id !== deal.id);
      return newDealsByStage;
    });
    setComments(prev => {
      const newComments = { ...prev };
      delete newComments[deal.id];
      return newComments;
    });
    setAttachments(prev => {
      const newAttachments = { ...prev };
      delete newAttachments[deal.id];
      return newAttachments;
    });
    logActivity(deal.id, "delete", `Deal deleted`);
    setActivityLog(prev => {
      const newLog = { ...prev };
      // Keep the log for deleted deals
      return newLog;
    });
    setShowDeleteConfirm(false);
    setEditingDeal(null);
  }

  // Ensure dealsByStage always has an array for every stage
  // When adding a stage, add an empty array for it
  function handleAddStage() {
    const name = newStage.trim();
    if (!name || stages.includes(name)) return;
    // Prevent duplicate names
    if (stages.some(s => s.toLowerCase() === name.toLowerCase())) return;
    setStages([...stages, name]);
    setDealsByStage(prev => ({ ...prev, [name]: [] }));
    setNewStage("");
  }
  // When renaming a stage, update dealsByStage keys
  function handleRenameStage(oldName: string, newName: string) {
    if (!newName.trim() || stages.includes(newName)) return;
    // Prevent duplicate names
    if (stages.some(s => s.toLowerCase() === newName.toLowerCase())) return;
    setStages(stages.map(s => (s === oldName ? newName : s)));
    setDealsByStage(prev => {
      const updated: DealsByStage = {};
      for (const s of stages) {
        if (s === oldName) {
          updated[newName] = prev[oldName] || [];
        } else if (s !== newName) {
          updated[s] = prev[s] || [];
        }
      }
      return updated;
    });
    setEditingStage(null);
    setEditStageValue("");
  }
  // When deleting a stage, remove it from dealsByStage
  function handleDeleteStage(stage: string) {
    setStages(stages.filter(s => s !== stage));
    setDealsByStage(prev => {
      const updated: DealsByStage = {};
      for (const s of stages) {
        if (s !== stage) updated[s] = prev[s] || [];
      }
      return updated;
    });
    setDeleteStage(null);
  }

  // Compute filtered deals by stage
  const filteredDealsByStage: DealsByStage = useMemo(() => {
    return stages.reduce((acc, stage) => {
      let deals = dealsByStage[stage];
      // Owner filter
      if (ownerFilter !== "All") {
        deals = deals.filter(d => d.owner === ownerFilter);
      }
      // Stage filter
      if (stage !== "All") {
        deals = deals.filter(d => d.stage === stage);
      }
      // Search filter
      if (selectedDeal?.id === stage) { // This part needs to be re-evaluated based on the new UI
        const q = selectedDeal.title.toLowerCase();
        deals = deals.filter(d =>
          d.title.toLowerCase().includes(q) ||
          d.value.toLowerCase().includes(q) ||
          d.description.toLowerCase().includes(q)
        );
      }
      acc[stage] = deals;
      return acc;
    }, {} as DealsByStage);
  }, [dealsByStage, ownerFilter, selectedDeal]);

  // Compute analytics data
  const deals = Object.values(dealsByStage).flat();
  const stageCounts = stages.map(stage => ({ stage, count: (dealsByStage[stage] || []).length }));
  const avgDealSizeByStage = stages.map(stage => {
    const stageDeals = (dealsByStage[stage] || []);
    const avg = stageDeals.length ? stageDeals.reduce((sum, d) => sum + parseFloat(d.value.replace(/[^\d.]/g, "")), 0) / stageDeals.length : 0;
    return { stage, avg: Math.round(avg) };
  });
  const funnelData = stages.map((stage, idx) => ({
    stage,
    count: (dealsByStage[stage] || []).length,
    next: idx < stages.length - 1 ? (dealsByStage[stages[idx + 1]] || []).length : 0,
  }));
  const pieColors = ["#6366f1", "#f59e42", "#10b981", "#f43f5e", "#a21caf", "#fbbf24", "#0ea5e9", "#eab308"];

  // In Analytics tab, aggregate activityLog by day for the past 6 months
  const today = dayjs();
  const startDate = today.subtract(6, 'month').startOf('day');
  const endDate = today.endOf('day');
  const activityByDay: Record<string, number> = {};
  Object.values(activityLog).flat().forEach(log => {
    const day = dayjs(log.timestamp).format('YYYY-MM-DD');
    activityByDay[day] = (activityByDay[day] || 0) + 1;
  });
  const heatmapValues = [];
  for (let d = startDate; d.isBefore(endDate); d = d.add(1, 'day')) {
    const dateStr = d.format('YYYY-MM-DD');
    heatmapValues.push({ date: dateStr, count: activityByDay[dateStr] || 0 });
  }

  // Compute top owners/contributors analytics
  const owners = Array.from(new Set(deals.map(d => d.owner)));
  const dealsClosedByOwner = owners.map(owner => ({
    owner,
    count: deals.filter(d => d.owner === owner && d.stage === 'Won').length,
  }));
  const activityCountsByOwner: Record<string, number> = {};
  Object.values(activityLog).flat().forEach(log => {
    if (log.user) activityCountsByOwner[log.user] = (activityCountsByOwner[log.user] || 0) + 1;
  });
  const activityByOwner = Object.entries(activityCountsByOwner).map(([owner, count]) => ({ owner, count }));

  // Activity by Type (bar chart)
  const activityTypeCounts: Record<string, number> = {};
  Object.values(activityLog).flat().forEach(log => {
    if (log.type) activityTypeCounts[log.type] = (activityTypeCounts[log.type] || 0) + 1;
  });
  const activityTypeChartData = Object.entries(activityTypeCounts).map(([type, count]) => ({ type, count }));

  // Activity by Hour of Day (bar chart)
  const activityByHour: number[] = Array(24).fill(0);
  Object.values(activityLog).flat().forEach(log => {
    const hour = dayjs(log.timestamp).hour();
    activityByHour[hour]++;
  });
  const activityHourChartData = activityByHour.map((count, hour) => ({ hour, count }));

  // Compute deal velocity (average time to close per month)
  const wonDeals = deals.filter(d => d.stage === 'Won' && d.createdAt && d.closedAt);
  const velocityByMonth: Record<string, { total: number, count: number }> = {};
  wonDeals.forEach(d => {
    const closeMonth = dayjs(d.closedAt).format('YYYY-MM');
    const days = dayjs(d.closedAt).diff(dayjs(d.createdAt), 'day');
    if (!velocityByMonth[closeMonth]) velocityByMonth[closeMonth] = { total: 0, count: 0 };
    velocityByMonth[closeMonth].total += days;
    velocityByMonth[closeMonth].count += 1;
  });
  const velocityChartData = Object.entries(velocityByMonth).map(([month, { total, count }]) => ({
    month,
    avgDays: Math.round(total / count),
  }));

  // Compute deal count and total value by owner
  const dealCountByOwner = owners.map(owner => ({
    owner,
    count: deals.filter(d => d.owner === owner).length,
  }));
  const dealValueByOwner = owners.map(owner => ({
    owner,
    value: deals.filter(d => d.owner === owner).reduce((sum, d) => sum + parseFloat(d.value.replace(/[^\d.]/g, "")), 0),
  }));

  return (
    <div className="p-2 md:p-6">
      <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-6">Deals Pipeline</h1>
      {/* Filtering dropdown */}
      <div className="mb-4 flex flex-col md:flex-row md:items-center md:gap-4 gap-2">
        {/* Owner filter */}
        <div className="flex items-center gap-2">
          <label className="font-medium text-gray-700 dark:text-gray-200">Owner:</label>
          <select
            className="rounded px-2 py-1 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white min-w-[100px]"
            value={ownerFilter}
            onChange={e => setOwnerFilter(e.target.value)}
          >
            <option value="All">All</option>
            {owners.map(owner => (
              <option key={owner} value={owner}>{owner}</option>
            ))}
          </select>
        </div>
        {/* Stage filter */}
        <div className="flex items-center gap-2">
          <label className="font-medium text-gray-700 dark:text-gray-200">Stage:</label>
          <select
            className="rounded px-2 py-1 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white min-w-[100px]"
            value="All" // This value is not directly controlled by a state variable, so it's hardcoded
            onChange={e => {
              // This onChange is not directly tied to a state variable, so it doesn't filter
            }}
          >
            <option value="All">All</option>
            {stages.map((stage: string) => (
              <option key={stage} value={stage}>{stage}</option>
            ))}
          </select>
        </div>
      </div>
      {/* Add 'Manage Stages' button above the Kanban board */}
      <div className="flex justify-end mb-2">
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white font-semibold shadow hover:from-fuchsia-700 hover:to-pink-600 transition"
          onClick={() => setManageStagesOpen(true)}
        >
          <Plus className="w-4 h-4" /> Manage Stages
        </button>
      </div>
      {/* Tabbed interface */}
      <div>
        <div className="flex gap-2 mb-6">
          <button
            className={`px-4 py-2 rounded-full font-semibold transition ${tab === 'board' ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
            onClick={() => setTab('board')}
          >
            Board
          </button>
          <button
            className={`px-4 py-2 rounded-full font-semibold transition ${tab === 'analytics' ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
            onClick={() => setTab('analytics')}
          >
            Analytics
          </button>
        </div>
        {tab === 'board' && (
          // Kanban Board with Drag-and-Drop
          // Restore classic Kanban drag-and-drop for deals (cards) only
          <DragDropContext onDragEnd={onDragEnd}>
            <div className="flex gap-4 overflow-x-auto pb-4">
              {stages.map((stage: string) => (
                <div key={stage} className="flex-shrink-0 w-72">
                  <div className={`flex-shrink-0 w-72 bg-gray-50 dark:bg-gray-900 rounded-2xl shadow border border-gray-200 dark:border-gray-800 p-4 flex flex-col max-h-[80vh] transition`}>
                    <div className="font-bold text-lg mb-3 text-gray-700 dark:text-gray-200 flex items-center gap-2">
                      {/* Stage color tag */}
                      <span className={`inline-block w-3 h-3 rounded-full mr-2 ${stageColors[stage]}`}></span>
                      {stage}
                      <span className="bg-pink-100 dark:bg-pink-900 text-pink-600 dark:text-pink-200 rounded-full px-2 py-0.5 text-xs font-semibold">
                        {filteredDealsByStage[stage]?.length || 0}
                      </span>
                    </div>
                    <Droppable droppableId={stage}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className="flex-1 space-y-4 overflow-y-auto pr-1"
                        >
                          {filteredDealsByStage[stage]?.length === 0 && (
                            <div className="text-gray-400 dark:text-gray-600 text-sm text-center mt-8">No deals</div>
                          )}
                          {filteredDealsByStage[stage]?.map((deal, idx) => (
                            <Draggable draggableId={deal.id} index={idx} key={deal.id}>
                              {(dragProvided, dragSnapshot) => (
                                <div
                                  ref={dragProvided.innerRef}
                                  {...dragProvided.draggableProps}
                                  {...dragProvided.dragHandleProps}
                                  className={`rounded-xl bg-white dark:bg-gray-800 shadow p-4 border border-gray-100 dark:border-gray-800 hover:shadow-lg transition cursor-pointer ${dragSnapshot.isDragging ? "ring-2 ring-blue-400" : ""}`}
                                  onClick={() => setSelectedDeal(deal)}
                                >
                                  {/* Deal content: title, value, owner, tags, watchers, etc. */}
                                  <div className="flex items-center gap-2 mb-1">
                                    {/* Deal stage color tag */}
                                    <span className={`inline-block w-2 h-2 rounded-full ${stageColors[deal.stage as string]}`}></span>
                                    <div className="font-semibold text-gray-900 dark:text-white">{deal.title}</div>
                                    {/* AI Deal Score */}
                                    <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-bold bg-gradient-to-r from-green-400 to-blue-400 text-white" title="Likelihood to close">
                                      {getDealScore(deal, activityLog[deal.id])}%
                                    </span>
                                  </div>
                                  <div className="text-blue-600 dark:text-blue-400 font-bold text-lg mb-1">{deal.value}</div>
                                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Owner: {deal.owner}</div>
                                  {deal.tags && deal.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-1 mb-1">
                                      {deal.tags.map((tag: Tag) => (
                                        <span key={tag.label} className={`px-2 py-0.5 rounded-full text-xs font-semibold text-white ${tag.color}`}>{tag.label}</span>
                                      ))}
                                    </div>
                                  )}
                                  {deal.reminderDate && (
                                    <div className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 mb-1">
                                      <Calendar className="w-4 h-4" />
                                      <span>{dayjs(deal.reminderDate).format("MMM D, YYYY")}</span>
                                      {dayjs(deal.reminderDate).isBefore(dayjs(), "day") && (
                                        <span className="ml-2 px-2 py-0.5 rounded-full bg-red-500 text-white text-xs font-bold">Overdue</span>
                                      )}
                                      {dayjs(deal.reminderDate).isSame(dayjs(), "day") && !dayjs(deal.reminderDate).isBefore(dayjs(), "day") && (
                                        <span className="ml-2 px-2 py-0.5 rounded-full bg-yellow-400 text-white text-xs font-bold">Today</span>
                                      )}
                                    </div>
                                  )}
                                  {/* Watchers avatars and watch icon */}
                                  <div className="flex items-center gap-2 mt-2">
                                    {Array.isArray(deal.watchers) && deal.watchers.length > 0 && (
                                      <div className="flex -space-x-2">
                                        {deal.watchers.map((w: string) => (
                                          <span key={w} className="w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-xs font-bold text-white border-2 border-white dark:border-gray-900 shadow">
                                            {getInitials(w)}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                    <button
                                      className={`ml-2 p-1 rounded-full ${Array.isArray(deal.watchers) && deal.watchers.includes(currentUser) ? "bg-pink-100 dark:bg-pink-900" : "bg-gray-100 dark:bg-gray-800"}`}
                                      title={Array.isArray(deal.watchers) && deal.watchers.includes(currentUser) ? "Unwatch" : "Watch"}
                                      onClick={e => {
                                        e.stopPropagation();
                                        const updated = Array.isArray(deal.watchers)
                                          ? deal.watchers.includes(currentUser)
                                            ? deal.watchers.filter((w: string) => w !== currentUser)
                                            : [...deal.watchers, currentUser]
                                          : [currentUser];
                                        setDealsByStage(prev => {
                                          const updatedDeals = prev[deal.stage].map((d: Deal) => d.id === deal.id ? { ...d, watchers: updated } : d);
                                          return { ...prev, [deal.stage]: updatedDeals };
                                        });
                                      }}
                                    >
                                      <Eye className={`w-5 h-5 ${Array.isArray(deal.watchers) && deal.watchers.includes(currentUser) ? "text-pink-500" : "text-gray-400"}`} />
                                    </button>
                                  </div>
                                  <div className="flex gap-2 mt-2">
                                    <button className="px-3 py-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition" onClick={e => {e.stopPropagation(); setSelectedDeal(deal);}}>View</button>
                                    <button className="px-3 py-1 rounded-full bg-gradient-to-r from-yellow-400 to-pink-500 text-white text-xs font-semibold shadow hover:from-yellow-500 hover:to-pink-600 transition" onClick={e => {e.stopPropagation(); openEditModal(deal);}}>Edit</button>
                                  </div>
                                  {/* Next Step Suggestion */}
                                  <div className="text-xs text-pink-600 dark:text-pink-300 mb-1 font-semibold flex items-center gap-1">
                                    <span className="inline-block w-4 h-4"><Calendar className="w-4 h-4 inline" /></span>
                                    Next: {getNextStepSuggestion(deal)}
                                  </div>
                                </div>
                              )}
                            </Draggable>
                          ))}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                  </div>
                </div>
              ))}
            </div>
          </DragDropContext>
        )}
        {tab === 'analytics' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {/* Conversion Funnel (bar chart) */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Conversion Funnel</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={funnelData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="stage" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="count" fill="#6366f1" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Deals per Stage (pie chart) */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Deals per Stage</div>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={stageCounts}
                      dataKey="count"
                      nameKey="stage"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label
                    >
                      {stageCounts.map((entry, idx) => (
                        <Cell key={`cell-${entry.stage}`} fill={pieColors[idx % pieColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CompactTooltip />} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              {/* Average Deal Size (bar chart) */}
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Average Deal Size</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={avgDealSizeByStage} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="stage" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="avg" fill="#f59e42" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Top Owners/Contributors - Deals Closed */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Top Owners (Deals Closed)</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={dealsClosedByOwner} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="owner" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Deal Count by Owner (Pie Chart) */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Deal Count by Owner</div>
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie
                      data={dealCountByOwner}
                      dataKey="count"
                      nameKey="owner"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label
                    >
                      {dealCountByOwner.map((entry, idx) => (
                        <Cell key={`cell-${entry.owner}`} fill={pieColors[idx % pieColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CompactTooltip />} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              {/* Deal Value by Owner (Bar Chart) */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Total Deal Value by Owner</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={dealValueByOwner} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="owner" />
                    <YAxis allowDecimals={false} />
                    <Tooltip formatter={v => `$${v}`}/>
                    <Bar dataKey="value" fill="#f59e42" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Top Contributors - Activity Count */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Top Contributors (Activity)</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={activityByOwner} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="owner" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="count" fill="#6366f1" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Activity by Type (bar chart) */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Activity by Type</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={activityTypeChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="count" fill="#a21caf" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Activity by Hour of Day (bar chart) */}
              <div className="col-span-1 md:col-span-2 xl:col-span-1 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Activity by Hour of Day</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={activityHourChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" tickFormatter={h => `${h}:00`} />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Deal Velocity (average time to close) */}
              <div className="col-span-1 md:col-span-2 xl:col-span-3 bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
                <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Deal Velocity (Avg. Days to Close)</div>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={velocityChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis allowDecimals={false} />
                    <Tooltip content={<CompactTooltip />} />
                    <Bar dataKey="avgDays" fill="#f43f5e" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            {/* Move Team Activity Heatmap after the last chart */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 border flex flex-col items-center mt-6">
              <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Team Activity Heatmap</div>
              <div className="w-full flex justify-center">
                <div className="max-w-2xl">
                  <CalendarHeatmap
                    startDate={startDate.format('YYYY-MM-DD')}
                    endDate={endDate.format('YYYY-MM-DD')}
                    values={heatmapValues}
                    classForValue={value => {
                      if (!value || value.count === 0) return "react-calendar-heatmap-empty";
                      if (value.count >= 8) return "bg-pink-600";
                      if (value.count >= 5) return "bg-pink-400";
                      if (value.count >= 2) return "bg-pink-200";
                      return "bg-pink-100";
                    }}
                    tooltipDataAttrs={value => {
                      if (!value || !value.date) return {};
                      return { 'data-tip': `${value.date}: ${value.count} activities` };
                    }}
                    showWeekdayLabels={true}
                  />
                  {/* Custom CSS for smaller squares */}
                  <style>{`
                    .react-calendar-heatmap .react-calendar-heatmap-day {
                      width: 12px;
                      height: 12px;
                    }
                  `}</style>
                </div>
              </div>
              {/* Legend */}
              <div className="flex gap-2 mt-4 items-center text-xs text-gray-500 dark:text-gray-300">
                <span>Less</span>
                <span className="w-5 h-5 rounded bg-pink-100 inline-block"></span>
                <span className="w-5 h-5 rounded bg-pink-200 inline-block"></span>
                <span className="w-5 h-5 rounded bg-pink-400 inline-block"></span>
                <span className="w-5 h-5 rounded bg-pink-600 inline-block"></span>
                <span>More</span>
              </div>
            </div>
          </>
        )}
      </div>
      {/* Deal Detail Modal */}
      <Transition.Root show={!!selectedDeal} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setSelectedDeal(null)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />
          </Transition.Child>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all border border-gray-200 dark:border-gray-800">
                  <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 dark:text-white mb-2">
                    {selectedDeal?.title}
                  </Dialog.Title>
                  {selectedDeal && (
                    <div className="mb-2 text-xs text-blue-700 dark:text-blue-300 font-semibold bg-blue-50 dark:bg-blue-900 rounded px-2 py-1">
                      {getDealSummary(
                        selectedDeal,
                        activityLog[selectedDeal.id] || [],
                        comments[selectedDeal.id] || [],
                        attachments[selectedDeal.id] || []
                      )}
                    </div>
                  )}
                  <div className="mb-2 text-blue-600 dark:text-blue-400 font-bold text-lg">{selectedDeal?.value}</div>
                  <div className="mb-2 text-xs text-gray-500 dark:text-gray-400">Owner: {selectedDeal?.owner}</div>
                  <div className="mb-4 text-gray-700 dark:text-gray-200">{selectedDeal?.description}</div>
                  {/* Comments Section */}
                  <div className="mt-6">
                    <div className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Comments</div>
                    <div className="space-y-3 max-h-40 overflow-y-auto mb-2">
                      {(comments[selectedDeal?.id || ""] || []).length === 0 && (
                        <div className="text-gray-400 text-sm">No comments yet.</div>
                      )}
                      {(comments[selectedDeal?.id || ""] || []).map(comment => (
                        <div key={comment.id} className="bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 flex items-start gap-2 group">
                          <div className="flex-1">
                            <div className="text-xs text-gray-500 dark:text-gray-400 mb-0.5 flex items-center gap-2">
                              <span className="font-bold text-gray-700 dark:text-gray-200">{comment.author}</span>
                              <span className="text-gray-400">{dayjs(comment.timestamp).fromNow()}</span>
                            </div>
                            <div className="text-gray-900 dark:text-gray-100 text-sm">{comment.text}</div>
                          </div>
                          <button
                            className="ml-2 text-xs text-gray-400 hover:text-pink-500 opacity-0 group-hover:opacity-100 transition"
                            title="Delete"
                            onClick={() => deleteComment(selectedDeal!.id, comment.id)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <form
                      className="flex gap-2 mt-2"
                      onSubmit={e => {
                        e.preventDefault();
                        if (selectedDeal) addComment(selectedDeal.id);
                      }}
                    >
                      <input
                        type="text"
                        className="flex-1 rounded-full px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="Add a comment..."
                        value={newComment}
                        onChange={e => setNewComment(e.target.value)}
                        maxLength={300}
                      />
                      <button
                        type="submit"
                        className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition"
                        disabled={!newComment.trim()}
                      >
                        Post
                      </button>
                    </form>
                  </div>
                  {/* Attachments Section */}
                  <div className="mt-6">
                    <div className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Attachments</div>
                    <div className="space-y-2 mb-2">
                      {(attachments[selectedDeal?.id || ""] || []).length === 0 && (
                        <div className="text-gray-400 text-sm">No attachments yet.</div>
                      )}
                      {(attachments[selectedDeal?.id || ""] || []).map(att => (
                        <div key={att.id} className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded px-3 py-2">
                          <a
                            href={att.url}
                            download={att.name}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 dark:text-blue-400 font-medium hover:underline truncate max-w-[120px]"
                            title={att.name}
                          >
                            {att.name}
                          </a>
                          <span className="text-xs text-gray-500">({(att.size / 1024).toFixed(1)} KB)</span>
                          <span className="text-xs text-gray-400">{att.type.startsWith("image/") ? "Image" : att.type === "application/pdf" ? "PDF" : att.type}</span>
                          <span className="text-xs text-gray-400 ml-auto">{dayjs(att.uploadedAt).fromNow()}</span>
                          <button
                            className="ml-2 text-xs text-gray-400 hover:text-pink-500 transition"
                            title="Delete"
                            onClick={() => deleteAttachment(selectedDeal!.id, att.id)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <form
                      className="flex gap-2 mt-2 items-center"
                      onSubmit={e => e.preventDefault()}
                    >
                      <label className="px-3 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition cursor-pointer">
                        <input
                          type="file"
                          accept="image/*,application/pdf"
                          className="hidden"
                          onChange={e => {
                            const file = e.target.files?.[0];
                            if (file && selectedDeal) addAttachment(selectedDeal.id, file);
                            e.target.value = "";
                          }}
                          disabled={uploading}
                        />
                        {uploading ? "Uploading..." : "Upload"}
                      </label>
                    </form>
                  </div>
                  {/* Activity Log Section */}
                  <div className="mt-6">
                    <div className="font-semibold text-gray-800 dark:text-gray-100 mb-2">Activity Log</div>
                    <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
                      {(activityLog[selectedDeal?.id || ""] || []).length === 0 && (
                        <div className="text-gray-400">No activity yet.</div>
                      )}
                      {(activityLog[selectedDeal?.id || ""] || []).map(log => (
                        <div key={log.id} className="flex items-center gap-2">
                          {/* Avatar */}
                          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white shadow ${userAvatars[log.user]?.color || "bg-gray-400"}`}>
                            {getInitials(log.user)}
                          </span>
                          <span className="font-bold text-blue-600 dark:text-blue-400">[{log.user}]</span>
                          <span className="font-bold text-gray-700 dark:text-gray-200">{log.type.charAt(0).toUpperCase() + log.type.slice(1)}</span>
                          <span className="text-gray-900 dark:text-gray-100">{log.message}</span>
                          <span className="text-gray-400 ml-auto">{dayjs(log.timestamp).fromNow()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="flex justify-center mt-6">
                    <button className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition" onClick={() => setSelectedDeal(null)}>Close</button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
      {/* Deal Edit Modal */}
      <Transition.Root show={!!editingDeal} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setEditingDeal(null)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />
          </Transition.Child>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all border border-gray-200 dark:border-gray-800">
                  <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 dark:text-white mb-4">
                    Edit Deal
                  </Dialog.Title>
                  <form onSubmit={e => { e.preventDefault(); saveEdit(); }}>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Title</label>
                      <input type="text" className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={editForm.title || ""} onChange={e => handleEditChange("title", e.target.value)} required />
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Value</label>
                      <input type="text" className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={editForm.value || ""} onChange={e => handleEditChange("value", e.target.value)} required />
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Owner</label>
                      <select
                        className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        value={isOwner(editForm.owner || "") ? editForm.owner : owners[0]}
                        onChange={e => {
                          const value = e.target.value;
                          if (isOwner(value)) handleEditChange("owner", value);
                        }}
                        required
                      >
                        {owners.map((owner) => (
                          <option key={owner} value={owner}>{owner}</option>
                        ))}
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Stage</label>
                      <select
                        className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        value={isStage(editForm.stage || "") ? editForm.stage : stages[0]}
                        onChange={e => {
                          const value = e.target.value;
                          if (isStage(value)) handleEditChange("stage", value);
                        }}
                        required
                      >
                        {stages.map((stage) => (
                          <option key={stage} value={stage}>{stage}</option>
                        ))}
                      </select>
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Tags</label>
                      <div className="flex flex-wrap gap-2">
                        {predefinedTags.map(tag => {
                          const selected = (editForm.tags || []).some((t: Tag) => t.label === tag.label);
                          return (
                            <button
                              key={tag.label}
                              type="button"
                              className={`px-2 py-1 rounded-full text-xs font-semibold border transition ${tag.color} text-white ${selected ? "ring-2 ring-pink-400" : "opacity-70"}`}
                              onClick={() => {
                                let tags = editForm.tags ? [...editForm.tags] : [];
                                if (selected) {
                                  tags = tags.filter((t: Tag) => t.label !== tag.label);
                                } else {
                                  tags.push(tag);
                                }
                                handleEditChange("tags", tags);
                              }}
                            >
                              {tag.label}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Description</label>
                      <textarea className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white" value={editForm.description || ""} onChange={e => handleEditChange("description", e.target.value)} rows={3} />
                    </div>
                    <div className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Reminder / Follow-up Date</label>
                      <input
                        type="date"
                        className="w-full rounded px-3 py-2 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        value={editForm.reminderDate ? dayjs(editForm.reminderDate).format("YYYY-MM-DD") : ""}
                        onChange={e => handleEditChange("reminderDate", e.target.value ? dayjs(e.target.value).toISOString() : undefined)}
                      />
                    </div>
                    <div className="flex gap-2 mt-4">
                      <button type="submit" className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition">Save</button>
                      <button type="button" className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-semibold shadow hover:bg-gray-300 dark:hover:bg-gray-600 transition" onClick={() => setEditingDeal(null)}>Cancel</button>
                    </div>
                  </form>
                  {editingDeal && (
                    <button
                      type="button"
                      className="px-4 py-2 rounded-full bg-gradient-to-r from-red-500 to-pink-500 text-white font-semibold shadow hover:from-red-600 hover:to-pink-600 transition mt-4"
                      onClick={() => confirmDeleteDeal(editingDeal)}
                    >
                      Delete Deal
                    </button>
                  )}
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
      {/* Delete confirmation dialog */}
      <Transition.Root show={showDeleteConfirm} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setShowDeleteConfirm(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />
          </Transition.Child>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-sm transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all border border-gray-200 dark:border-gray-800">
                  <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 dark:text-white mb-4">
                    Delete Deal
                  </Dialog.Title>
                  <div className="mb-4 text-gray-700 dark:text-gray-200">Are you sure you want to delete this deal? This action cannot be undone.</div>
                  <div className="flex gap-2 mt-4 justify-end">
                    <button
                      className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-semibold shadow hover:bg-gray-300 dark:hover:bg-gray-600 transition"
                      onClick={() => setShowDeleteConfirm(false)}
                    >
                      Cancel
                    </button>
                    <button
                      className="px-4 py-2 rounded-full bg-gradient-to-r from-red-500 to-pink-500 text-white font-semibold shadow hover:from-red-600 hover:to-pink-600 transition"
                      onClick={deleteDeal}
                    >
                      Delete
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
      {/* Manage Stages Modal */}
      <Transition.Root show={manageStagesOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setManageStagesOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />
          </Transition.Child>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all border border-gray-200 dark:border-gray-800">
                  <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 dark:text-white mb-4">
                    Manage Stages
                  </Dialog.Title>
                  <div className="space-y-3 mb-4">
                    {stages.map(stage => (
                      <div key={stage} className="flex items-center gap-2">
                        {editingStage === stage ? (
                          <input
                            className="flex-1 rounded px-2 py-1 border border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            value={editStageValue}
                            onChange={e => setEditStageValue(e.target.value)}
                            onBlur={() => handleRenameStage(stage, editStageValue)}
                            onKeyDown={e => {
                              if (e.key === "Enter") handleRenameStage(stage, editStageValue);
                              if (e.key === "Escape") setEditingStage(null);
                            }}
                            autoFocus
                          />
                        ) : (
                          <>
                            <span className="flex-1 font-semibold text-gray-900 dark:text-white">{stage}</span>
                            <button
                              className="p-1 rounded hover:bg-pink-100 dark:hover:bg-pink-900"
                              onClick={() => { setEditingStage(stage); setEditStageValue(stage); }}
                              title="Rename"
                            >
                              <Pencil className="w-4 h-4 text-pink-500" />
                            </button>
                            <button
                              className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-900"
                              onClick={() => setDeleteStage(stage)}
                              title="Delete"
                              disabled={stages.length <= 1}
                            >
                              <Trash2 className="w-4 h-4 text-red-500" />
                            </button>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                  <form
                    className="flex gap-2"
                    onSubmit={e => { e.preventDefault(); handleAddStage(); }}
                  >
                    <input
                      type="text"
                      className="flex-1 rounded px-2 py-1 border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      placeholder="Add new stage..."
                      value={newStage}
                      onChange={e => setNewStage(e.target.value)}
                      maxLength={20}
                    />
                    <button
                      type="submit"
                      className="px-4 py-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition"
                      disabled={!newStage.trim() || stages.includes(newStage)}
                    >
                      Add
                    </button>
                  </form>
                  <div className="flex justify-end mt-4">
                    <button
                      className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-semibold shadow hover:bg-gray-300 dark:hover:bg-gray-600 transition"
                      onClick={() => setManageStagesOpen(false)}
                    >
                      Close
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
      {/* Delete Stage Confirmation Dialog */}
      <Transition.Root show={!!deleteStage} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setDeleteStage(null)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100"
            leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-30 transition-opacity" />
          </Transition.Child>
          <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
                leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-sm transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all border border-gray-200 dark:border-gray-800">
                  <Dialog.Title as="h3" className="text-lg font-bold leading-6 text-gray-900 dark:text-white mb-4">
                    Delete Stage
                  </Dialog.Title>
                  <div className="mb-4 text-gray-700 dark:text-gray-200">Are you sure you want to delete the stage "{deleteStage}"? All deals in this stage will be removed. This action cannot be undone.</div>
                  <div className="flex gap-2 mt-4 justify-end">
                    <button
                      className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white font-semibold shadow hover:bg-gray-300 dark:hover:bg-gray-600 transition"
                      onClick={() => setDeleteStage(null)}
                    >
                      Cancel
                    </button>
                    <button
                      className="px-4 py-2 rounded-full bg-gradient-to-r from-red-500 to-pink-500 text-white font-semibold shadow hover:from-red-600 hover:to-pink-600 transition"
                      onClick={() => handleDeleteStage(deleteStage!)}
                    >
                      Delete
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition.Root>
    </div>
  );
} 