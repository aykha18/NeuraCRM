/**
 * Leads page: Stunning table with search, filters, actions, detail modal, sorting, pagination, bulk actions, and inline editing
 * - Modern, responsive design matching dashboard
 * - Column sorting, pagination, bulk actions, row highlight, inline editing
 */
import { useEffect, useState } from "react";
import { Search, Filter, Eye, Trash2, X, ChevronUp, ChevronDown, Download, Plus, Zap, BarChart3, TrendingUp, ArrowRight } from "lucide-react";
import * as XLSX from "xlsx";
import { fetchLeads, getLead, createLead, updateLead, deleteLead, convertLeadToDeal } from "../services/leads";
import { scoreAllLeads, getScoringAnalytics } from "../services/leadScoring";
import DetailModal from "../components/DetailModal";
import LeadScore from "../components/LeadScore";
import AnimatedModal from "../components/AnimatedModal";

const statusColors: Record<string, string> = {
  New: "bg-blue-100 text-blue-700",
  Contacted: "bg-yellow-100 text-yellow-700",
  Qualified: "bg-green-100 text-green-700",
  Lost: "bg-red-100 text-red-700",
  // Handle lowercase statuses from database
  new: "bg-blue-100 text-blue-700",
  contacted: "bg-yellow-100 text-yellow-700",
  qualified: "bg-green-100 text-green-700",
  lost: "bg-red-100 text-red-700",
  converted: "bg-purple-100 text-purple-700",
};

const statusBadgeColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  qualified: 'bg-green-100 text-green-700',
  lost: 'bg-red-100 text-red-700',
  converted: 'bg-purple-100 text-purple-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  proposal: 'bg-pink-100 text-pink-700',
  negotiation: 'bg-orange-100 text-orange-700',
  won: 'bg-green-200 text-green-800',
};

const columns = [
  { key: "title", label: "Name", sortable: true },
  { key: "company", label: "Company", sortable: true },
  { key: "status", label: "Status", sortable: true },
  { key: "score", label: "Score", sortable: true },
  { key: "owner_name", label: "Owner", sortable: true },
  { key: "created_at", label: "Created", sortable: true },
];


// const ownerOptions = ["Alex", "Sam", "Chris"];

export default function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [scoreFilter, setScoreFilter] = useState("");
  const [detailLead, setDetailLead] = useState<any | null>(null);
  const [editingCell, setEditingCell] = useState<{ id: number; field: string } | null>(null);
  const [editCellValue, setEditCellValue] = useState("");
  const [sortBy, setSortBy] = useState<string>("created");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number[]>([]);
  // const [leadsData, setLeadsData] = useState(leads); // This state is no longer needed for static data
  // const [editing, setEditing] = useState<{ id: number; field: string } | null>(null);
  // const [editValue, setEditValue] = useState("");
  const pageSize = 10;
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newLead, setNewLead] = useState({
    title: "",
    status: "new",
    source: "manual",
    contact_id: null,
    owner_id: 1
  });
  const [scoringAnalytics, setScoringAnalytics] = useState<any>(null);
  const [showScoringModal, setShowScoringModal] = useState(false);
  const [scoringLoading, setScoringLoading] = useState(false);
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    fetchLeads()
      .then(data => {
        // loaded
        setLeads(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load leads:', err);
        setError("Failed to load leads");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-lg">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  // Filtered and sorted leads
  let leadsToDisplay = leads.filter(
    (lead) => {
      // Search filter
      const searchMatch = !search || 
        lead.title?.toLowerCase().includes(search.toLowerCase()) || 
        lead.company?.toLowerCase().includes(search.toLowerCase());
      
      // Status filter
      const statusMatch = !statusFilter || 
        (lead.status && (
          lead.status.toLowerCase() === statusFilter.toLowerCase() ||
          lead.status === statusFilter
        ));
      
      // statusFilter diagnostics removed
      

      
      // Score filter
      let scoreMatch = true;
      if (scoreFilter) {
        const score = lead.score ?? 0;
        switch (scoreFilter) {
          case "hot":
            scoreMatch = score >= 80;
            break;
          case "warm":
            scoreMatch = score >= 60 && score < 80;
            break;
          case "lukewarm":
            scoreMatch = score >= 40 && score < 60;
            break;
          case "cold":
            scoreMatch = score < 40;
            break;
          case "scored":
            scoreMatch = score > 0;
            break;
          case "unscored":
            scoreMatch = score === 0 || score === null;
            break;
        }
      }
      
      return searchMatch && statusMatch && scoreMatch;
    }
  );
  
  // Enhanced sorting logic
  leadsToDisplay = leadsToDisplay.sort((a, b) => {
    let aValue = (a as any)[sortBy];
    let bValue = (b as any)[sortBy];
    
    // Handle null/undefined values for score
    if (sortBy === "score") {
      aValue = aValue ?? 0;
      bValue = bValue ?? 0;
    }
    
    // Handle date sorting
    if (sortBy === "created_at") {
      aValue = new Date(aValue || 0);
      bValue = new Date(bValue || 0);
    }
    
    // Handle string sorting
    if (typeof aValue === "string" && typeof bValue === "string") {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }
    
    if (aValue < bValue) return sortDir === "asc" ? -1 : 1;
    if (aValue > bValue) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(leadsToDisplay.length / pageSize);
  const pagedLeads = leadsToDisplay.slice((page - 1) * pageSize, page * pageSize);

  // filtering summary removed

  // Handle column sort
  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortDir("asc");
    }
    setPage(1);
  };

  // Bulk selection logic
  const allSelected = pagedLeads.length > 0 && pagedLeads.every((lead) => selected.includes(lead.id));
  const someSelected = pagedLeads.some((lead) => selected.includes(lead.id));
  const toggleAll = () => {
    if (allSelected) {
      setSelected(selected.filter(id => !pagedLeads.some(l => l.id === id)));
    } else {
      setSelected([...selected, ...pagedLeads.filter(l => !selected.includes(l.id)).map(l => l.id)]);
    }
  };
  const toggleOne = (id: number) => {
    setSelected(selected.includes(id) ? selected.filter(i => i !== id) : [...selected, id]);
  };
  const clearSelected = () => setSelected([]);
  const deleteSelected = () => {
    // In a real app, you'd update the backend and state
    alert(`Deleted ${selected.length} leads (demo only)`);
    clearSelected();
  };

  // Inline editing logic
  // const startEdit = (id: number, field: string, value: string) => {
  //   setEditing({ id, field });
  //   setEditValue(value);
  // };
  // const saveEdit = (id: number, field: string) => {
  //   setLeads((prev) =>
  //     prev.map((lead) =>
  //       lead.id === id ? { ...lead, [field]: editValue } : lead
  //     )
  //   );
  //   setEditing(null);
  //   setEditValue("");
  // };
  // const handleEditKey = (e: React.KeyboardEvent, id: number, field: string) => {
  //   if (e.key === "Enter") {
  //     saveEdit(id, field);
  //   } else if (e.key === "Escape") {
  //     setEditing(null);
  //     setEditValue("");
  //   }
  // };

  // Inline edit handlers
  const startEditCell = (id: number, field: string, value: string) => {
    setEditingCell({ id, field });
    setEditCellValue(value);
  };
  const saveEditCell = async (id: number, field: string) => {
    setActionLoading(true);
    try {
      await updateLead(id, { [field]: editCellValue });
      setLeads(prev =>
        prev.map(lead =>
          lead.id === id ? { ...lead, [field]: editCellValue } : lead
        )
      );
      setToast("Lead updated!");
      setTimeout(() => setToast(null), 2000);
    } catch (e) {
      alert("Failed to update lead");
    }
    setEditingCell(null);
    setEditCellValue("");
    setActionLoading(false);
  };
  const handleEditCellKey = (e: React.KeyboardEvent, id: number, field: string) => {
    if (e.key === "Enter") saveEditCell(id, field);
    if (e.key === "Escape") setEditingCell(null);
  };

  // CSV Export
  function exportCSV() {
    const headers = ["Name", "Company", "Status", "Owner", "Created"];
    const rows = leadsToDisplay.map(lead => [
      lead.name,
      lead.company,
      lead.status,
      lead.owner,
      lead.created,
    ]);
    const csvContent =
      [headers, ...rows]
        .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(","))
        .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "leads.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  // Excel Export
  function exportExcel() {
    const headers = ["Name", "Company", "Status", "Owner", "Created"];
    const rows = leadsToDisplay.map(lead => [
      lead.name,
      lead.company,
      lead.status,
      lead.owner,
      lead.created,
    ]);
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Leads");
    XLSX.writeFile(wb, "leads.xlsx");
  }

  // Action handlers
  const handleView = async (id: number) => {
    setActionLoading(true);
    try {
      const lead = await getLead(id);
      setDetailLead(lead);
    } catch (e) {
      alert("Failed to fetch lead details");
    }
    setActionLoading(false);
  };

  // const handleEdit = async (id: number) => {
  //   const newTitle = prompt("Enter new title for the lead:");
  //   if (!newTitle) return;
  //   setActionLoading(true);
  //   try {
  //     await updateLead(id, { title: newTitle });
  //     // Refresh leads
  //     fetchLeads().then(setLeads);
  //   } catch (e) {
  //     alert("Failed to update lead");
  //   }
  //   setActionLoading(false);
  // };

  const handleDelete = async (id: number) => {
    setConfirmDeleteId(id);
  };

  const confirmDelete = async () => {
    if (confirmDeleteId === null) return;
    setActionLoading(true);
    try {
      await deleteLead(confirmDeleteId);
      fetchLeads().then(setLeads);
      setToast("Lead deleted!");
      setTimeout(() => setToast(null), 2000);
    } catch (e) {
      alert("Failed to delete lead");
    }
    setActionLoading(false);
    setConfirmDeleteId(null);
  };

  const cancelDelete = () => setConfirmDeleteId(null);

  // Convert lead to deal handler
  const handleConvertToDeal = async (id: number) => {
    setActionLoading(true);
    try {
      const result = await convertLeadToDeal(id);
      setLeads(await fetchLeads()); // Refresh the list
      setToast(`Lead converted to deal: ${result.message}`);
      setTimeout(() => setToast(null), 3000);
    } catch (e) {
      alert("Failed to convert lead to deal");
    }
    setActionLoading(false);
  };

  // Create lead handlers
  const handleCreateLead = async () => {
    if (!newLead.title.trim()) {
      alert("Please enter a lead title");
      return;
    }
    
    setActionLoading(true);
    try {
      await createLead(newLead);
      setLeads(await fetchLeads()); // Refresh the list
      setShowCreateModal(false);
      setNewLead({ title: "", status: "new", source: "manual", contact_id: null, owner_id: 1 });
      setToast("Lead created successfully!");
      setTimeout(() => setToast(null), 2000);
    } catch (e) {
      alert("Failed to create lead");
    }
    setActionLoading(false);
  };

  const resetCreateForm = () => {
    setNewLead({ title: "", status: "new", source: "manual", contact_id: null, owner_id: 1 });
  };

  // Lead scoring functions
  const handleScoreAllLeads = async () => {
    setScoringLoading(true);
    try {
      const result = await scoreAllLeads();
      setLeads(await fetchLeads()); // Refresh leads with new scores
      setToast(`Successfully scored ${result.results.length} leads!`);
      setTimeout(() => setToast(null), 3000);
    } catch (error) {
      setToast("Failed to score leads");
      setTimeout(() => setToast(null), 3000);
    }
    setScoringLoading(false);
  };

  const handleViewScoringAnalytics = async () => {
    setScoringLoading(true);
    try {
      const analytics = await getScoringAnalytics();
      setScoringAnalytics(analytics);
      setShowScoringModal(true);
    } catch (error) {
      setToast("Failed to load scoring analytics");
      setTimeout(() => setToast(null), 3000);
    }
    setScoringLoading(false);
  };

  // Get unique status values from leads data
  const getUniqueStatuses = () => {
    if (!leads || leads.length === 0) {
      return ["new", "qualified", "lost", "converted", "contacted"];
    }
    const statuses = [...new Set(leads.map(lead => lead.status).filter(Boolean))];
    // available statuses
    return statuses.length > 0 ? statuses : ["new", "qualified", "lost", "converted", "contacted"];
  };

  return (
    <div className="p-2 md:p-6">
      {/* Bulk Action Bar */}
      {selected.length > 0 && (
        <div className="flex items-center justify-between bg-pink-50 dark:bg-pink-900/30 border border-pink-200 dark:border-pink-800 rounded-xl px-4 py-2 mb-4 shadow animate-fade-in">
          <span className="text-pink-700 dark:text-pink-200 font-semibold">{selected.length} selected</span>
          <div className="flex gap-2">
            <button
              className="px-4 py-1 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition"
              onClick={deleteSelected}
            >
              Delete Selected
            </button>
            <button
              className="px-4 py-1 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition"
              onClick={clearSelected}
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Header and actions */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">Leads</h1>
        
        {/* Action Buttons Group */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          
          {/* Primary Actions - Left Group */}
          <div className="flex flex-wrap gap-3">
            {/* Create Lead Button */}
            <button
              className="px-6 py-3 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 text-white font-semibold shadow-lg hover:from-pink-600 hover:to-purple-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={(e) => { setAnchorRect((e.currentTarget as HTMLButtonElement).getBoundingClientRect()); setShowCreateModal(true); }}
            >
              <Plus className="w-5 h-5" />
              Create Lead
            </button>
            
            {/* Score All Leads Button */}
            <button
              className="px-6 py-3 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold shadow-lg hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={handleScoreAllLeads}
              disabled={scoringLoading}
            >
              <Zap className="w-5 h-5" />
              {scoringLoading ? "Scoring..." : "Score All Leads"}
            </button>
            
            {/* Analytics Button */}
            <button
              className="px-6 py-3 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold shadow-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={handleViewScoringAnalytics}
              disabled={scoringLoading}
            >
              <BarChart3 className="w-5 h-5" />
              Analytics
            </button>
          </div>
          
          {/* Secondary Actions - Right Group */}
          <div className="flex flex-wrap gap-3">
            {/* Sort by Score Button */}
            <button
              className="px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-semibold shadow hover:from-purple-600 hover:to-indigo-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={() => {
                setSortBy("score");
                setSortDir("desc");
                setPage(1);
              }}
            >
              <TrendingUp className="w-4 h-4" />
              Sort by Score
            </button>
            
            {/* Export Buttons */}
            <button
              className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={exportCSV}
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
            <button
              className="px-4 py-2 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-white font-semibold shadow hover:from-green-600 hover:to-teal-600 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={exportExcel}
            >
              <Download className="w-4 h-4" />
              Export Excel
            </button>
          </div>
        </div>
      </div>
      
      {/* Search and Filters Row */}
      <div className="flex flex-col lg:flex-row gap-4 mb-6">
        {/* Search and Filters - Left Side */}
        <div className="flex flex-col sm:flex-row gap-3 flex-1">
          {/* Search bar */}
          <div className="relative flex-1 max-w-md">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search leads..."
              className="w-full rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 shadow"
            />
            <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          </div>
          
          {/* Status filter */}
          <div className="relative">
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 w-40 shadow appearance-none"
            >
              <option value="">All Statuses</option>
              {getUniqueStatuses().map(status => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
            <Filter className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          </div>
          
          {/* Score filter */}
          <div className="relative">
            <select
              value={scoreFilter}
              onChange={e => setScoreFilter(e.target.value)}
              className="rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-pink-400 w-40 shadow appearance-none"
            >
              <option value="">All Scores</option>
              <option value="hot">Hot Leads (80+)</option>
              <option value="warm">Warm Leads (60-79)</option>
              <option value="lukewarm">Lukewarm (40-59)</option>
              <option value="cold">Cold Leads (0-39)</option>
              <option value="scored">Scored Leads</option>
              <option value="unscored">Unscored Leads</option>
            </select>
            <Filter className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          </div>
        </div>
        
        {/* Clear Filters - Right Side */}
        {(search || statusFilter || scoreFilter) && (
          <div className="flex justify-end">
            <button
              className="px-4 py-2 rounded-full bg-gradient-to-r from-gray-500 to-gray-600 text-white font-semibold shadow hover:from-gray-600 hover:to-gray-700 transition-all duration-200 flex items-center gap-2 hover:scale-105"
              onClick={() => {
                setSearch("");
                setStatusFilter("");
                setScoreFilter("");
                setSortBy("created_at");
                setSortDir("desc");
                setPage(1);
              }}
            >
              <X className="w-4 h-4" />
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Filter Summary */}
      {(search || statusFilter || scoreFilter || sortBy !== "created_at") && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="font-semibold text-blue-700 dark:text-blue-300">Active Filters:</span>
            {search && (
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 rounded-full">
                Search: "{search}"
              </span>
            )}
            {statusFilter && (
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 rounded-full">
                Status: {statusFilter}
              </span>
            )}
            {scoreFilter && (
              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 rounded-full">
                Score: {scoreFilter}
              </span>
            )}
            <span className="px-2 py-1 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-300 rounded-full">
                Sort: {columns.find(col => col.key === sortBy)?.label} ({sortDir.toUpperCase()})
            </span>
            <span className="text-gray-500 dark:text-gray-400">
              Showing {leadsToDisplay.length} of {leads.length} leads
            </span>
          </div>
        </div>
      )}

      {/* Responsive Table: hidden on mobile */}
      <div className="overflow-x-auto rounded-2xl shadow border bg-white dark:bg-gray-900 hidden sm:block">
        <table className="min-w-full bg-white dark:bg-gray-900 rounded shadow overflow-hidden">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-700">
              <th className="px-4 py-2">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={el => { if (el) el.indeterminate = someSelected && !allSelected; }}
                  onChange={toggleAll}
                  aria-label="Select all leads on this page"
                  className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                />
              </th>
              {columns.map((column) => (
                <th 
                  key={column.key}
                  className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center gap-1">
                    {column.label}
                    {column.sortable && (
                      <div className="flex flex-col">
                        <ChevronUp 
                          className={`w-3 h-3 ${
                            sortBy === column.key && sortDir === "asc" 
                              ? "text-pink-500" 
                              : "text-gray-400"
                          }`} 
                        />
                        <ChevronDown 
                          className={`w-3 h-3 ${
                            sortBy === column.key && sortDir === "desc" 
                              ? "text-pink-500" 
                              : "text-gray-400"
                          }`} 
                        />
                      </div>
                    )}
                  </div>
                </th>
              ))}
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Actions</th>
            </tr>
          </thead>
          <tbody>
            {pagedLeads.map(lead => (
              <tr
                key={lead.id}
                className="border-b border-gray-200 dark:border-gray-700 hover:bg-pink-50 dark:hover:bg-pink-900/20 transition cursor-pointer"
              >
                <td className="px-4 py-2">
                  <input
                    type="checkbox"
                    checked={selected.includes(lead.id)}
                    onChange={() => toggleOne(lead.id)}
                    aria-label={`Select lead ${lead.title || lead.contact_name}`}
                    className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                  />
                </td>
                <td className="px-4 py-2 text-gray-900 dark:text-white">
                  {editingCell && editingCell.id === lead.id && editingCell.field === "title" ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={e => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(lead.id, "title")}
                      onKeyDown={e => handleEditCellKey(e, lead.id, "title")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEditCell(lead.id, "title", lead.title)}
                    >
                      {lead.title || lead.contact_name}
                    </span>
                  )}
                </td>
                <td className="px-4 py-2 text-gray-700 dark:text-gray-300">{lead.company}</td>
                <td className="px-4 py-2">
                  {editingCell && editingCell.id === lead.id && editingCell.field === "status" ? (
                    <select
                      autoFocus
                      value={editCellValue}
                      onChange={e => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(lead.id, "status")}
                      onKeyDown={e => handleEditCellKey(e, lead.id, "status")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      {Object.keys(statusBadgeColors).map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <span
                      className={`cursor-pointer hover:underline px-3 py-1 rounded-full text-xs font-bold capitalize ${statusBadgeColors[lead.status?.toLowerCase()] || 'bg-gray-200 text-gray-700'}`}
                      onClick={() => startEditCell(lead.id, "status", lead.status)}
                    >
                      {lead.status ? lead.status.charAt(0).toUpperCase() + lead.status.slice(1) : 'Unknown'}
                    </span>
                  )}
                </td>
                <td className="px-4 py-2">
                  <LeadScore score={lead.score} size="sm" />
                </td>
                <td className="px-4 py-2 text-gray-700 dark:text-gray-300">{lead.owner_name}</td>
                <td className="px-4 py-2 text-gray-500 dark:text-gray-400">{lead.created_at?.slice(0, 10)}</td>
                <td className="px-4 py-2 flex gap-2">
                  <button
                    className="text-blue-500 hover:text-blue-700"
                    title="View"
                    onClick={() => handleView(lead.id).then(() => setDetailLead(lead))}
                    disabled={actionLoading}
                  >
                    <Eye />
                  </button>
                  {lead.status !== "converted" && (
                    <button
                      className="text-green-500 hover:text-green-700"
                      title="Convert to Deal"
                      onClick={() => handleConvertToDeal(lead.id)}
                      disabled={actionLoading}
                    >
                      <ArrowRight />
                    </button>
                  )}
                  <button
                    className="text-red-500 hover:text-red-700"
                    title="Delete"
                    onClick={() => handleDelete(lead.id)}
                    disabled={actionLoading}
                  >
                    <Trash2 />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Responsive Card View: only on mobile */}
      <div className="sm:hidden space-y-4">
        {/* Mobile Create Button */}
        <button
          className="w-full px-4 py-3 rounded-2xl bg-gradient-to-r from-pink-500 to-purple-500 text-white font-semibold shadow hover:from-pink-600 hover:to-purple-600 transition flex items-center justify-center gap-2"
          onClick={(e) => { setAnchorRect((e.currentTarget as HTMLButtonElement).getBoundingClientRect()); setShowCreateModal(true); }}
        >
          <Plus className="w-5 h-5" />
          Create New Lead
        </button>
        
        {pagedLeads.map((lead) => (
          <div
            key={lead.id}
            className={`rounded-2xl shadow border p-4 bg-white dark:bg-gray-900 transition ${selected.includes(lead.id) ? "bg-pink-100 dark:bg-pink-900/40 border-pink-300 dark:border-pink-800" : "hover:bg-pink-50 dark:hover:bg-pink-900/20"}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.includes(lead.id)}
                  onChange={() => toggleOne(lead.id)}
                  className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                />
                <span className="font-bold text-lg text-gray-900 dark:text-white">{lead.name}</span>
              </div>
              <div className="flex gap-2">
                <button
                  className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition"
                  title="View"
                  onClick={() => setDetailLead(lead)}
                >
                  <Eye className="w-5 h-5 text-blue-500" />
                </button>
                {lead.status !== "converted" && (
                  <button
                    className="p-2 rounded-full hover:bg-green-100 dark:hover:bg-green-900 transition"
                    title="Convert to Deal"
                    onClick={() => handleConvertToDeal(lead.id)}
                    disabled={actionLoading}
                  >
                    <ArrowRight className="w-5 h-5 text-green-500" />
                  </button>
                )}
                <button
                  className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5 text-red-500" />
                </button>
              </div>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Company:</span> {lead.company}</div>
            <div className="flex items-center justify-between mb-1">
              <div className="text-sm">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[lead.status]}`}>
                  {lead.status ? lead.status.charAt(0).toUpperCase() + lead.status.slice(1) : 'Unknown'}
                </span>
              </div>
              <LeadScore score={lead.score} size="sm" />
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Owner:</span> {lead.owner_name}</div>
            <div className="text-gray-500 dark:text-gray-400 text-xs"><span className="font-semibold">Created:</span> {lead.created_at?.slice(0, 10)}</div>
          </div>
        ))}
        {pagedLeads.length === 0 && (
          <div className="text-center py-8 text-gray-400 dark:text-gray-600">No leads found.</div>
        )}
      </div>

      {/* Pagination Controls */}
      <div className="flex justify-end items-center gap-2 mt-4">
        <button
          className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-300 font-semibold disabled:opacity-50"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Prev
        </button>
        <span className="text-gray-700 dark:text-gray-200 text-sm">
          Page {page} of {totalPages}
        </span>
        <button
          className="px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-300 font-semibold disabled:opacity-50"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages}
        >
          Next
        </button>
      </div>

      {/* Detail Modal Skeleton */}
      {detailLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 w-full max-w-md relative">
            <button
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
              onClick={() => setDetailLead(null)}
              title="Close"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Lead Details</h2>
            <div className="space-y-2">
              <div><span className="font-semibold">Name:</span> {detailLead.name}</div>
              <div><span className="font-semibold">Company:</span> {detailLead.company}</div>
              <div><span className="font-semibold">Status:</span> {detailLead.status}</div>
              <div><span className="font-semibold">Owner:</span> {detailLead.owner}</div>
              <div><span className="font-semibold">Created:</span> {detailLead.created}</div>
            </div>
          </div>
        </div>
      )}

      <DetailModal open={!!detailLead} onClose={() => setDetailLead(null)} title="Lead Details">
        {detailLead && (
          <>
            <div><b>Name:</b> {detailLead.title || detailLead.contact_name}</div>
            <div><b>Company:</b> {detailLead.company}</div>
            <div><b>Status:</b> {detailLead.status}</div>
            <div><b>Owner:</b> {detailLead.owner_name}</div>
            <div><b>Created:</b> {detailLead.created_at?.slice(0, 10)}</div>
          </>
        )}
      </DetailModal>
      {/* Confirmation Modal for Delete */}
      <DetailModal open={confirmDeleteId !== null} onClose={cancelDelete} title="Delete Lead?">
        <div>Are you sure you want to delete this lead?</div>
        <div className="flex gap-4 mt-6 justify-end">
          <button
            className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition"
            onClick={cancelDelete}
            disabled={actionLoading}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition"
            onClick={confirmDelete}
            disabled={actionLoading}
          >
            Delete
          </button>
        </div>
      </DetailModal>
      {/* Create Lead Modal */}
      <AnimatedModal open={showCreateModal} onClose={() => { setShowCreateModal(false); resetCreateForm(); }} title="Create Lead">
        <div className="p-8 w-full max-w-md relative">
          <button
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
            onClick={() => { setShowCreateModal(false); resetCreateForm(); }}
            title="Close"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
          <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Create New Lead</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Lead Title *
              </label>
              <input
                type="text"
                value={newLead.title}
                onChange={(e) => setNewLead({ ...newLead, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="Enter lead title"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status
              </label>
              <select
                value={newLead.status}
                onChange={(e) => setNewLead({ ...newLead, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="proposal">Proposal</option>
                <option value="negotiation">Negotiation</option>
                <option value="won">Won</option>
                <option value="lost">Lost</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Source
              </label>
              <select
                value={newLead.source}
                onChange={(e) => setNewLead({ ...newLead, source: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value="manual">Manual</option>
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="social">Social Media</option>
                <option value="email">Email Campaign</option>
              </select>
            </div>
            <div className="flex gap-4 pt-4">
              <button
                className="flex-1 px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition"
                onClick={() => { setShowCreateModal(false); resetCreateForm(); }}
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                className="flex-1 px-4 py-2 rounded-lg bg-gradient-to-r from-pink-500 to-purple-500 text-white font-semibold hover:from-pink-600 hover:to-purple-600 transition"
                onClick={handleCreateLead}
                disabled={actionLoading}
              >
                {actionLoading ? "Creating..." : "Create Lead"}
              </button>
            </div>
          </div>
        </div>
      </AnimatedModal>

      {/* Scoring Analytics Modal */}
      {showScoringModal && scoringAnalytics && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 w-full max-w-2xl relative max-h-[80vh] overflow-y-auto">
            <button
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
              onClick={() => setShowScoringModal(false)}
              title="Close"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Lead Scoring Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Summary Stats */}
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-xl p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Summary</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-300">Total Leads:</span>
                      <span className="font-semibold">{scoringAnalytics.total_leads}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-300">Average Score:</span>
                      <span className="font-semibold">{scoringAnalytics.average_score}</span>
                    </div>
                  </div>
                </div>
                
                {/* Score Distribution */}
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 rounded-xl p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Score Distribution</h3>
                  <div className="space-y-2">
                    {Object.entries(scoringAnalytics.score_distribution).map(([category, count]) => (
                      <div key={category} className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-300">{category}:</span>
                        <span className="font-semibold">{count as number}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Top Scoring Leads */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/30 dark:to-pink-900/30 rounded-xl p-4">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Top Scoring Leads</h3>
                <div className="space-y-3">
                  {scoringAnalytics.top_scoring_leads.map((lead: any) => (
                    <div key={lead.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{lead.title}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{lead.status}</div>
                      </div>
                      <LeadScore score={lead.score} size="sm" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-green-600 text-white px-6 py-3 rounded-xl shadow-lg z-50 animate-fade-in">
          {toast}
        </div>
      )}
    </div>
  );
} 