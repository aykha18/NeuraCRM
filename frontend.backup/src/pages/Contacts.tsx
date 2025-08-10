/**
 * Contacts page: Full functionality without status
 * - NO STATUS FILTER - Contacts don't have status field
 * - FULL FUNCTIONALITY: search, sort, pagination, actions
 */
import { useEffect, useState } from "react";
import { Search, Eye, Edit, Trash2, ChevronUp, ChevronDown, Download } from "lucide-react";
import * as XLSX from "xlsx";
import { fetchContacts, getContact, updateContact, deleteContact } from "../services/contacts";
import DetailModal from "../components/DetailModal";

const columns = [
  { key: "name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "company", label: "Company" },
  { key: "owner_name", label: "Owner" },
  { key: "created_at", label: "Created" },
];

export default function ContactsNew() {
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [detailContact, setDetailContact] = useState<any | null>(null);
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number[]>([]);
  const [editingCell, setEditingCell] = useState<{ id: number; field: string } | null>(null);
  const [editCellValue, setEditCellValue] = useState("");
  const pageSize = 10;
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);

  useEffect(() => {
    console.log('ContactsNew page loading... - FULL FUNCTIONALITY');
    fetchContacts()
      .then(data => {
        console.log('Contacts loaded successfully:', data.length, 'contacts');
        setContacts(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load contacts:', err);
        setError("Failed to load contacts");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8 text-lg">Loading...</div>;
  if (error) return <div className="p-8 text-red-500">{error}</div>;

  // Filtered and sorted contacts
  let contactsToDisplay = contacts.filter(
    (contact) => {
      const matchesSearch = !search || 
        contact.name?.toLowerCase().includes(search.toLowerCase()) || 
        contact.company?.toLowerCase().includes(search.toLowerCase()) || 
        contact.email?.toLowerCase().includes(search.toLowerCase());
      
      return matchesSearch;
    }
  );
  contactsToDisplay = contactsToDisplay.sort((a, b) => {
    let aVal = (a as any)[sortBy];
    let bVal = (b as any)[sortBy];
    
    // Handle date sorting
    if (sortBy === 'created_at') {
      aVal = new Date(aVal || 0);
      bVal = new Date(bVal || 0);
    }
    
    // Handle null/undefined values
    if (!aVal && !bVal) return 0;
    if (!aVal) return sortDir === "asc" ? -1 : 1;
    if (!bVal) return sortDir === "asc" ? 1 : -1;
    
    if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(contactsToDisplay.length / pageSize);
  const pagedContacts = contactsToDisplay.slice((page - 1) * pageSize, page * pageSize);

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
  const allSelected = pagedContacts.length > 0 && pagedContacts.every((contact) => selected.includes(contact.id));
  const someSelected = pagedContacts.some((contact) => selected.includes(contact.id));
  const toggleAll = () => {
    if (allSelected) {
      setSelected(selected.filter(id => !pagedContacts.some(l => l.id === id)));
    } else {
      setSelected([...selected, ...pagedContacts.filter(l => !selected.includes(l.id)).map(l => l.id)]);
    }
  };
  const toggleOne = (id: number) => {
    setSelected(selected.includes(id) ? selected.filter(i => i !== id) : [...selected, id]);
  };
  const clearSelected = () => setSelected([]);
  const confirmBulkDeleteAction = () => {
    setConfirmBulkDelete(true);
  };
  
  const cancelBulkDelete = () => {
    setConfirmBulkDelete(false);
  };
  
  const deleteSelected = async () => {
    if (selected.length === 0) return;
    
    setActionLoading(true);
    try {
      const deletePromises = selected.map(id => deleteContact(id));
      await Promise.all(deletePromises);
      await fetchContacts().then(setContacts);
      setToast(`Successfully deleted ${selected.length} contacts`);
      setTimeout(() => setToast(null), 2000);
      clearSelected();
    } catch (e) {
      alert("Failed to delete selected contacts");
    }
    setActionLoading(false);
    setConfirmBulkDelete(false);
  };

  // Cell editing logic
  const startEditCell = (id: number, field: string, value: string) => {
    setEditingCell({ id, field });
    setEditCellValue(value);
  };
  const saveEditCell = async (id: number, field: string) => {
    setActionLoading(true);
    try {
      await updateContact(id, { [field]: editCellValue });
      await fetchContacts().then(setContacts);
      setToast("Contact updated!");
      setTimeout(() => setToast(null), 2000);
    } catch (e) {
      alert("Failed to update contact");
    }
    setActionLoading(false);
    setEditingCell(null);
    setEditCellValue("");
  };
  const handleEditCellKey = (e: React.KeyboardEvent, id: number, field: string) => {
    if (e.key === "Enter") {
      saveEditCell(id, field);
    } else if (e.key === "Escape") {
      setEditingCell(null);
      setEditCellValue("");
    }
  };

  // Export functions
  function exportCSV() {
    const headers = ["Name", "Email", "Company", "Owner", "Created"];
    const rows = contactsToDisplay.map(contact => [
      contact.name,
      contact.email,
      contact.company,
      contact.owner_name,
      contact.created_at?.slice(0, 10) || "",
    ]);
    const csvContent =
      [headers, ...rows]
        .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(","))
        .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "contacts.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  function exportExcel() {
    const headers = ["Name", "Email", "Company", "Owner", "Created"];
    const rows = contactsToDisplay.map(contact => [
      contact.name,
      contact.email,
      contact.company,
      contact.owner_name,
      contact.created_at?.slice(0, 10) || "",
    ]);
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Contacts");
    XLSX.writeFile(wb, "contacts.xlsx");
  }

  // Action handlers
  const handleView = async (id: number) => {
    setActionLoading(true);
    try {
      const contact = await getContact(id);
      setDetailContact(contact);
    } catch (e) {
      alert("Failed to fetch contact details");
    }
    setActionLoading(false);
  };

  const handleDelete = async (id: number) => {
    setConfirmDeleteId(id);
  };

  const confirmDelete = async () => {
    if (confirmDeleteId === null) return;
    setActionLoading(true);
    try {
      await deleteContact(confirmDeleteId);
      fetchContacts().then(setContacts);
      setToast("Contact deleted!");
      setTimeout(() => setToast(null), 2000);
    } catch (e) {
      alert("Failed to delete contact");
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
              className="px-4 py-1 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={confirmBulkDeleteAction}
              disabled={actionLoading}
            >
              Delete Selected
            </button>
            <button
              className="px-4 py-1 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={clearSelected}
              disabled={actionLoading}
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Header and actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white">Contacts</h1>
        <div className="flex gap-2 items-center">
          {/* Search bar */}
          <div className="relative">
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search contacts..."
              className="rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 w-56 shadow"
            />
            <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
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
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th className="px-4 py-3 text-center">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={el => { if (el) el.indeterminate = !allSelected && someSelected; }}
                  onChange={toggleAll}
                  className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                />
              </th>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer select-none group"
                  onClick={() => handleSort(col.key)}
                >
                  <span className="flex items-center gap-1">
                    {col.label}
                    {sortBy === col.key && (
                      sortDir === "asc" ? (
                        <ChevronUp className="w-4 h-4 text-pink-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-pink-500" />
                      )
                    )}
                  </span>
                </th>
              ))}
              <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
            {pagedContacts.map((contact) => (
              <tr
                key={contact.id}
                className={`transition ${selected.includes(contact.id) ? "bg-pink-100 dark:bg-pink-900/40" : "hover:bg-pink-50 dark:hover:bg-pink-900/20"}`}
              >
                <td className="px-4 py-4 text-center">
                  <input
                    type="checkbox"
                    checked={selected.includes(contact.id)}
                    onChange={() => toggleOne(contact.id)}
                    className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                  />
                </td>
                {/* Name (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap font-semibold text-gray-900 dark:text-white">
                  {editingCell && editingCell.id === contact.id && editingCell.field === "name" ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={e => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(contact.id, "name")}
                      onKeyDown={e => handleEditCellKey(e, contact.id, "name")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEditCell(contact.id, "name", contact.name)}
                    >
                      {contact.name || contact.contact_name}
                    </span>
                  )}
                </td>
                {/* Email (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {editingCell && editingCell.id === contact.id && editingCell.field === "email" ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={e => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(contact.id, "email")}
                      onKeyDown={e => handleEditCellKey(e, contact.id, "email")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEditCell(contact.id, "email", contact.email)}
                    >
                      {contact.email}
                    </span>
                  )}
                </td>
                {/* Company (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {editingCell && editingCell.id === contact.id && editingCell.field === "company" ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={e => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(contact.id, "company")}
                      onKeyDown={e => handleEditCellKey(e, contact.id, "company")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEditCell(contact.id, "company", contact.company)}
                    >
                      {contact.company}
                    </span>
                  )}
                </td>
                {/* Owner */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {contact.owner_name || "N/A"}
                </td>
                {/* Created */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-500 dark:text-gray-400 text-sm">
                  {contact.created_at?.slice(0, 10) || "N/A"}
                </td>
                {/* Actions */}
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    <button
                      className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition"
                      title="View"
                      onClick={() => handleView(contact.id)}
                      disabled={actionLoading}
                    >
                      <Eye className="w-5 h-5 text-blue-500" />
                    </button>
                    <button
                      className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                      title="Delete"
                      onClick={() => handleDelete(contact.id)}
                      disabled={actionLoading}
                    >
                      <Trash2 className="w-5 h-5 text-red-500" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {pagedContacts.length === 0 && (
              <tr>
                <td colSpan={columns.length + 2} className="text-center py-8 text-gray-400 dark:text-gray-600">No contacts found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Responsive Card View: only on mobile */}
      <div className="sm:hidden space-y-4">
        {pagedContacts.map((contact) => (
          <div
            key={contact.id}
            className={`rounded-2xl shadow border p-4 bg-white dark:bg-gray-900 transition ${selected.includes(contact.id) ? "bg-pink-100 dark:bg-pink-900/40 border-pink-300 dark:border-pink-800" : "hover:bg-pink-50 dark:hover:bg-pink-900/20"}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selected.includes(contact.id)}
                  onChange={() => toggleOne(contact.id)}
                  className="accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                />
                <span className="font-bold text-lg text-gray-900 dark:text-white">{contact.name || contact.contact_name}</span>
              </div>
              <div className="flex gap-2">
                <button
                  className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition"
                  title="View"
                  onClick={() => handleView(contact.id)}
                  disabled={actionLoading}
                >
                  <Eye className="w-5 h-5 text-blue-500" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-yellow-100 dark:hover:bg-yellow-900 transition"
                  title="Edit"
                  disabled={actionLoading}
                >
                  <Edit className="w-5 h-5 text-yellow-500" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                  title="Delete"
                  onClick={() => handleDelete(contact.id)}
                  disabled={actionLoading}
                >
                  <Trash2 className="w-5 h-5 text-red-500" />
                </button>
              </div>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Email:</span> {contact.email}</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Company:</span> {contact.company}</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Owner:</span> {contact.owner_name || "N/A"}</div>
            <div className="text-gray-500 dark:text-gray-400 text-xs"><span className="font-semibold">Created:</span> {contact.created_at?.slice(0, 10) || "N/A"}</div>
          </div>
        ))}
        {pagedContacts.length === 0 && (
          <div className="text-center py-8 text-gray-400 dark:text-gray-600">No contacts found.</div>
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

      {/* Detail Modal using the DetailModal component */}
      <DetailModal open={!!detailContact} onClose={() => setDetailContact(null)} title="Contact Details">
        {detailContact && (
          <>
            <div><b>Name:</b> {detailContact.name}</div>
            <div><b>Email:</b> {detailContact.email}</div>
            <div><b>Company:</b> {detailContact.company}</div>
            <div><b>Owner:</b> {detailContact.owner_name || detailContact.owner}</div>
            <div><b>Created:</b> {detailContact.created_at?.slice(0, 10) || detailContact.created}</div>
          </>
        )}
      </DetailModal>

      {/* Confirmation Modal for Single Delete */}
      <DetailModal open={confirmDeleteId !== null} onClose={cancelDelete} title="Delete Contact?">
        <div>Are you sure you want to delete this contact?</div>
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

      {/* Confirmation Modal for Bulk Delete */}
      <DetailModal open={confirmBulkDelete} onClose={cancelBulkDelete} title="Delete Multiple Contacts?">
        <div>Are you sure you want to delete {selected.length} contacts? This action cannot be undone.</div>
        <div className="flex gap-4 mt-6 justify-end">
          <button
            className="px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition"
            onClick={cancelBulkDelete}
            disabled={actionLoading}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition"
            onClick={deleteSelected}
            disabled={actionLoading}
          >
            {actionLoading ? "Deleting..." : "Delete All"}
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