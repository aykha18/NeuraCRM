/**
 * Leads page: Stunning table with search, filters, actions, detail modal, sorting, pagination, bulk actions, and inline editing
 * - Modern, responsive design matching dashboard
 * - Column sorting, pagination, bulk actions, row highlight, inline editing
 */
import { useEffect, useState } from "react";
import { Search, Filter, Eye, Edit, Trash2, X, ChevronUp, ChevronDown, Download } from "lucide-react";
import * as XLSX from "xlsx";
import { fetchLeads, getLead, updateLead, deleteLead } from "../services/leads";
import DetailModal from "../components/DetailModal";

const statusColors: Record<string, string> = {
  New: "bg-blue-100 text-blue-700",
  Contacted: "bg-yellow-100 text-yellow-700",
  Qualified: "bg-green-100 text-green-700",
  Lost: "bg-red-100 text-red-700",
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
  { key: "name", label: "Name" },
  { key: "company", label: "Company" },
  { key: "status", label: "Status" },
  { key: "owner", label: "Owner" },
  { key: "created", label: "Created" },
];

const statusOptions = ["New", "Contacted", "Qualified", "Lost"];
const ownerOptions = ["Alex", "Sam", "Chris"];

export default function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [detailLead, setDetailLead] = useState<any | null>(null);
  const [editingCell, setEditingCell] = useState<{ id: number; field: string } | null>(null);
  const [editCellValue, setEditCellValue] = useState("");
  const [sortBy, setSortBy] = useState<string>("created");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number[]>([]);
  const [leadsData, setLeadsData] = useState(leads); // This state is no longer needed for static data
  const [editing, setEditing] = useState<{ id: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState("");
  const pageSize = 10;
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  useEffect(() => {
    fetchLeads()
      .then(data => {
        setLeads(data);
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to load leads");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-lg">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  // Filtered and sorted leads
  let leadsToDisplay = leads.filter(
    (lead) =>
      (!search || lead.name.toLowerCase().includes(search.toLowerCase()) || lead.company.toLowerCase().includes(search.toLowerCase())) &&
      (!statusFilter || lead.status === statusFilter)
  );
  leadsToDisplay = leadsToDisplay.sort((a, b) => {
    if ((a as any)[sortBy] < (b as any)[sortBy]) return sortDir === "asc" ? -1 : 1;
    if ((a as any)[sortBy] > (b as any)[sortBy]) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(leadsToDisplay.length / pageSize);
  const pagedLeads = leadsToDisplay.slice((page - 1) * pageSize, page * pageSize);

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
  const startEdit = (id: number, field: string, value: string) => {
    setEditing({ id, field });
    setEditValue(value);
  };
  const saveEdit = (id: number, field: string) => {
    setLeads((prev) =>
      prev.map((lead) =>
        lead.id === id ? { ...lead, [field]: editValue } : lead
      )
    );
    setEditing(null);
    setEditValue("");
  };
  const handleEditKey = (e: React.KeyboardEvent, id: number, field: string) => {
    if (e.key === "Enter") {
      saveEdit(id, field);
    } else if (e.key === "Escape") {
      setEditing(null);
      setEditValue("");
    }
  };

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
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">Leads</h1>
        <div className="flex gap-2 items-center">
          {/* Search bar */}
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search leads..."
              className="rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 w-56 shadow"
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
              <option value="New">New</option>
              <option value="Contacted">Contacted</option>
              <option value="Qualified">Qualified</option>
              <option value="Lost">Lost</option>
            </select>
            <Filter className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
          </div>
          {/* Export buttons */}
          <button
            className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition flex items-center gap-2"
            onClick={exportCSV}
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button
            className="px-4 py-2 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-white font-semibold shadow hover:from-green-600 hover:to-teal-600 transition flex items-center gap-2"
            onClick={exportExcel}
          >
            <Download className="w-4 h-4" />
            Export Excel
          </button>
        </div>
      </div>

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
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Name</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Company</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Status</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Owner</th>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-700 dark:text-gray-200">Created</th>
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
                      {lead.status}
                    </span>
                  )}
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
                  {/* <button
                    className="text-yellow-500 hover:text-yellow-700"
                    title="Edit"
                    onClick={() => handleEdit(lead.id)}
                    disabled={actionLoading}
                  >
                    <Edit />
                  </button> */}
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
                <button
                  className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5 text-red-500" />
                </button>
              </div>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Company:</span> {lead.company}</div>
            <div className="text-sm mb-1">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[lead.status]}`}>{lead.status}</span>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Owner:</span> {lead.owner}</div>
            <div className="text-gray-500 dark:text-gray-400 text-xs"><span className="font-semibold">Created:</span> {lead.created}</div>
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
      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-6 right-6 bg-green-600 text-white px-6 py-3 rounded-xl shadow-lg z-50 animate-fade-in">
          {toast}
        </div>
      )}
    </div>
  );
} 