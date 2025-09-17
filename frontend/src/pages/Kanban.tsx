/**
 * Deals page: Modern Kanban board (responsive)
 * - Columns for stages, cards for deals
 * - Responsive: horizontal scroll on mobile
 * - Beautiful Tailwind styling with backend integration
 */
import { useState, useMemo, useCallback, useRef } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import type { DropResult } from '@hello-pangea/dnd';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getKanbanBoard, moveDeal, watchDeal, unwatchDeal, updateDeal, type KanbanBoard as ApiKanbanBoard, type Deal as ApiDeal } from '../services/kanban';
import StageManagementModal from '../components/StageManagementModal';
import { Plus, Eye, Calendar } from 'lucide-react';
// import { Dialog, Transition } from '@headlessui/react';
import DetailModal from '../components/DetailModal';
import AnimatedModal from '../components/AnimatedModal';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
// import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

// Define the Tag type
type Tag = { label: string; color: string };

// Frontend-specific Deal type that extends the API Deal type
type FrontendDeal = Omit<ApiDeal, 'value' | 'owner_id' | 'contact_id' | 'stage_id' | 'id'> & {
  id: string; // Ensure ID is string for dnd-kit
  value: string;
  owner: string;
  stage: string;
  tags: Tag[];
  watchers: string[];
  reminderDate?: string;
  closedAt?: string;
  stage_id: number; // Add back stage_id for backend operations
  createdAt?: string;
  updatedAt?: string;
};

// Type for dealsByStage: Record<number, FrontendDeal[]>
type DealsByStage = Record<number, FrontendDeal[]>;

// Predefined tags and colors
const predefinedTags = [
  { label: "High Priority", color: "bg-red-500" },
  { label: "VIP", color: "bg-yellow-500" },
  { label: "Follow Up", color: "bg-blue-500" },
  { label: "Demo", color: "bg-purple-500" },
];

// Sample users for demo
// const sampleUsers = ["You", "Alex", "Sam", "Chris"];
// const currentUser = 'Imran Patel';

// Avatar color mapping
// const userAvatars: Record<string, { color: string }> = {
//   "You": { color: "bg-gradient-to-r from-pink-500 to-purple-500" },
//   "Alex": { color: "bg-gradient-to-r from-blue-500 to-indigo-500" },
//   "Sam": { color: "bg-gradient-to-r from-green-500 to-teal-500" },
//   "Chris": { color: "bg-gradient-to-r from-yellow-500 to-orange-500" },
// };

// Color tags for each stage
const stageColors: Record<string, string> = {
  New: "bg-blue-500",
  Contacted: "bg-purple-500",
  "Proposal Sent": "bg-yellow-500",
  Negotiation: "bg-green-500",
  Won: "bg-green-500",
  Lost: "bg-red-500",
};

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

// AI helper functions
function getDealScore(deal: FrontendDeal, activity: Array<any> = []) {
  const stageWeights: Record<string, number> = { New: 0.2, Contacted: 0.4, "Proposal Sent": 0.6, Negotiation: 0.8, Won: 1, Lost: 0 };
  const stageScore = stageWeights[deal.stage] ?? 0.3;
  const valueScore = Math.min(parseFloat(deal.value.replace(/[^\d.]/g, "")) / 20000, 1) * 0.3;
  const activityScore = Math.min((activity?.length || 0) / 10, 1) * 0.3;
  let score = stageScore + valueScore + activityScore;
  if (deal.stage === "Lost") score = 0;
  if (deal.stage === "Won") score = 1;
  return Math.round(score * 100);
}

function getNextStepSuggestion(deal: FrontendDeal) {
  switch (deal.stage) {
    case "New": return "Contact the lead";
    case "Contacted": return "Send proposal";
    case "Proposal Sent": return "Follow up";
    case "Negotiation": return "Close the deal";
    case "Won": return "Onboard client";
    case "Lost": return "Review lost reason";
    default: return "Review deal";
  }
}

// function getDealSummary(deal: FrontendDeal, activity: Array<any> = [], comments: Array<any> = [], attachments: Array<any> = []) {
//   const lastActivity = activity[0]?.timestamp ? dayjs(activity[0].timestamp).fromNow() : "No activity yet";
//   return `${comments.length} comments, ${attachments.length} attachments, last activity ${lastActivity}, current stage: ${deal.stage}`;
// }

// Helper to get initials for avatars
function getInitials(name: string) {
  return name.split(" ").map(n => n[0]).join("").toUpperCase();
}

// Main Kanban component
export default function Kanban() {
  const queryClient = useQueryClient();
  
  // State for UI
  const [selectedDeal, setSelectedDeal] = useState<FrontendDeal | null>(null);
  const [isDealModalOpen, setIsDealModalOpen] = useState(false);
  const [isManageStagesOpen, setIsManageStagesOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'board' | 'analytics'>('board');
  
  // State for filtering
  const [ownerFilter, setOwnerFilter] = useState<string>("All");
  
  // State for modals
  const [editingDeal, setEditingDeal] = useState<FrontendDeal | null>(null);
  const [editForm, setEditForm] = useState<Partial<FrontendDeal>>({ watchers: [] });
  const [savingEdit, setSavingEdit] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const dealToDelete = useRef<FrontendDeal | null>(null);
  
  // State for comments and attachments
  const [comments, setComments] = useState<Record<string, Array<{id: string, author: string, text: string, timestamp: string}>>>({});
  const [newComment, setNewComment] = useState<string>("");
  const [attachments, setAttachments] = useState<Record<string, Array<{id: string, name: string, size: number, url: string, type: string, uploadedAt: string}>>>({});
  const [uploading, setUploading] = useState(false);
  
  // State for activity log
  const [activityLog, setActivityLog] = useState<Record<string, Array<{id: string, type: string, message: string, timestamp: string, user: string}>>>({});
  
  // State for stage management
  // const [newStage, setNewStage] = useState("");
  // const [editingStage, setEditingStage] = useState<string | null>(null);
  // const [editStageValue, setEditStageValue] = useState("");
  const [deleteStage, setDeleteStage] = useState<string | null>(null);
  
  // State for watch loading
  const [watchLoading, setWatchLoading] = useState<number | null>(null);

  // Fetch kanban data
  const { data: kanbanData, isLoading, error } = useQuery<ApiKanbanBoard>({
    queryKey: ['kanban'],
    queryFn: getKanbanBoard,
  });

  // Group deals by stage
  const dealsByStage = useMemo<DealsByStage>(() => {
    if (!kanbanData?.deals || !kanbanData?.stages) return {};
    
      const stageMap = new Map<number, string>();
    kanbanData.stages.forEach(stage => stageMap.set(stage.id, stage.name));
    
    return kanbanData.deals.reduce((acc, deal) => {
      const stageId = deal.stage_id;
      if (!acc[stageId]) {
        acc[stageId] = [];
      }
      
      // Convert API deal to frontend deal format
      const frontendDeal: FrontendDeal = {
        ...deal,
        id: String(deal.id),
        value: `$${deal.value?.toLocaleString() || '0'}`,
        owner: deal.owner_name || 'Unassigned',
        stage: stageMap.get(stageId) || 'Unknown',
        tags: [],
        watchers: deal.watchers || [],
      };
      
      acc[stageId].push(frontendDeal);
      return acc;
    }, {} as DealsByStage);
  }, [kanbanData]);

  // Get sorted stages
  const stages = useMemo(() => {
    if (!kanbanData?.stages) return [];
    return [...kanbanData.stages].sort((a, b) => a.order - b.order);
  }, [kanbanData?.stages]);

  // Get unique owners for filtering
  const owners = useMemo(() => {
    const allDeals = Object.values(dealsByStage).flat();
    return Array.from(new Set(allDeals.map(d => d.owner)));
  }, [dealsByStage]);

  // Mock current user
  const currentUser = 'Imran Patel';
  
  // Mock user avatars for activity log
  const userAvatars: Record<string, {color: string}> = {
    'Alex': { color: 'bg-blue-500' },
    'Sam': { color: 'bg-green-500' },
    'Chris': { color: 'bg-purple-500' },
  };

  // Activity logging functions
  const logActivity = useCallback((dealId: string, type: string, message: string) => {
    const newActivity = {
      id: Date.now().toString(),
      user: currentUser,
      type,
      message,
      timestamp: new Date().toISOString(),
    };
    setActivityLog(prev => ({
      ...prev,
      [dealId]: [...(prev[dealId] || []), newActivity]
    }));
  }, [currentUser]);

  // Comment functions
  const addComment = useCallback((dealId: string) => {
    if (!newComment.trim()) return;
    
    const comment = {
      id: Date.now().toString(),
      author: currentUser,
      text: newComment.trim(),
      timestamp: new Date().toISOString(),
    };
    
    setComments(prev => ({
      ...prev,
      [dealId]: [...(prev[dealId] || []), comment]
    }));
    
    setNewComment("");
    logActivity(dealId, "comment", `Added a comment`);
  }, [newComment, currentUser, logActivity]);

  const deleteComment = useCallback((dealId: string, commentId: string) => {
    setComments(prev => ({
        ...prev,
      [dealId]: (prev[dealId] || []).filter(c => c.id !== commentId)
    }));
    logActivity(dealId, "comment", "Deleted a comment");
  }, [logActivity]);

  // Attachment functions
  const addAttachment = useCallback((dealId: string, file: File) => {
    setUploading(true);
    
    // Simulate file upload
    setTimeout(() => {
      const attachment = {
        id: Date.now().toString(),
            name: file.name,
            size: file.size,
            type: file.type,
        url: URL.createObjectURL(file),
            uploadedAt: new Date().toISOString(),
      };
      
      setAttachments(prev => ({
        ...prev,
        [dealId]: [...(prev[dealId] || []), attachment]
      }));
      
      setUploading(false);
      logActivity(dealId, "attachment", `Uploaded ${file.name}`);
    }, 1000);
  }, [logActivity]);

  const deleteAttachment = useCallback((dealId: string, attachmentId: string) => {
    setAttachments(prev => ({
      ...prev,
      [dealId]: (prev[dealId] || []).filter(a => a.id !== attachmentId)
    }));
    logActivity(dealId, "attachment", "Deleted an attachment");
  }, [logActivity]);

  // Edit functions
  const handleEditChange = useCallback(<K extends keyof FrontendDeal>(key: K, value: FrontendDeal[K]) => {
    setEditForm(prev => ({ ...prev, [key]: value }));
  }, []);

  const saveEdit = useCallback(async () => {
    if (!editingDeal) return;
    
    setSavingEdit(true);
    try {
      // Prepare the update data
      const updateData: any = {};
      if (editForm.title) updateData.title = editForm.title;
      if (editForm.description !== undefined) updateData.description = editForm.description;
      if (editForm.value) updateData.value = editForm.value;
      if (editForm.reminderDate) updateData.reminder_date = editForm.reminderDate;
      
      // Call the API to update the deal
      await updateDeal(parseInt(editingDeal.id), updateData);
      
      // Update local state
      queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
        if (!oldData) return oldData;
        
        return {
          ...oldData,
          deals: oldData.deals.map(d => 
            d.id === parseInt(editingDeal.id) 
              ? { 
                  ...d, 
                  title: editForm.title || d.title,
                  description: editForm.description || d.description,
                  value: editForm.value ? parseFloat(editForm.value.replace(/[^\d.]/g, "")) : d.value,
                  reminder_date: editForm.reminderDate || d.reminder_date,
                }
              : d
          )
        };
      });
      
      logActivity(editingDeal.id, "edit", "Updated deal details");
      setEditingDeal(null);
      setEditForm({});
    } catch (error) {
      console.error('Failed to update deal:', error);
      // Revert optimistic update on error
      queryClient.invalidateQueries({ queryKey: ['kanban'] });
    } finally {
      setSavingEdit(false);
    }
  }, [editingDeal, editForm, queryClient, logActivity]);

  const confirmDeleteDeal = useCallback((deal: FrontendDeal) => {
    dealToDelete.current = deal;
    setShowDeleteConfirm(true);
  }, []);

  const deleteDeal = useCallback(() => {
    if (!dealToDelete.current) return;
    
    // Remove from local state
    queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
      if (!oldData) return oldData;
      
      return {
        ...oldData,
        deals: oldData.deals.filter(d => d.id !== parseInt(dealToDelete.current!.id))
      };
    });
    
    setShowDeleteConfirm(false);
    dealToDelete.current = null;
  }, [queryClient]);

  // Stage management functions
  // const handleAddStage = useCallback(() => {
  //   if (!newStage.trim()) return;
  //   
  //   // Add to local state
  //   queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
  //     if (!oldData) return oldData;
  //     
  //     const newStageData = {
  //       id: Date.now(),
  //       name: newStage.trim(),
  //       order: oldData.stages.length,
  //       is_active: true,
  //     };
  //     
  //     return {
  //       ...oldData,
  //       stages: [...oldData.stages, newStageData]
  //     };
  //   });
  //   
  //   setNewStage("");
  // }, [newStage, queryClient]);

  // const handleRenameStage = useCallback((oldName: string, newName: string) => {
  //   if (!newName.trim() || newName === oldName) {
  //     setEditingStage(null);
  //     return;
  //   }
  //   
  //   // Update local state
  //   queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
  //     if (!oldData) return oldData;
  //     
  //     return {
  //       ...oldData,
  //       stages: oldData.stages.map(s => 
  //         s.name === oldName ? { ...s, name: newName.trim() } : s
  //       )
  //     };
  //   });
  //   
  //   setEditingStage(null);
  // }, [queryClient]);

  const handleDeleteStage = useCallback((stageName: string) => {
    // Remove from local state
    queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
      if (!oldData) return oldData;
      
      return {
        ...oldData,
        stages: oldData.stages.filter(s => s.name !== stageName),
        deals: oldData.deals.filter(d => {
          const stage = oldData.stages.find(s => s.id === d.stage_id);
          return stage?.name !== stageName;
        })
      };
    });
    
    setDeleteStage(null);
  }, [queryClient]);

  // Handle drag and drop
  const onDragEnd = useCallback((result: DropResult) => {
    const { source, destination } = result;
    
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) {
      return;
    }
    
    // const sourceStageId = parseInt(source.droppableId);
    const destStageId = parseInt(destination.droppableId);
    const dealId = parseInt(result.draggableId);
    
    // Update local state optimistically
    queryClient.setQueryData<ApiKanbanBoard>(['kanban'], (oldData) => {
      if (!oldData) return oldData;
      
      const dealToMove = oldData.deals.find(d => d.id === dealId);
      if (!dealToMove) return oldData;
      
      const updatedDeals = oldData.deals.map(d => ({
        ...d,
        stage_id: d.id === dealId ? destStageId : d.stage_id,
      }));
      
      return {
        ...oldData,
        deals: updatedDeals,
      };
    });
    
    // Call API to update deal stage
    moveDeal(dealId, destStageId, destination.index)
      .then(() => {
        // Success - the optimistic update is already applied
        console.log(`Deal ${dealId} moved to stage ${destStageId}`);
      })
      .catch((error) => {
        console.error('Failed to move deal:', error);
        // Revert on error
        queryClient.invalidateQueries({ queryKey: ['kanban'] });
      });
  }, [queryClient]);

  // Compute filtered deals by stage
  const filteredDealsByStage: DealsByStage = useMemo(() => {
    return stages.reduce((acc, stage) => {
      let deals = dealsByStage[stage.id] || [];
      
      // Owner filter
      if (ownerFilter !== "All") {
        deals = deals.filter(d => d.owner === ownerFilter);
      }
      
      acc[stage.id] = deals;
      return acc;
    }, {} as DealsByStage);
  }, [dealsByStage, ownerFilter, stages]);

  // Compute analytics data
  const allDeals = Object.values(dealsByStage).flat();
  const stageCounts = stages.map(stage => ({ 
    stage: stage.name, 
    count: (dealsByStage[stage.id] || []).length 
  }));
  const avgDealSizeByStage = stages.map(stage => {
    const stageDeals = (dealsByStage[stage.id] || []);
    const avg = stageDeals.length ? stageDeals.reduce((sum, d) => sum + parseFloat(d.value.replace(/[^\d.]/g, "")), 0) / stageDeals.length : 0;
    return { stage: stage.name, avg: Math.round(avg) };
  });
  const funnelData = stages.map((stage, idx) => ({
    stage: stage.name,
    count: (dealsByStage[stage.id] || []).length,
    next: idx < stages.length - 1 ? (dealsByStage[stages[idx + 1].id] || []).length : 0,
  }));
  const pieColors = ["#6366f1", "#f59e42", "#10b981", "#f43f5e", "#a21caf", "#fbbf24", "#0ea5e9", "#eab308"];

  // Compute top owners/contributors analytics
  const dealsClosedByOwner = owners.map(owner => ({
    owner,
    count: allDeals.filter(d => d.owner === owner && d.stage === 'Won').length,
  })).sort((a, b) => b.count - a.count).slice(0, 10);
  
  const dealCountByOwner = owners.map(owner => ({
    owner,
    count: allDeals.filter(d => d.owner === owner).length,
  })).sort((a, b) => b.count - a.count).slice(0, 10);
  
  const dealValueByOwner = owners.map(owner => ({
    owner,
    value: allDeals.filter(d => d.owner === owner).reduce((sum, d) => sum + parseFloat(d.value.replace(/[^\d.]/g, "")), 0),
  })).sort((a, b) => b.value - a.value).slice(0, 10);

  // Helper component for loading state
  const LoadingState = () => (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );

  // Helper component for error state
  const ErrorState = ({ error, onRetry }: { error: any, onRetry: () => void }) => (
    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-400">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium">Error loading Kanban board</h3>
          <div className="mt-2 text-sm">
            <p>{error?.message || 'An error occurred'}</p>
          </div>
          <div className="mt-4">
            <button
              type="button"
              onClick={onRetry}
              className="rounded-md bg-red-50 dark:bg-red-900/30 px-2 py-1.5 text-sm font-medium text-red-800 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 focus:ring-offset-red-50 dark:focus:ring-offset-gray-800"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} onRetry={() => queryClient.invalidateQueries({ queryKey: ['kanban'] })} />;

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
        </div>
      
      {/* Metrics Cards Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Deals */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-full mb-3">
            <svg className="w-7 h-7 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
      </div>
          <div className="text-3xl font-extrabold text-blue-600 dark:text-blue-400 mb-1">{allDeals.length}</div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Total Deals</div>
          <div className="text-xs text-purple-500">Active pipeline</div>
        </div>
        {/* Deals in Progress */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-yellow-100 dark:bg-yellow-900 p-3 rounded-full mb-3">
            <svg className="w-7 h-7 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="text-3xl font-extrabold text-yellow-600 dark:text-yellow-400 mb-1">
            {allDeals.filter(d => d.stage !== 'Won' && d.stage !== 'Lost').length}
          </div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">In Progress</div>
          <div className="text-xs text-blue-500">Active negotiations</div>
        </div>
        {/* Total Value */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full mb-3">
            <svg className="w-7 h-7 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <div className="text-3xl font-extrabold text-green-600 dark:text-green-400 mb-1">
            ${allDeals.reduce((sum, d) => sum + parseFloat(d.value.replace(/[^\d.]/g, "")), 0).toLocaleString()}
          </div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Total Value</div>
          <div className="text-xs text-pink-500">Pipeline worth</div>
        </div>
        {/* Win Rate */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow p-6 flex flex-col items-center text-center border transition duration-300 ease hover:shadow-2xl hover:scale-105">
          <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-full mb-3">
            <svg className="w-7 h-7 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div className="text-3xl font-extrabold text-purple-600 dark:text-purple-400 mb-1">
            {allDeals.length > 0 ? Math.round((allDeals.filter(d => d.stage === 'Won').length / allDeals.length) * 100) : 0}%
          </div>
          <div className="text-gray-700 dark:text-gray-200 text-lg font-semibold mb-1">Win Rate</div>
          <div className="text-xs text-green-500">Success ratio</div>
        </div>
      </div>

      {/* Add 'Manage Stages' button above the Kanban board */}
      <div className="flex justify-end mb-2">
        <button
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-fuchsia-600 to-pink-500 text-white font-semibold shadow hover:from-fuchsia-700 hover:to-pink-600 transition"
          onClick={() => setIsManageStagesOpen(true)}
        >
          <Plus className="w-4 h-4" /> Manage Stages
        </button>
      </div>
      
      {/* Tabbed interface */}
      <div>
        <div className="flex gap-2 mb-6">
          <button
            className={`px-4 py-2 rounded-full font-semibold transition ${activeTab === 'board' ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
            onClick={() => setActiveTab('board')}
          >
            Board
          </button>
          <button
            className={`px-4 py-2 rounded-full font-semibold transition ${activeTab === 'analytics' ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
        </div>
        
        {activeTab === 'board' && (
          // Kanban Board with Drag-and-Drop
          <DragDropContext onDragEnd={onDragEnd}>
            <div className="flex gap-4 pb-4" style={{ overflowX: 'auto', scrollbarWidth: 'thin' }}>
              {stages.map((stage) => (
                <div key={stage.id} className="flex-shrink-0 w-72">
                  <div className={`flex-shrink-0 w-72 bg-gray-50 dark:bg-gray-900 rounded-2xl shadow border border-gray-200 dark:border-gray-800 p-4 flex flex-col transition`}>
                    <div className="font-bold text-lg mb-3 text-gray-700 dark:text-gray-200 flex items-center gap-2">
                      {/* Stage color tag */}
                      <span className={`inline-block w-3 h-3 rounded-full mr-2 ${stageColors[stage.name] || 'bg-gray-500'}`}></span>
                      {stage.name}
                      <span className="bg-pink-100 dark:bg-pink-900 text-pink-600 dark:text-pink-200 rounded-full px-2 py-0.5 text-xs font-semibold">
                        {filteredDealsByStage[stage.id]?.length || 0}
                      </span>
                    </div>
                    <Droppable droppableId={String(stage.id)} isDropDisabled={false}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className="flex-1 space-y-4 pr-1 min-h-0"
                        >
                          {filteredDealsByStage[stage.id]?.length === 0 && (
                            <div className="text-gray-400 dark:text-gray-600 text-sm text-center mt-8">No deals</div>
                          )}
                          {filteredDealsByStage[stage.id]?.map((deal, idx) => (
                            <Draggable draggableId={deal.id} index={idx} key={deal.id} isDragDisabled={false}>
                              {(dragProvided, dragSnapshot) => (
                                <div
                                  ref={dragProvided.innerRef}
                                  {...dragProvided.draggableProps}
                                  {...dragProvided.dragHandleProps}
                                  className={`rounded-xl bg-white dark:bg-gray-800 shadow p-4 border border-gray-100 dark:border-gray-800 hover:shadow-xl hover:scale-105 transition-all duration-300 cursor-pointer transform ${dragSnapshot.isDragging ? "ring-2 ring-blue-400 scale-105" : ""}`}
                                  onClick={() => setSelectedDeal(deal)}
                                >
                                  {/* Compact Deal Card Content */}
                                  <div className="flex items-start justify-between mb-2">
                                    <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                        <span className={`inline-block w-2 h-2 rounded-full ${stageColors[deal.stage] || 'bg-gray-500'}`}></span>
                                        <div className="font-semibold text-gray-900 dark:text-white text-sm truncate">{deal.title}</div>
                                        <span className="px-1.5 py-0.5 rounded-full text-xs font-bold bg-gradient-to-r from-green-400 to-blue-400 text-white" title="AI Score">
                                      {getDealScore(deal, activityLog[deal.id])}%
                                    </span>
                                  </div>
                                      <div className="text-blue-600 dark:text-blue-400 font-bold text-base">{deal.value}</div>
                                      <div className="text-xs text-gray-500 dark:text-gray-400">Owner: {deal.owner}</div>
                                    </div>
                                    {/* Watch button */}
                                    <button
                                      className={`ml-2 focus:outline-none rounded-full p-2 transition shadow ${Array.isArray(deal.watchers) && deal.watchers.includes(currentUser) ? "bg-pink-100 dark:bg-pink-900" : "bg-gray-100 dark:bg-gray-800"} hover:scale-110 hover:shadow-lg`}
                                      style={{ minWidth: 36, minHeight: 36, position: 'relative' }}
                                      onClick={async (e) => {
                                        e.stopPropagation();
                                        setWatchLoading(Number(deal.id));
                                        if (Array.isArray(deal.watchers) && deal.watchers.includes(currentUser)) {
                                          await unwatchDeal(Number(deal.id));
                                        } else {
                                          await watchDeal(Number(deal.id));
                                        }
                                        setWatchLoading(null);
                                        queryClient.invalidateQueries({ queryKey: ['kanban'] });
                                      }}
                                      title={Array.isArray(deal.watchers) && deal.watchers.length > 0 ? `Watchers: ${deal.watchers.join(', ')}` : "No watchers"}
                                      disabled={watchLoading === Number(deal.id)}
                                    >
                                      {watchLoading === Number(deal.id) ? (
                                        <span className="w-6 h-6 block animate-spin border-2 border-blue-400 border-t-transparent rounded-full mx-auto" />
                                      ) : (
                                        <span className="relative flex items-center">
                                          <Eye className={`w-6 h-6 ${Array.isArray(deal.watchers) && deal.watchers.includes(currentUser) ? "text-pink-500" : "text-gray-400"}`} />
                                          {Array.isArray(deal.watchers) && deal.watchers.length > 0 && (
                                            <span className="absolute -top-1 -right-2 bg-blue-500 text-white text-xs font-bold rounded-full px-1.5 py-0.5 shadow border border-white dark:border-gray-900">
                                              {deal.watchers.length}
                                            </span>
                                          )}
                                        </span>
                                      )}
                                    </button>
                                  </div>
                                  
                                  {/* Tags and Reminder - Compact */}
                                  <div className="flex items-center justify-between mb-2">
                                  {deal.tags && deal.tags.length > 0 && (
                                      <div className="flex gap-1">
                                        {deal.tags.slice(0, 2).map((tag: Tag) => (
                                          <span key={tag.label} className={`px-1.5 py-0.5 rounded-full text-xs font-semibold text-white ${tag.color}`}>{tag.label}</span>
                                        ))}
                                        {deal.tags.length > 2 && (
                                          <span className="px-1.5 py-0.5 rounded-full text-xs font-semibold bg-gray-500 text-white">+{deal.tags.length - 2}</span>
                                        )}
                                    </div>
                                  )}
                                  {deal.reminderDate && (
                                      <div className="flex items-center gap-1 text-xs">
                                        <Calendar className="w-3 h-3" />
                                        <span className={dayjs(deal.reminderDate).isBefore(dayjs(), "day") ? "text-red-500" : dayjs(deal.reminderDate).isSame(dayjs(), "day") ? "text-yellow-500" : "text-blue-500"}>
                                          {dayjs(deal.reminderDate).format("MMM D")}
                                        </span>
                                    </div>
                                  )}
                                  </div>
                                  
                                  {/* Actions and Watchers - Compact */}
                                  <div className="flex items-center justify-between">
                                    <div className="flex gap-2">
                                      <button 
                                        className="px-3 py-1 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition-all duration-300 hover:scale-110 hover:shadow-lg transform" 
                                        onClick={e => {e.stopPropagation(); setSelectedDeal(deal); setIsDealModalOpen(true);}}
                                        title="View Details"
                                      >
                                        View
                                      </button>
                                      <button 
                                        className="px-3 py-1 rounded-full bg-gradient-to-r from-yellow-400 to-pink-500 text-white text-xs font-semibold shadow hover:from-yellow-500 hover:to-pink-600 transition-all duration-300 hover:scale-110 hover:shadow-lg transform" 
                                        onClick={e => {e.stopPropagation(); setEditingDeal(deal);}}
                                        title="Edit Deal"
                                      >
                                        Edit
                                      </button>
                                    </div>
                                    <div className="flex items-center gap-1">
                                    {Array.isArray(deal.watchers) && deal.watchers.length > 0 && (
                                        <div className="flex -space-x-1">
                                          {deal.watchers.slice(0, 3).map((w: string) => (
                                            <span key={w} className="w-5 h-5 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-xs font-bold text-white border border-white dark:border-gray-900">
                                            {getInitials(w)}
                                          </span>
                                        ))}
                                          {deal.watchers.length > 3 && (
                                            <span className="w-5 h-5 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-xs font-bold text-gray-600 dark:text-gray-300 border border-white dark:border-gray-900">
                                              +{deal.watchers.length - 3}
                                            </span>
                                          )}
                                      </div>
                                    )}
                                  </div>
                                  </div>
                                  
                                  {/* Next Step - Compact */}
                                  <div className="text-xs text-pink-600 dark:text-pink-300 mt-1 font-medium">
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
        
        {activeTab === 'analytics' && (
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
                 <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Top 10 Owners (Deals Closed)</div>
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
                 <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Top 10 Deal Count by Owner</div>
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
                 <div className="font-bold text-lg mb-4 text-gray-900 dark:text-white">Top 10 Deal Value by Owner</div>
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
              </div>
          </>
        )}
              </div>

      {/* Deal Detail Modal */}
      <AnimatedModal
        open={isDealModalOpen}
        onClose={() => setIsDealModalOpen(false)}
        title={selectedDeal ? `Deal: ${selectedDeal.title}` : 'Deal Details'}
        animationType="slideUp"
        size="lg"
      >
        {selectedDeal && (
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Title</h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedDeal.title}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Value</h3>
                <p className="text-blue-600 dark:text-blue-400 font-bold">{selectedDeal.value}</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Owner</h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedDeal.owner}</p>
            </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Stage</h3>
                <p className="text-gray-600 dark:text-gray-300">{selectedDeal.stage}</p>
                </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">AI Score</h3>
                <p className="text-gray-600 dark:text-gray-300">{getDealScore(selectedDeal, activityLog[selectedDeal.id])}%</p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Next Step</h3>
                <p className="text-gray-600 dark:text-gray-300">{getNextStepSuggestion(selectedDeal)}</p>
              </div>
            </div>
            
            {selectedDeal.description && (
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-2">Description</h3>
                <p className="text-gray-600 dark:text-gray-300 text-sm">{selectedDeal.description}</p>
      </div>
            )}

            {/* Tags */}
            {selectedDeal.tags && selectedDeal.tags.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-2">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedDeal.tags.map((tag: Tag) => (
                    <span key={tag.label} className={`px-2 py-1 rounded-full text-xs font-semibold text-white ${tag.color}`}>
                      {tag.label}
                    </span>
                  ))}
                </div>
                    </div>
                  )}

                  {/* Comments Section */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-2">Comments</h3>
              <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
                {(comments[selectedDeal.id] || []).length === 0 && (
                  <div className="text-gray-400">No comments yet.</div>
                )}
                {(comments[selectedDeal.id] || []).map(comment => (
                  <div key={comment.id} className="flex items-start gap-2 bg-gray-50 dark:bg-gray-800 rounded p-2">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold text-white shadow ${userAvatars[comment.author]?.color || "bg-gray-400"}`}>
                      {getInitials(comment.author)}
                    </span>
                          <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-blue-600 dark:text-blue-400">[{comment.author}]</span>
                              <span className="text-gray-400">{dayjs(comment.timestamp).fromNow()}</span>
                            </div>
                      <p className="text-gray-900 dark:text-gray-100 mt-1">{comment.text}</p>
                          </div>
                          <button
                      className="text-xs text-gray-400 hover:text-red-500 transition"
                            title="Delete"
                      onClick={() => deleteComment(selectedDeal.id, comment.id)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                    <form
                className="flex gap-2 mt-2 items-center"
                onSubmit={e => { e.preventDefault(); addComment(selectedDeal.id); }}
                    >
                      <input
                        type="text"
                  className="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="Add a comment..."
                        value={newComment}
                        onChange={e => setNewComment(e.target.value)}
                      />
                      <button
                        type="submit"
                  className="px-3 py-1 rounded bg-blue-500 text-white text-xs font-semibold hover:bg-blue-600 transition"
                        disabled={!newComment.trim()}
                      >
                  Add
                      </button>
                    </form>
                  </div>

                  {/* Attachments Section */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-2">Attachments</h3>
              <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
                {(attachments[selectedDeal.id] || []).length === 0 && (
                  <div className="text-gray-400">No attachments yet.</div>
                )}
                {(attachments[selectedDeal.id] || []).map(att => (
                  <div key={att.id} className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded px-3 py-2">
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
                      className="ml-2 text-xs text-gray-400 hover:text-red-500 transition"
                            title="Delete"
                      onClick={() => deleteAttachment(selectedDeal.id, att.id)}
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
                <label className="px-3 py-1 rounded bg-blue-500 text-white text-xs font-semibold hover:bg-blue-600 transition cursor-pointer">
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
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-2">Activity Log</h3>
                    <div className="space-y-2 max-h-32 overflow-y-auto text-xs">
                {(activityLog[selectedDeal.id] || []).length === 0 && (
                        <div className="text-gray-400">No activity yet.</div>
                      )}
                {(activityLog[selectedDeal.id] || []).map(log => (
                        <div key={log.id} className="flex items-center gap-2">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold text-white shadow ${userAvatars[log.user]?.color || "bg-gray-400"}`}>
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
                  </div>
        )}
      </AnimatedModal>

      {/* Edit Deal Modal */}
      <AnimatedModal
        open={!!editingDeal}
        onClose={() => setEditingDeal(null)}
        title={editingDeal ? `Edit Deal: ${editingDeal.title}` : 'Edit Deal'}
        animationType="scale"
        size="md"
      >
        {editingDeal && (
                  <form onSubmit={e => { e.preventDefault(); saveEdit(); }}>
            <div className="space-y-4">
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Title</label>
                <input
                  type="text"
                  value={editForm.title || editingDeal.title}
                  onChange={e => handleEditChange("title", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  required
                />
                    </div>
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Value</label>
                <input
                  type="text"
                  value={editForm.value || editingDeal.value}
                  onChange={e => handleEditChange("value", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  required
                />
                    </div>
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Owner</label>
                      <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  value={editForm.owner || editingDeal.owner}
                  onChange={e => handleEditChange("owner", e.target.value)}
                        required
                      >
                        {owners.map((owner) => (
                          <option key={owner} value={owner}>{owner}</option>
                        ))}
                      </select>
                    </div>
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Stage</label>
                      <select
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  value={editForm.stage || editingDeal.stage}
                  onChange={e => handleEditChange("stage", e.target.value)}
                        required
                      >
                        {stages.map((stage) => (
                    <option key={stage.id} value={stage.name}>{stage.name}</option>
                        ))}
                      </select>
                    </div>
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Tags</label>
                      <div className="flex flex-wrap gap-2">
                        {predefinedTags.map(tag => {
                    const selected = (editForm.tags || editingDeal.tags || []).some((t: Tag) => t.label === tag.label);
                          return (
                            <button
                              key={tag.label}
                              type="button"
                              className={`px-2 py-1 rounded-full text-xs font-semibold border transition ${tag.color} text-white ${selected ? "ring-2 ring-pink-400" : "opacity-70"}`}
                              onClick={() => {
                          let tags = editForm.tags ? [...editForm.tags] : [...(editingDeal.tags || [])];
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
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Description</label>
                <textarea
                  value={editForm.description || editingDeal.description || ""}
                  onChange={e => handleEditChange("description", e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
                    </div>
              <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Reminder / Follow-up Date</label>
                      <input
                        type="date"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  value={editForm.reminderDate ? dayjs(editForm.reminderDate).format("YYYY-MM-DD") : editingDeal.reminderDate ? dayjs(editingDeal.reminderDate).format("YYYY-MM-DD") : ""}
                        onChange={e => handleEditChange("reminderDate", e.target.value ? dayjs(e.target.value).toISOString() : undefined)}
                      />
                    </div>
              <div className="flex gap-2 pt-4">
                <button
                  type="submit"
                  disabled={savingEdit}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-all duration-300 hover:scale-105 hover:shadow-lg transform disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {savingEdit ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditingDeal(null);
                    setEditForm({});
                  }}
                  className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 transition-all duration-300 hover:scale-105 hover:shadow-lg transform"
                >
                  Cancel
                </button>
              </div>
                    </div>
                  </form>
        )}
                  {editingDeal && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      type="button"
              className="w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                      onClick={() => confirmDeleteDeal(editingDeal)}
                    >
                      Delete Deal
                    </button>
            </div>
        )}
      </AnimatedModal>

      {/* Delete confirmation dialog */}
      <AnimatedModal
        open={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        title="Delete Deal"
        animationType="slideDown"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-200">
            Are you sure you want to delete this deal? This action cannot be undone.
          </p>
          <div className="flex gap-2 pt-4">
                    <button
                      onClick={deleteDeal}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                    >
                      Delete
                    </button>
                            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 transition"
                            >
              Cancel
                            </button>
                      </div>
                  </div>
      </AnimatedModal>

      {/* Delete Stage Confirmation Dialog */}
      <AnimatedModal
        open={!!deleteStage}
        onClose={() => setDeleteStage(null)}
        title="Delete Stage"
        animationType="fade"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-200">
            Are you sure you want to delete the stage "{deleteStage}"? All deals in this stage will be removed. This action cannot be undone.
          </p>
          <div className="flex gap-2 pt-4">
                    <button
              onClick={() => deleteStage && handleDeleteStage(deleteStage)}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
                    >
              Delete
                    </button>
                    <button
                      onClick={() => setDeleteStage(null)}
              className="flex-1 px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 transition"
                    >
                      Cancel
                    </button>
                  </div>
            </div>
      </AnimatedModal>

      {/* Stage Management Modal */}
      <StageManagementModal
        isOpen={isManageStagesOpen}
        onClose={() => setIsManageStagesOpen(false)}
        onStagesUpdated={() => {
          // Refresh the kanban data when stages are updated
          queryClient.invalidateQueries({ queryKey: ['kanban-board'] });
        }}
      />
    </div>
  );
} 