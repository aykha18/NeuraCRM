/**
 * Contacts page: Stunning table with search, filters, actions, detail modal, sorting, pagination, bulk actions, inline editing, and export
 * - Modern, responsive design matching Leads page
 */
import { useState } from "react";
import { Search, Filter, Eye, Edit, Trash2, X, ChevronUp, ChevronDown, Download } from "lucide-react";
import * as XLSX from "xlsx";

const sampleContacts = [
  { id: 1, name: "John Doe", email: "john@acme.com", company: "Acme Corp", status: "Active", owner: "Alex", created: "2024-06-01" },
  { id: 2, name: "Jane Smith", email: "jane@globex.com", company: "Globex", status: "Inactive", owner: "Sam", created: "2024-06-02" },
  { id: 3, name: "Alice Brown", email: "alice@initech.com", company: "Initech", status: "Active", owner: "Alex", created: "2024-06-03" },
  { id: 4, name: "Bob Lee", email: "bob@umbrella.com", company: "Umbrella", status: "Active", owner: "Chris", created: "2024-06-04" },
  { id: 5, name: "Charlie Black", email: "charlie@wayne.com", company: "Wayne Enterprises", status: "Inactive", owner: "Sam", created: "2024-06-05" },
  { id: 6, name: "Diana Prince", email: "diana@stark.com", company: "Stark Industries", status: "Active", owner: "Alex", created: "2024-06-06" },
  { id: 7, name: "Eve White", email: "eve@oscorp.com", company: "Oscorp", status: "Active", owner: "Chris", created: "2024-06-07" },
  { id: 8, name: "Frank Green", email: "frank@lexcorp.com", company: "LexCorp", status: "Inactive", owner: "Sam", created: "2024-06-08" },
];

const statusColors: Record<string, string> = {
  Active: "bg-green-100 text-green-700",
  Inactive: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
};

const columns = [
  { key: "name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "company", label: "Company" },
  { key: "status", label: "Status" },
  { key: "owner", label: "Owner" },
  { key: "created", label: "Created" },
];

const statusOptions = ["Active", "Inactive"];
const ownerOptions = ["Alex", "Sam", "Chris"];

export default function Contacts() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [detailContact, setDetailContact] = useState<any>(null);
  const [sortBy, setSortBy] = useState<string>("created");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<number[]>([]);
  const [contactsData, setContactsData] = useState(sampleContacts);
  const [editing, setEditing] = useState<{ id: number; field: string } | null>(null);
  const [editValue, setEditValue] = useState("");
  const pageSize = 5;

  // Filtered and sorted contacts
  let contacts = contactsData.filter(
    (contact) =>
      (!search || contact.name.toLowerCase().includes(search.toLowerCase()) || contact.company.toLowerCase().includes(search.toLowerCase()) || contact.email.toLowerCase().includes(search.toLowerCase())) &&
      (!statusFilter || contact.status === statusFilter)
  );
  contacts = contacts.sort((a, b) => {
    if ((a as any)[sortBy] < (b as any)[sortBy]) return sortDir === "asc" ? -1 : 1;
    if ((a as any)[sortBy] > (b as any)[sortBy]) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination
  const totalPages = Math.ceil(contacts.length / pageSize);
  const pagedContacts = contacts.slice((page - 1) * pageSize, page * pageSize);

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
  const deleteSelected = () => {
    alert(`Deleted ${selected.length} contacts (demo only)`);
    clearSelected();
  };

  // Inline editing logic
  const startEdit = (id: number, field: string, value: string) => {
    setEditing({ id, field });
    setEditValue(value);
  };
  const saveEdit = (id: number, field: string) => {
    setContactsData((prev) =>
      prev.map((contact) =>
        contact.id === id ? { ...contact, [field]: editValue } : contact
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

  // CSV Export
  function exportCSV() {
    const headers = ["Name", "Email", "Company", "Status", "Owner", "Created"];
    const rows = contacts.map(contact => [
      contact.name,
      contact.email,
      contact.company,
      contact.status,
      contact.owner,
      contact.created,
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

  // Excel Export
  function exportExcel() {
    const headers = ["Name", "Email", "Company", "Status", "Owner", "Created"];
    const rows = contacts.map(contact => [
      contact.name,
      contact.email,
      contact.company,
      contact.status,
      contact.owner,
      contact.created,
    ]);
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Contacts");
    XLSX.writeFile(wb, "contacts.xlsx");
  }

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
          {/* Status filter */}
          <div className="relative">
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-400 w-40 shadow appearance-none"
            >
              <option value="">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
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
                  {editing?.id === contact.id && editing.field === "name" ? (
                    <input
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => saveEdit(contact.id, "name")}
                      onKeyDown={e => handleEditKey(e, contact.id, "name")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEdit(contact.id, "name", contact.name)}
                    >
                      {contact.name}
                    </span>
                  )}
                </td>
                {/* Email (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {editing?.id === contact.id && editing.field === "email" ? (
                    <input
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => saveEdit(contact.id, "email")}
                      onKeyDown={e => handleEditKey(e, contact.id, "email")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEdit(contact.id, "email", contact.email)}
                    >
                      {contact.email}
                    </span>
                  )}
                </td>
                {/* Company (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {editing?.id === contact.id && editing.field === "company" ? (
                    <input
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => saveEdit(contact.id, "company")}
                      onKeyDown={e => handleEditKey(e, contact.id, "company")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEdit(contact.id, "company", contact.company)}
                    >
                      {contact.company}
                    </span>
                  )}
                </td>
                {/* Status (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap">
                  {editing?.id === contact.id && editing.field === "status" ? (
                    <select
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => saveEdit(contact.id, "status")}
                      onKeyDown={e => handleEditKey(e, contact.id, "status")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      {statusOptions.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <span
                      className={`cursor-pointer hover:underline px-3 py-1 rounded-full text-xs font-bold ${statusColors[contact.status]}`}
                      onClick={() => startEdit(contact.id, "status", contact.status)}
                    >
                      {contact.status}
                    </span>
                  )}
                </td>
                {/* Owner (inline edit) */}
                <td className="px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200">
                  {editing?.id === contact.id && editing.field === "owner" ? (
                    <select
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => saveEdit(contact.id, "owner")}
                      onKeyDown={e => handleEditKey(e, contact.id, "owner")}
                      className="rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      {ownerOptions.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <span
                      className="cursor-pointer hover:underline"
                      onClick={() => startEdit(contact.id, "owner", contact.owner)}
                    >
                      {contact.owner}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-500 dark:text-gray-400">{contact.created}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right flex gap-2 justify-end">
                  <button
                    className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition"
                    title="View"
                    onClick={() => setDetailContact(contact)}
                  >
                    <Eye className="w-5 h-5 text-blue-500" />
                  </button>
                  <button
                    className="p-2 rounded-full hover:bg-yellow-100 dark:hover:bg-yellow-900 transition"
                    title="Edit"
                  >
                    <Edit className="w-5 h-5 text-yellow-500" />
                  </button>
                  <button
                    className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                    title="Delete"
                  >
                    <Trash2 className="w-5 h-5 text-red-500" />
                  </button>
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
                <span className="font-bold text-lg text-gray-900 dark:text-white">{contact.name}</span>
              </div>
              <div className="flex gap-2">
                <button
                  className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition"
                  title="View"
                  onClick={() => setDetailContact(contact)}
                >
                  <Eye className="w-5 h-5 text-blue-500" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-yellow-100 dark:hover:bg-yellow-900 transition"
                  title="Edit"
                >
                  <Edit className="w-5 h-5 text-yellow-500" />
                </button>
                <button
                  className="p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition"
                  title="Delete"
                >
                  <Trash2 className="w-5 h-5 text-red-500" />
                </button>
              </div>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Email:</span> {contact.email}</div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Company:</span> {contact.company}</div>
            <div className="text-sm mb-1">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${statusColors[contact.status]}`}>{contact.status}</span>
            </div>
            <div className="text-gray-700 dark:text-gray-200 text-sm mb-1"><span className="font-semibold">Owner:</span> {contact.owner}</div>
            <div className="text-gray-500 dark:text-gray-400 text-xs"><span className="font-semibold">Created:</span> {contact.created}</div>
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

      {/* Detail Modal Skeleton */}
      {detailContact && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-8 w-full max-w-md relative">
            <button
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
              onClick={() => setDetailContact(null)}
              title="Close"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Contact Details</h2>
            <div className="space-y-2">
              <div><span className="font-semibold">Name:</span> {detailContact.name}</div>
              <div><span className="font-semibold">Email:</span> {detailContact.email}</div>
              <div><span className="font-semibold">Company:</span> {detailContact.company}</div>
              <div><span className="font-semibold">Status:</span> {detailContact.status}</div>
              <div><span className="font-semibold">Owner:</span> {detailContact.owner}</div>
              <div><span className="font-semibold">Created:</span> {detailContact.created}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 