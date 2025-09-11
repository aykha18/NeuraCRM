import { createHotContext as __vite__createHotContext } from "/@vite/client";import.meta.hot = __vite__createHotContext("/src/pages/Contacts.tsx");import __vite__cjsImport0_react_jsxDevRuntime from "/node_modules/.vite/deps/react_jsx-dev-runtime.js?v=d124530c"; const Fragment = __vite__cjsImport0_react_jsxDevRuntime["Fragment"]; const jsxDEV = __vite__cjsImport0_react_jsxDevRuntime["jsxDEV"];
import * as RefreshRuntime from "/@react-refresh";
const inWebWorker = typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope;
let prevRefreshReg;
let prevRefreshSig;
if (import.meta.hot && !inWebWorker) {
  if (!window.$RefreshReg$) {
    throw new Error(
      "@vitejs/plugin-react can't detect preamble. Something is wrong."
    );
  }
  prevRefreshReg = window.$RefreshReg$;
  prevRefreshSig = window.$RefreshSig$;
  window.$RefreshReg$ = RefreshRuntime.getRefreshReg("C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx");
  window.$RefreshSig$ = RefreshRuntime.createSignatureFunctionForTransform;
}
var _s = $RefreshSig$();
import __vite__cjsImport3_react from "/node_modules/.vite/deps/react.js?v=d124530c"; const useEffect = __vite__cjsImport3_react["useEffect"]; const useState = __vite__cjsImport3_react["useState"];
import { Search, Eye, Edit, Trash2, ChevronUp, ChevronDown, Download, Plus } from "/node_modules/.vite/deps/lucide-react.js?v=d124530c";
import * as XLSX from "/node_modules/.vite/deps/xlsx.js?v=d124530c";
import { fetchContacts, getContact, updateContact, deleteContact, createContact } from "/src/services/contacts.ts";
import DetailModal from "/src/components/DetailModal.tsx";
const columns = [
  { key: "name", label: "Name" },
  { key: "email", label: "Email" },
  { key: "company", label: "Company" },
  { key: "owner_name", label: "Owner" },
  { key: "created_at", label: "Created" }
];
export default function ContactsNew() {
  _s();
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [detailContact, setDetailContact] = useState(null);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortDir, setSortDir] = useState("desc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState([]);
  const [editingCell, setEditingCell] = useState(null);
  const [editCellValue, setEditCellValue] = useState("");
  const pageSize = 10;
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newContact, setNewContact] = useState({
    name: "",
    email: "",
    company: ""
  });
  useEffect(() => {
    console.log("ContactsNew page loading... - FULL FUNCTIONALITY");
    fetchContacts().then((data) => {
      console.log("Contacts loaded successfully:", data.length, "contacts");
      setContacts(data);
      setLoading(false);
    }).catch((err) => {
      console.error("Failed to load contacts:", err);
      setError("Failed to load contacts");
      setLoading(false);
    });
  }, []);
  if (loading) return /* @__PURE__ */ jsxDEV("div", { className: "p-8 text-lg", children: "Loading..." }, void 0, false, {
    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
    lineNumber: 79,
    columnNumber: 23
  }, this);
  if (error) return /* @__PURE__ */ jsxDEV("div", { className: "p-8 text-red-500", children: error }, void 0, false, {
    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
    lineNumber: 80,
    columnNumber: 21
  }, this);
  let contactsToDisplay = contacts.filter(
    (contact) => {
      const matchesSearch = !search || contact.name?.toLowerCase().includes(search.toLowerCase()) || contact.company?.toLowerCase().includes(search.toLowerCase()) || contact.email?.toLowerCase().includes(search.toLowerCase());
      return matchesSearch;
    }
  );
  contactsToDisplay = contactsToDisplay.sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    if (sortBy === "created_at") {
      aVal = new Date(aVal || 0);
      bVal = new Date(bVal || 0);
    }
    if (!aVal && !bVal) return 0;
    if (!aVal) return sortDir === "asc" ? -1 : 1;
    if (!bVal) return sortDir === "asc" ? 1 : -1;
    if (aVal < bVal) return sortDir === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDir === "asc" ? 1 : -1;
    return 0;
  });
  const totalPages = Math.ceil(contactsToDisplay.length / pageSize);
  const pagedContacts = contactsToDisplay.slice((page - 1) * pageSize, page * pageSize);
  const handleSort = (col) => {
    if (sortBy === col) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortDir("asc");
    }
    setPage(1);
  };
  const allSelected = pagedContacts.length > 0 && pagedContacts.every((contact) => selected.includes(contact.id));
  const someSelected = pagedContacts.some((contact) => selected.includes(contact.id));
  const toggleAll = () => {
    if (allSelected) {
      setSelected(selected.filter((id) => !pagedContacts.some((l) => l.id === id)));
    } else {
      setSelected([...selected, ...pagedContacts.filter((l) => !selected.includes(l.id)).map((l) => l.id)]);
    }
  };
  const toggleOne = (id) => {
    setSelected(selected.includes(id) ? selected.filter((i) => i !== id) : [...selected, id]);
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
      const deletePromises = selected.map((id) => deleteContact(id));
      await Promise.all(deletePromises);
      await fetchContacts().then(setContacts);
      setToast(`Successfully deleted ${selected.length} contacts`);
      setTimeout(() => setToast(null), 2e3);
      clearSelected();
    } catch (e) {
      alert("Failed to delete selected contacts");
    }
    setActionLoading(false);
    setConfirmBulkDelete(false);
  };
  const startEditCell = (id, field, value) => {
    setEditingCell({ id, field });
    setEditCellValue(value);
  };
  const saveEditCell = async (id, field) => {
    setActionLoading(true);
    try {
      await updateContact(id, { [field]: editCellValue });
      await fetchContacts().then(setContacts);
      setToast("Contact updated!");
      setTimeout(() => setToast(null), 2e3);
    } catch (e) {
      alert("Failed to update contact");
    }
    setActionLoading(false);
    setEditingCell(null);
    setEditCellValue("");
  };
  const handleEditCellKey = (e, id, field) => {
    if (e.key === "Enter") {
      saveEditCell(id, field);
    } else if (e.key === "Escape") {
      setEditingCell(null);
      setEditCellValue("");
    }
  };
  function exportCSV() {
    const headers = ["Name", "Email", "Company", "Owner", "Created"];
    const rows = contactsToDisplay.map(
      (contact) => [
        contact.name,
        contact.email,
        contact.company,
        contact.owner_name,
        contact.created_at?.slice(0, 10) || ""
      ]
    );
    const csvContent = [headers, ...rows].map((row) => row.map((field) => `"${String(field).replace(/"/g, '""')}"`).join(",")).join("\n");
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
    const rows = contactsToDisplay.map(
      (contact) => [
        contact.name,
        contact.email,
        contact.company,
        contact.owner_name,
        contact.created_at?.slice(0, 10) || ""
      ]
    );
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Contacts");
    XLSX.writeFile(wb, "contacts.xlsx");
  }
  const handleView = async (id) => {
    setActionLoading(true);
    try {
      const contact = await getContact(id);
      setDetailContact(contact);
    } catch (e) {
      alert("Failed to fetch contact details");
    }
    setActionLoading(false);
  };
  const handleDelete = async (id) => {
    setConfirmDeleteId(id);
  };
  const confirmDelete = async () => {
    if (confirmDeleteId === null) return;
    setActionLoading(true);
    try {
      await deleteContact(confirmDeleteId);
      fetchContacts().then(setContacts);
      setToast("Contact deleted!");
      setTimeout(() => setToast(null), 2e3);
    } catch (e) {
      alert("Failed to delete contact");
    }
    setActionLoading(false);
    setConfirmDeleteId(null);
  };
  const cancelDelete = () => setConfirmDeleteId(null);
  const handleCreateContact = async () => {
    if (!newContact.name.trim()) {
      setToast("Name is required");
      return;
    }
    setActionLoading(true);
    try {
      const createdContact = await createContact(newContact);
      setContacts([...contacts, createdContact]);
      setShowCreateModal(false);
      setNewContact({ name: "", email: "", company: "" });
      setToast("Contact created successfully!");
    } catch (error2) {
      setToast("Failed to create contact");
    } finally {
      setActionLoading(false);
    }
  };
  return /* @__PURE__ */ jsxDEV("div", { className: "p-2 md:p-6", children: [
    selected.length > 0 && /* @__PURE__ */ jsxDEV("div", { className: "flex items-center justify-between bg-pink-50 dark:bg-pink-900/30 border border-pink-200 dark:border-pink-800 rounded-xl px-4 py-2 mb-4 shadow animate-fade-in", children: [
      /* @__PURE__ */ jsxDEV("span", { className: "text-pink-700 dark:text-pink-200 font-semibold", children: [
        selected.length,
        " selected"
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 292,
        columnNumber: 11
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "flex gap-2", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-1 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition disabled:opacity-50 disabled:cursor-not-allowed",
            onClick: confirmBulkDeleteAction,
            disabled: actionLoading,
            children: "Delete Selected"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 294,
            columnNumber: 13
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-1 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition disabled:opacity-50 disabled:cursor-not-allowed",
            onClick: clearSelected,
            disabled: actionLoading,
            children: "Clear"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 301,
            columnNumber: 13
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 293,
        columnNumber: 11
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 291,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "flex flex-col gap-4 mb-6", children: [
      /* @__PURE__ */ jsxDEV("h1", { className: "text-3xl font-extrabold text-red-600 dark:text-red-400", children: "Contacts - ADD CONTACT BUTTON IS HERE!" }, void 0, false, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 314,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "flex flex-wrap gap-2 items-center", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-6 py-3 rounded-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-bold shadow-lg hover:from-red-600 hover:to-orange-600 transition flex items-center gap-2 text-lg",
            onClick: () => setShowCreateModal(true),
            children: [
              /* @__PURE__ */ jsxDEV(Plus, { className: "w-5 h-5" }, void 0, false, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 321,
                columnNumber: 13
              }, this),
              "????????? ADD CONTACT BUTTON ?????????"
            ]
          },
          void 0,
          true,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 317,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-6 py-3 rounded-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-bold shadow-lg hover:from-red-600 hover:to-orange-600 transition flex items-center gap-2 text-lg",
            onClick: () => setShowCreateModal(true),
            children: [
              /* @__PURE__ */ jsxDEV(Plus, { className: "w-5 h-5" }, void 0, false, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 329,
                columnNumber: 13
              }, this),
              "????????? ADD CONTACT BUTTON ?????????"
            ]
          },
          void 0,
          true,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 325,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV("div", { className: "relative", children: [
          /* @__PURE__ */ jsxDEV(
            "input",
            {
              type: "text",
              value: search,
              onChange: (e) => setSearch(e.target.value),
              placeholder: "Search contacts... - UPDATED",
              className: "rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 w-56 shadow"
            },
            void 0,
            false,
            {
              fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
              lineNumber: 335,
              columnNumber: 13
            },
            this
          ),
          /* @__PURE__ */ jsxDEV(Search, { className: "absolute left-3 top-2.5 w-5 h-5 text-gray-400" }, void 0, false, {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 342,
            columnNumber: 13
          }, this)
        ] }, void 0, true, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 334,
          columnNumber: 11
        }, this),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold shadow hover:from-blue-600 hover:to-purple-600 transition flex items-center gap-2",
            onClick: exportCSV,
            children: [
              /* @__PURE__ */ jsxDEV(Download, { className: "w-4 h-4" }, void 0, false, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 350,
                columnNumber: 13
              }, this),
              "Export CSV"
            ]
          },
          void 0,
          true,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 346,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gradient-to-r from-green-500 to-teal-500 text-white font-semibold shadow hover:from-green-600 hover:to-teal-600 transition flex items-center gap-2",
            onClick: exportExcel,
            children: [
              /* @__PURE__ */ jsxDEV(Download, { className: "w-4 h-4" }, void 0, false, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 357,
                columnNumber: 13
              }, this),
              "Export Excel"
            ]
          },
          void 0,
          true,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 353,
            columnNumber: 11
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 315,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 313,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "overflow-x-auto rounded-2xl shadow border bg-white dark:bg-gray-900 hidden sm:block", children: /* @__PURE__ */ jsxDEV("table", { className: "min-w-full divide-y divide-gray-200 dark:divide-gray-800", children: [
      /* @__PURE__ */ jsxDEV("thead", { className: "bg-gray-50 dark:bg-gray-800", children: /* @__PURE__ */ jsxDEV("tr", { children: [
        /* @__PURE__ */ jsxDEV("th", { className: "px-4 py-3 text-center", children: /* @__PURE__ */ jsxDEV(
          "input",
          {
            type: "checkbox",
            checked: allSelected,
            ref: (el) => {
              if (el) el.indeterminate = !allSelected && someSelected;
            },
            onChange: toggleAll,
            className: "accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 369,
            columnNumber: 17
          },
          this
        ) }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 368,
          columnNumber: 15
        }, this),
        columns.map(
          (col) => /* @__PURE__ */ jsxDEV(
            "th",
            {
              className: "px-6 py-3 text-left text-xs font-bold text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer select-none group",
              onClick: () => handleSort(col.key),
              children: /* @__PURE__ */ jsxDEV("span", { className: "flex items-center gap-1", children: [
                col.label,
                sortBy === col.key && (sortDir === "asc" ? /* @__PURE__ */ jsxDEV(ChevronUp, { className: "w-4 h-4 text-pink-500" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 387,
                  columnNumber: 19
                }, this) : /* @__PURE__ */ jsxDEV(ChevronDown, { className: "w-4 h-4 text-pink-500" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 389,
                  columnNumber: 19
                }, this))
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 383,
                columnNumber: 19
              }, this)
            },
            col.key,
            false,
            {
              fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
              lineNumber: 378,
              columnNumber: 15
            },
            this
          )
        ),
        /* @__PURE__ */ jsxDEV("th", { className: "px-6 py-3 text-right text-xs font-bold text-gray-500 dark:text-gray-300 uppercase tracking-wider", children: "Actions" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 395,
          columnNumber: 15
        }, this)
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 367,
        columnNumber: 13
      }, this) }, void 0, false, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 366,
        columnNumber: 11
      }, this),
      /* @__PURE__ */ jsxDEV("tbody", { className: "bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800", children: [
        pagedContacts.map(
          (contact) => /* @__PURE__ */ jsxDEV(
            "tr",
            {
              className: `transition ${selected.includes(contact.id) ? "bg-pink-100 dark:bg-pink-900/40" : "hover:bg-pink-50 dark:hover:bg-pink-900/20"}`,
              children: [
                /* @__PURE__ */ jsxDEV("td", { className: "px-4 py-4 text-center", children: /* @__PURE__ */ jsxDEV(
                  "input",
                  {
                    type: "checkbox",
                    checked: selected.includes(contact.id),
                    onChange: () => toggleOne(contact.id),
                    className: "accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 405,
                    columnNumber: 19
                  },
                  this
                ) }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 404,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap font-semibold text-gray-900 dark:text-white", children: editingCell && editingCell.id === contact.id && editingCell.field === "name" ? /* @__PURE__ */ jsxDEV(
                  "input",
                  {
                    autoFocus: true,
                    value: editCellValue,
                    onChange: (e) => setEditCellValue(e.target.value),
                    onBlur: () => saveEditCell(contact.id, "name"),
                    onKeyDown: (e) => handleEditCellKey(e, contact.id, "name"),
                    className: "rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 415,
                    columnNumber: 17
                  },
                  this
                ) : /* @__PURE__ */ jsxDEV(
                  "span",
                  {
                    className: "cursor-pointer hover:underline",
                    onClick: () => startEditCell(contact.id, "name", contact.name),
                    children: contact.name || contact.contact_name
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 424,
                    columnNumber: 17
                  },
                  this
                ) }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 413,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200", children: editingCell && editingCell.id === contact.id && editingCell.field === "email" ? /* @__PURE__ */ jsxDEV(
                  "input",
                  {
                    autoFocus: true,
                    value: editCellValue,
                    onChange: (e) => setEditCellValue(e.target.value),
                    onBlur: () => saveEditCell(contact.id, "email"),
                    onKeyDown: (e) => handleEditCellKey(e, contact.id, "email"),
                    className: "rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 435,
                    columnNumber: 17
                  },
                  this
                ) : /* @__PURE__ */ jsxDEV(
                  "span",
                  {
                    className: "cursor-pointer hover:underline",
                    onClick: () => startEditCell(contact.id, "email", contact.email),
                    children: contact.email
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 444,
                    columnNumber: 17
                  },
                  this
                ) }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 433,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200", children: editingCell && editingCell.id === contact.id && editingCell.field === "company" ? /* @__PURE__ */ jsxDEV(
                  "input",
                  {
                    autoFocus: true,
                    value: editCellValue,
                    onChange: (e) => setEditCellValue(e.target.value),
                    onBlur: () => saveEditCell(contact.id, "company"),
                    onKeyDown: (e) => handleEditCellKey(e, contact.id, "company"),
                    className: "rounded px-2 py-1 border-2 border-pink-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 455,
                    columnNumber: 17
                  },
                  this
                ) : /* @__PURE__ */ jsxDEV(
                  "span",
                  {
                    className: "cursor-pointer hover:underline",
                    onClick: () => startEditCell(contact.id, "company", contact.company),
                    children: contact.company
                  },
                  void 0,
                  false,
                  {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 464,
                    columnNumber: 17
                  },
                  this
                ) }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 453,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap text-gray-700 dark:text-gray-200", children: contact.owner_name || "N/A" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 473,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap text-gray-500 dark:text-gray-400 text-sm", children: contact.created_at?.slice(0, 10) || "N/A" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 477,
                  columnNumber: 17
                }, this),
                /* @__PURE__ */ jsxDEV("td", { className: "px-6 py-4 whitespace-nowrap text-right text-sm font-medium", children: /* @__PURE__ */ jsxDEV("div", { className: "flex justify-end gap-2", children: [
                  /* @__PURE__ */ jsxDEV(
                    "button",
                    {
                      className: "p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition",
                      title: "View",
                      onClick: () => handleView(contact.id),
                      disabled: actionLoading,
                      children: /* @__PURE__ */ jsxDEV(Eye, { className: "w-5 h-5 text-blue-500" }, void 0, false, {
                        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                        lineNumber: 489,
                        columnNumber: 23
                      }, this)
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 483,
                      columnNumber: 21
                    },
                    this
                  ),
                  /* @__PURE__ */ jsxDEV(
                    "button",
                    {
                      className: "p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition",
                      title: "Delete",
                      onClick: () => handleDelete(contact.id),
                      disabled: actionLoading,
                      children: /* @__PURE__ */ jsxDEV(Trash2, { className: "w-5 h-5 text-red-500" }, void 0, false, {
                        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                        lineNumber: 497,
                        columnNumber: 23
                      }, this)
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 491,
                      columnNumber: 21
                    },
                    this
                  )
                ] }, void 0, true, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 482,
                  columnNumber: 19
                }, this) }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 481,
                  columnNumber: 17
                }, this)
              ]
            },
            contact.id,
            true,
            {
              fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
              lineNumber: 400,
              columnNumber: 13
            },
            this
          )
        ),
        pagedContacts.length === 0 && /* @__PURE__ */ jsxDEV("tr", { children: /* @__PURE__ */ jsxDEV("td", { colSpan: columns.length + 2, className: "text-center py-8 text-gray-400 dark:text-gray-600", children: "No contacts found." }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 505,
          columnNumber: 17
        }, this) }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 504,
          columnNumber: 13
        }, this)
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 398,
        columnNumber: 11
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 365,
      columnNumber: 9
    }, this) }, void 0, false, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 364,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "sm:hidden space-y-4", children: [
      pagedContacts.map(
        (contact) => /* @__PURE__ */ jsxDEV(
          "div",
          {
            className: `rounded-2xl shadow border p-4 bg-white dark:bg-gray-900 transition ${selected.includes(contact.id) ? "bg-pink-100 dark:bg-pink-900/40 border-pink-300 dark:border-pink-800" : "hover:bg-pink-50 dark:hover:bg-pink-900/20"}`,
            children: [
              /* @__PURE__ */ jsxDEV("div", { className: "flex items-center justify-between mb-2", children: [
                /* @__PURE__ */ jsxDEV("div", { className: "flex items-center gap-2", children: [
                  /* @__PURE__ */ jsxDEV(
                    "input",
                    {
                      type: "checkbox",
                      checked: selected.includes(contact.id),
                      onChange: () => toggleOne(contact.id),
                      className: "accent-pink-500 w-5 h-5 rounded focus:ring-pink-400"
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 521,
                      columnNumber: 17
                    },
                    this
                  ),
                  /* @__PURE__ */ jsxDEV("span", { className: "font-bold text-lg text-gray-900 dark:text-white", children: contact.name || contact.contact_name }, void 0, false, {
                    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                    lineNumber: 527,
                    columnNumber: 17
                  }, this)
                ] }, void 0, true, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 520,
                  columnNumber: 15
                }, this),
                /* @__PURE__ */ jsxDEV("div", { className: "flex gap-2", children: [
                  /* @__PURE__ */ jsxDEV(
                    "button",
                    {
                      className: "p-2 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900 transition",
                      title: "View",
                      onClick: () => handleView(contact.id),
                      disabled: actionLoading,
                      children: /* @__PURE__ */ jsxDEV(Eye, { className: "w-5 h-5 text-blue-500" }, void 0, false, {
                        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                        lineNumber: 536,
                        columnNumber: 19
                      }, this)
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 530,
                      columnNumber: 17
                    },
                    this
                  ),
                  /* @__PURE__ */ jsxDEV(
                    "button",
                    {
                      className: "p-2 rounded-full hover:bg-yellow-100 dark:hover:bg-yellow-900 transition",
                      title: "Edit",
                      disabled: actionLoading,
                      children: /* @__PURE__ */ jsxDEV(Edit, { className: "w-5 h-5 text-yellow-500" }, void 0, false, {
                        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                        lineNumber: 543,
                        columnNumber: 19
                      }, this)
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 538,
                      columnNumber: 17
                    },
                    this
                  ),
                  /* @__PURE__ */ jsxDEV(
                    "button",
                    {
                      className: "p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition",
                      title: "Delete",
                      onClick: () => handleDelete(contact.id),
                      disabled: actionLoading,
                      children: /* @__PURE__ */ jsxDEV(Trash2, { className: "w-5 h-5 text-red-500" }, void 0, false, {
                        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                        lineNumber: 551,
                        columnNumber: 19
                      }, this)
                    },
                    void 0,
                    false,
                    {
                      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                      lineNumber: 545,
                      columnNumber: 17
                    },
                    this
                  )
                ] }, void 0, true, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 529,
                  columnNumber: 15
                }, this)
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 519,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "text-gray-700 dark:text-gray-200 text-sm mb-1", children: [
                /* @__PURE__ */ jsxDEV("span", { className: "font-semibold", children: "Email:" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 555,
                  columnNumber: 76
                }, this),
                " ",
                contact.email
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 555,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "text-gray-700 dark:text-gray-200 text-sm mb-1", children: [
                /* @__PURE__ */ jsxDEV("span", { className: "font-semibold", children: "Company:" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 556,
                  columnNumber: 76
                }, this),
                " ",
                contact.company
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 556,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "text-gray-700 dark:text-gray-200 text-sm mb-1", children: [
                /* @__PURE__ */ jsxDEV("span", { className: "font-semibold", children: "Owner:" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 557,
                  columnNumber: 76
                }, this),
                " ",
                contact.owner_name || "N/A"
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 557,
                columnNumber: 13
              }, this),
              /* @__PURE__ */ jsxDEV("div", { className: "text-gray-500 dark:text-gray-400 text-xs", children: [
                /* @__PURE__ */ jsxDEV("span", { className: "font-semibold", children: "Created:" }, void 0, false, {
                  fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                  lineNumber: 558,
                  columnNumber: 71
                }, this),
                " ",
                contact.created_at?.slice(0, 10) || "N/A"
              ] }, void 0, true, {
                fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
                lineNumber: 558,
                columnNumber: 13
              }, this)
            ]
          },
          contact.id,
          true,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 515,
            columnNumber: 9
          },
          this
        )
      ),
      pagedContacts.length === 0 && /* @__PURE__ */ jsxDEV("div", { className: "text-center py-8 text-gray-400 dark:text-gray-600", children: "No contacts found." }, void 0, false, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 562,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 513,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV("div", { className: "flex justify-end items-center gap-2 mt-4", children: [
      /* @__PURE__ */ jsxDEV(
        "button",
        {
          className: "px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-300 font-semibold disabled:opacity-50",
          onClick: () => setPage((p) => Math.max(1, p - 1)),
          disabled: page === 1,
          children: "Prev"
        },
        void 0,
        false,
        {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 568,
          columnNumber: 9
        },
        this
      ),
      /* @__PURE__ */ jsxDEV("span", { className: "text-gray-700 dark:text-gray-200 text-sm", children: [
        "Page ",
        page,
        " of ",
        totalPages
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 575,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV(
        "button",
        {
          className: "px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-300 font-semibold disabled:opacity-50",
          onClick: () => setPage((p) => Math.min(totalPages, p + 1)),
          disabled: page === totalPages,
          children: "Next"
        },
        void 0,
        false,
        {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 578,
          columnNumber: 9
        },
        this
      )
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 567,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV(DetailModal, { open: !!detailContact, onClose: () => setDetailContact(null), title: "Contact Details", children: detailContact && /* @__PURE__ */ jsxDEV(Fragment, { children: [
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("b", { children: "Name:" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 591,
          columnNumber: 18
        }, this),
        " ",
        detailContact.name
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 591,
        columnNumber: 13
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("b", { children: "Email:" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 592,
          columnNumber: 18
        }, this),
        " ",
        detailContact.email
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 592,
        columnNumber: 13
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("b", { children: "Company:" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 593,
          columnNumber: 18
        }, this),
        " ",
        detailContact.company
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 593,
        columnNumber: 13
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("b", { children: "Owner:" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 594,
          columnNumber: 18
        }, this),
        " ",
        detailContact.owner_name || detailContact.owner
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 594,
        columnNumber: 13
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("b", { children: "Created:" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 595,
          columnNumber: 18
        }, this),
        " ",
        detailContact.created_at?.slice(0, 10) || detailContact.created
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 595,
        columnNumber: 13
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 590,
      columnNumber: 9
    }, this) }, void 0, false, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 588,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV(DetailModal, { open: confirmDeleteId !== null, onClose: cancelDelete, title: "Delete Contact?", children: [
      /* @__PURE__ */ jsxDEV("div", { children: "Are you sure you want to delete this contact?" }, void 0, false, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 602,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "flex gap-4 mt-6 justify-end", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition",
            onClick: cancelDelete,
            disabled: actionLoading,
            children: "Cancel"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 604,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition",
            onClick: confirmDelete,
            disabled: actionLoading,
            children: "Delete"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 611,
            columnNumber: 11
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 603,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 601,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV(DetailModal, { open: confirmBulkDelete, onClose: cancelBulkDelete, title: "Delete Multiple Contacts?", children: [
      /* @__PURE__ */ jsxDEV("div", { children: [
        "Are you sure you want to delete ",
        selected.length,
        " contacts? This action cannot be undone."
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 623,
        columnNumber: 9
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "flex gap-4 mt-6 justify-end", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition",
            onClick: cancelBulkDelete,
            disabled: actionLoading,
            children: "Cancel"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 625,
            columnNumber: 11
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-red-500 text-white font-semibold hover:bg-red-600 transition",
            onClick: deleteSelected,
            disabled: actionLoading,
            children: actionLoading ? "Deleting..." : "Delete All"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 632,
            columnNumber: 11
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 624,
        columnNumber: 9
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 622,
      columnNumber: 7
    }, this),
    /* @__PURE__ */ jsxDEV(DetailModal, { open: showCreateModal, onClose: () => setShowCreateModal(false), title: "Create New Contact", children: /* @__PURE__ */ jsxDEV("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Name *" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 646,
          columnNumber: 13
        }, this),
        /* @__PURE__ */ jsxDEV(
          "input",
          {
            type: "text",
            value: newContact.name,
            onChange: (e) => setNewContact({ ...newContact, name: e.target.value }),
            className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-pink-400",
            placeholder: "Enter contact name"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 649,
            columnNumber: 13
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 645,
        columnNumber: 11
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Email" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 658,
          columnNumber: 13
        }, this),
        /* @__PURE__ */ jsxDEV(
          "input",
          {
            type: "email",
            value: newContact.email,
            onChange: (e) => setNewContact({ ...newContact, email: e.target.value }),
            className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-pink-400",
            placeholder: "Enter email address"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 661,
            columnNumber: 13
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 657,
        columnNumber: 11
      }, this),
      /* @__PURE__ */ jsxDEV("div", { children: [
        /* @__PURE__ */ jsxDEV("label", { className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Company" }, void 0, false, {
          fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
          lineNumber: 670,
          columnNumber: 13
        }, this),
        /* @__PURE__ */ jsxDEV(
          "input",
          {
            type: "text",
            value: newContact.company,
            onChange: (e) => setNewContact({ ...newContact, company: e.target.value }),
            className: "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-pink-400",
            placeholder: "Enter company name"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 673,
            columnNumber: 13
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 669,
        columnNumber: 11
      }, this),
      /* @__PURE__ */ jsxDEV("div", { className: "flex gap-4 mt-6 justify-end", children: [
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold hover:bg-gray-300 dark:hover:bg-gray-700 transition",
            onClick: () => setShowCreateModal(false),
            disabled: actionLoading,
            children: "Cancel"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 682,
            columnNumber: 13
          },
          this
        ),
        /* @__PURE__ */ jsxDEV(
          "button",
          {
            className: "px-4 py-2 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 text-white font-semibold hover:from-pink-600 hover:to-purple-600 transition",
            onClick: handleCreateContact,
            disabled: actionLoading,
            children: actionLoading ? "Creating..." : "Create Contact"
          },
          void 0,
          false,
          {
            fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
            lineNumber: 689,
            columnNumber: 13
          },
          this
        )
      ] }, void 0, true, {
        fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
        lineNumber: 681,
        columnNumber: 11
      }, this)
    ] }, void 0, true, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 644,
      columnNumber: 9
    }, this) }, void 0, false, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 643,
      columnNumber: 7
    }, this),
    toast && /* @__PURE__ */ jsxDEV("div", { className: "fixed bottom-6 right-6 bg-green-600 text-white px-6 py-3 rounded-xl shadow-lg z-50 animate-fade-in", children: toast }, void 0, false, {
      fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
      lineNumber: 702,
      columnNumber: 7
    }, this)
  ] }, void 0, true, {
    fileName: "C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx",
    lineNumber: 288,
    columnNumber: 5
  }, this);
}
_s(ContactsNew, "3Zcup50P4C75T5CXvRT92r7dsLo=");
_c = ContactsNew;
var _c;
$RefreshReg$(_c, "ContactsNew");
if (import.meta.hot && !inWebWorker) {
  window.$RefreshReg$ = prevRefreshReg;
  window.$RefreshSig$ = prevRefreshSig;
}
if (import.meta.hot && !inWebWorker) {
  RefreshRuntime.__hmr_import(import.meta.url).then((currentExports) => {
    RefreshRuntime.registerExportsForReactRefresh("C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx", currentExports);
    import.meta.hot.accept((nextExports) => {
      if (!nextExports) return;
      const invalidateMessage = RefreshRuntime.validateRefreshBoundaryAndEnqueueUpdate("C:/Users/Khana/smart_crm/frontend/src/pages/Contacts.tsx", currentExports, nextExports);
      if (invalidateMessage) import.meta.hot.invalidate(invalidateMessage);
    });
  });
}

//# sourceMappingURL=data:application/json;base64,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O0FBQUEsV0FUcEM7QUFBQTtBQUFBO0FBQUE7QUFBQSxhQVdBO0FBQUEsTUFDQSx1QkFBQyxTQUFJLFdBQVUsK0JBQ2I7QUFBQTtBQUFBLFVBQUM7QUFBQTtBQUFBLFlBQ0MsV0FBVTtBQUFBLFlBQ1YsU0FBUyxNQUFNdEQsbUJBQW1CLEtBQUs7QUFBQSxZQUN2QyxVQUFVVDtBQUFBQSxZQUFjO0FBQUE7QUFBQSxVQUgxQjtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsUUFNQTtBQUFBLFFBQ0E7QUFBQSxVQUFDO0FBQUE7QUFBQSxZQUNDLFdBQVU7QUFBQSxZQUNWLFNBQVNvRztBQUFBQSxZQUNULFVBQVVwRztBQUFBQSxZQUVUQSwwQkFBZ0IsZ0JBQWdCO0FBQUE7QUFBQSxVQUxuQztBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUEsUUFNQTtBQUFBLFdBZEY7QUFBQTtBQUFBO0FBQUE7QUFBQSxhQWVBO0FBQUEsU0FwREY7QUFBQTtBQUFBO0FBQUE7QUFBQSxXQXFEQSxLQXRERjtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBdURBO0FBQUEsSUFHQ0UsU0FDQyx1QkFBQyxTQUFJLFdBQVUsc0dBQ1pBLG1CQURIO0FBQUE7QUFBQTtBQUFBO0FBQUEsV0FFQTtBQUFBLE9BaGFKO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FrYUE7QUFFSjtBQUFDMUIsR0E3cEJ1QkQsYUFBVztBQUFBeUksS0FBWHpJO0FBQVcsSUFBQXlJO0FBQUFDLGFBQUFELElBQUEiLCJuYW1lcyI6WyJ1c2VFZmZlY3QiLCJ1c2VTdGF0ZSIsIlNlYXJjaCIsIkV5ZSIsIkVkaXQiLCJUcmFzaDIiLCJDaGV2cm9uVXAiLCJDaGV2cm9uRG93biIsIkRvd25sb2FkIiwiUGx1cyIsIlhMU1giLCJmZXRjaENvbnRhY3RzIiwiZ2V0Q29udGFjdCIsInVwZGF0ZUNvbnRhY3QiLCJkZWxldGVDb250YWN0IiwiY3JlYXRlQ29udGFjdCIsIkRldGFpbE1vZGFsIiwiY29sdW1ucyIsImtleSIsImxhYmVsIiwiQ29udGFjdHNOZXciLCJfcyIsImNvbnRhY3RzIiwic2V0Q29udGFjdHMiLCJsb2FkaW5nIiwic2V0TG9hZGluZyIsImVycm9yIiwic2V0RXJyb3IiLCJzZWFyY2giLCJzZXRTZWFyY2giLCJkZXRhaWxDb250YWN0Iiwic2V0RGV0YWlsQ29udGFjdCIsInNvcnRCeSIsInNldFNvcnRCeSIsInNvcnREaXIiLCJzZXRTb3J0RGlyIiwicGFnZSIsInNldFBhZ2UiLCJzZWxlY3RlZCIsInNldFNlbGVjdGVkIiwiZWRpdGluZ0NlbGwiLCJzZXRFZGl0aW5nQ2VsbCIsImVkaXRDZWxsVmFsdWUiLCJzZXRFZGl0Q2VsbFZhbHVlIiwicGFnZVNpemUiLCJhY3Rpb25Mb2FkaW5nIiwic2V0QWN0aW9uTG9hZGluZyIsInRvYXN0Iiwic2V0VG9hc3QiLCJjb25maXJtRGVsZXRlSWQiLCJzZXRDb25maXJtRGVsZXRlSWQiLCJjb25maXJtQnVsa0RlbGV0ZSIsInNldENvbmZpcm1CdWxrRGVsZXRlIiwic2hvd0NyZWF0ZU1vZGFsIiwic2V0U2hvd0NyZWF0ZU1vZGFsIiwibmV3Q29udGFjdCIsInNldE5ld0NvbnRhY3QiLCJuYW1lIiwiZW1haWwiLCJjb21wYW55IiwiY29uc29sZSIsImxvZyIsInRoZW4iLCJkYXRhIiwibGVuZ3RoIiwiY2F0Y2giLCJlcnIiLCJjb250YWN0c1RvRGlzcGxheSIsImZpbHRlciIsImNvbnRhY3QiLCJtYXRjaGVzU2VhcmNoIiwidG9Mb3dlckNhc2UiLCJpbmNsdWRlcyIsInNvcnQiLCJhIiwiYiIsImFWYWwiLCJiVmFsIiwiRGF0ZSIsInRvdGFsUGFnZXMiLCJNYXRoIiwiY2VpbCIsInBhZ2VkQ29udGFjdHMiLCJzbGljZSIsImhhbmRsZVNvcnQiLCJjb2wiLCJhbGxTZWxlY3RlZCIsImV2ZXJ5IiwiaWQiLCJzb21lU2VsZWN0ZWQiLCJzb21lIiwidG9nZ2xlQWxsIiwibCIsIm1hcCIsInRvZ2dsZU9uZSIsImkiLCJjbGVhclNlbGVjdGVkIiwiY29uZmlybUJ1bGtEZWxldGVBY3Rpb24iLCJjYW5jZWxCdWxrRGVsZXRlIiwiZGVsZXRlU2VsZWN0ZWQiLCJkZWxldGVQcm9taXNlcyIsIlByb21pc2UiLCJhbGwiLCJzZXRUaW1lb3V0IiwiZSIsImFsZXJ0Iiwic3RhcnRFZGl0Q2VsbCIsImZpZWxkIiwidmFsdWUiLCJzYXZlRWRpdENlbGwiLCJoYW5kbGVFZGl0Q2VsbEtleSIsImV4cG9ydENTViIsImhlYWRlcnMiLCJyb3dzIiwib3duZXJfbmFtZSIsImNyZWF0ZWRfYXQiLCJjc3ZDb250ZW50Iiwicm93IiwiU3RyaW5nIiwicmVwbGFjZSIsImpvaW4iLCJibG9iIiwiQmxvYiIsInR5cGUiLCJ1cmwiLCJVUkwiLCJjcmVhdGVPYmplY3RVUkwiLCJkb2N1bWVudCIsImNyZWF0ZUVsZW1lbnQiLCJocmVmIiwiZG93bmxvYWQiLCJjbGljayIsInJldm9rZU9iamVjdFVSTCIsImV4cG9ydEV4Y2VsIiwid3MiLCJ1dGlscyIsImFvYV90b19zaGVldCIsIndiIiwiYm9va19uZXciLCJib29rX2FwcGVuZF9zaGVldCIsIndyaXRlRmlsZSIsImhhbmRsZVZpZXciLCJoYW5kbGVEZWxldGUiLCJjb25maXJtRGVsZXRlIiwiY2FuY2VsRGVsZXRlIiwiaGFuZGxlQ3JlYXRlQ29udGFjdCIsInRyaW0iLCJjcmVhdGVkQ29udGFjdCIsInRhcmdldCIsImVsIiwiaW5kZXRlcm1pbmF0ZSIsImNvbnRhY3RfbmFtZSIsInAiLCJtYXgiLCJtaW4iLCJvd25lciIsImNyZWF0ZWQiLCJfYyIsIiRSZWZyZXNoUmVnJCJdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlcyI6WyJDb250YWN0cy50c3giXSwic291cmNlc0NvbnRlbnQiOlsi77u/LyoqXHJcbiAqIENvbnRhY3RzIHBhZ2U6IEZ1bGwgZnVuY3Rpb25hbGl0eSB3aXRob3V0IHN0YXR1c1xyXG4gKiAtIE5PIFNUQVRVUyBGSUxURVIgLSBDb250YWN0cyBkb24ndCBoYXZlIHN0YXR1cyBmaWVsZFxyXG4gKiAtIEZVTEwgRlVOQ1RJT05BTElUWTogc2VhcmNoLCBzb3J0LCBwYWdpbmF0aW9uLCBhY3Rpb25zXHJcbiAqL1xyXG5pbXBvcnQgeyB1c2VFZmZlY3QsIHVzZVN0YXRlIH0gZnJvbSBcInJlYWN0XCI7XHJcbmltcG9ydCB7IFNlYXJjaCwgRXllLCBFZGl0LCBUcmFzaDIsIENoZXZyb25VcCwgQ2hldnJvbkRvd24sIERvd25sb2FkLCBQbHVzIH0gZnJvbSBcImx1Y2lkZS1yZWFjdFwiO1xyXG5pbXBvcnQgKiBhcyBYTFNYIGZyb20gXCJ4bHN4XCI7XHJcbmltcG9ydCB7IGZldGNoQ29udGFjdHMsIGdldENvbnRhY3QsIHVwZGF0ZUNvbnRhY3QsIGRlbGV0ZUNvbnRhY3QsIGNyZWF0ZUNvbnRhY3QgfSBmcm9tIFwiLi4vc2VydmljZXMvY29udGFjdHNcIjtcclxuaW1wb3J0IERldGFpbE1vZGFsIGZyb20gXCIuLi9jb21wb25lbnRzL0RldGFpbE1vZGFsXCI7XHJcblxyXG5jb25zdCBjb2x1bW5zID0gW1xyXG4gIHsga2V5OiBcIm5hbWVcIiwgbGFiZWw6IFwiTmFtZVwiIH0sXHJcbiAgeyBrZXk6IFwiZW1haWxcIiwgbGFiZWw6IFwiRW1haWxcIiB9LFxyXG4gIHsga2V5OiBcImNvbXBhbnlcIiwgbGFiZWw6IFwiQ29tcGFueVwiIH0sXHJcbiAgeyBrZXk6IFwib3duZXJfbmFtZVwiLCBsYWJlbDogXCJPd25lclwiIH0sXHJcbiAgeyBrZXk6IFwiY3JlYXRlZF9hdFwiLCBsYWJlbDogXCJDcmVhdGVkXCIgfSxcclxuXTtcclxuXHJcbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIENvbnRhY3RzTmV3KCkge1xyXG4gIGNvbnN0IFtjb250YWN0cywgc2V0Q29udGFjdHNdID0gdXNlU3RhdGU8YW55W10+KFtdKTtcclxuICBcclxuICBjb25zdCBbbG9hZGluZywgc2V0TG9hZGluZ10gPSB1c2VTdGF0ZSh0cnVlKTtcclxuICBjb25zdCBbZXJyb3IsIHNldEVycm9yXSA9IHVzZVN0YXRlPHN0cmluZyB8IG51bGw+KG51bGwpO1xyXG4gIGNvbnN0IFtzZWFyY2gsIHNldFNlYXJjaF0gPSB1c2VTdGF0ZShcIlwiKTtcclxuICBjb25zdCBbZGV0YWlsQ29udGFjdCwgc2V0RGV0YWlsQ29udGFjdF0gPSB1c2VTdGF0ZTxhbnkgfCBudWxsPihudWxsKTtcclxuICBjb25zdCBbc29ydEJ5LCBzZXRTb3J0QnldID0gdXNlU3RhdGU8c3RyaW5nPihcImNyZWF0ZWRfYXRcIik7XHJcbiAgY29uc3QgW3NvcnREaXIsIHNldFNvcnREaXJdID0gdXNlU3RhdGU8XCJhc2NcIiB8IFwiZGVzY1wiPihcImRlc2NcIik7XHJcbiAgY29uc3QgW3BhZ2UsIHNldFBhZ2VdID0gdXNlU3RhdGUoMSk7XHJcbiAgY29uc3QgW3NlbGVjdGVkLCBzZXRTZWxlY3RlZF0gPSB1c2VTdGF0ZTxudW1iZXJbXT4oW10pO1xyXG4gIGNvbnN0IFtlZGl0aW5nQ2VsbCwgc2V0RWRpdGluZ0NlbGxdID0gdXNlU3RhdGU8eyBpZDogbnVtYmVyOyBmaWVsZDogc3RyaW5nIH0gfCBudWxsPihudWxsKTtcclxuICBjb25zdCBbZWRpdENlbGxWYWx1ZSwgc2V0RWRpdENlbGxWYWx1ZV0gPSB1c2VTdGF0ZShcIlwiKTtcclxuICBjb25zdCBwYWdlU2l6ZSA9IDEwO1xyXG4gIGNvbnN0IFthY3Rpb25Mb2FkaW5nLCBzZXRBY3Rpb25Mb2FkaW5nXSA9IHVzZVN0YXRlKGZhbHNlKTtcclxuICBjb25zdCBbdG9hc3QsIHNldFRvYXN0XSA9IHVzZVN0YXRlPHN0cmluZyB8IG51bGw+KG51bGwpO1xyXG4gIGNvbnN0IFtjb25maXJtRGVsZXRlSWQsIHNldENvbmZpcm1EZWxldGVJZF0gPSB1c2VTdGF0ZTxudW1iZXIgfCBudWxsPihudWxsKTtcclxuICBjb25zdCBbY29uZmlybUJ1bGtEZWxldGUsIHNldENvbmZpcm1CdWxrRGVsZXRlXSA9IHVzZVN0YXRlKGZhbHNlKTtcclxuICBjb25zdCBbc2hvd0NyZWF0ZU1vZGFsLCBzZXRTaG93Q3JlYXRlTW9kYWxdID0gdXNlU3RhdGUoZmFsc2UpO1xyXG4gIGNvbnN0IFtuZXdDb250YWN0LCBzZXROZXdDb250YWN0XSA9IHVzZVN0YXRlKHtcclxuICAgIG5hbWU6IFwiXCIsXHJcbiAgICBlbWFpbDogXCJcIixcclxuICAgIGNvbXBhbnk6IFwiXCJcclxuICB9KTtcclxuXHJcbiAgdXNlRWZmZWN0KCgpID0+IHtcclxuICAgIGNvbnNvbGUubG9nKCdDb250YWN0c05ldyBwYWdlIGxvYWRpbmcuLi4gLSBGVUxMIEZVTkNUSU9OQUxJVFknKTtcclxuICAgIGZldGNoQ29udGFjdHMoKVxyXG4gICAgICAudGhlbihkYXRhID0+IHtcclxuICAgICAgICBjb25zb2xlLmxvZygnQ29udGFjdHMgbG9hZGVkIHN1Y2Nlc3NmdWxseTonLCBkYXRhLmxlbmd0aCwgJ2NvbnRhY3RzJyk7XHJcbiAgICAgICAgc2V0Q29udGFjdHMoZGF0YSk7XHJcbiAgICAgICAgc2V0TG9hZGluZyhmYWxzZSk7XHJcbiAgICAgIH0pXHJcbiAgICAgIC5jYXRjaChlcnIgPT4ge1xyXG4gICAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBsb2FkIGNvbnRhY3RzOicsIGVycik7XHJcbiAgICAgICAgc2V0RXJyb3IoXCJGYWlsZWQgdG8gbG9hZCBjb250YWN0c1wiKTtcclxuICAgICAgICBzZXRMb2FkaW5nKGZhbHNlKTtcclxuICAgICAgfSk7XHJcbiAgfSwgW10pO1xyXG5cclxuICBpZiAobG9hZGluZykgcmV0dXJuIDxkaXYgY2xhc3NOYW1lPVwicC04IHRleHQtbGdcIj5Mb2FkaW5nLi4uPC9kaXY+O1xyXG4gIGlmIChlcnJvcikgcmV0dXJuIDxkaXYgY2xhc3NOYW1lPVwicC04IHRleHQtcmVkLTUwMFwiPntlcnJvcn08L2Rpdj47XHJcblxyXG4gIC8vIEZpbHRlcmVkIGFuZCBzb3J0ZWQgY29udGFjdHNcclxuICBsZXQgY29udGFjdHNUb0Rpc3BsYXkgPSBjb250YWN0cy5maWx0ZXIoXHJcbiAgICAoY29udGFjdCkgPT4ge1xyXG4gICAgICBjb25zdCBtYXRjaGVzU2VhcmNoID0gIXNlYXJjaCB8fCBcclxuICAgICAgICBjb250YWN0Lm5hbWU/LnRvTG93ZXJDYXNlKCkuaW5jbHVkZXMoc2VhcmNoLnRvTG93ZXJDYXNlKCkpIHx8IFxyXG4gICAgICAgIGNvbnRhY3QuY29tcGFueT8udG9Mb3dlckNhc2UoKS5pbmNsdWRlcyhzZWFyY2gudG9Mb3dlckNhc2UoKSkgfHwgXHJcbiAgICAgICAgY29udGFjdC5lbWFpbD8udG9Mb3dlckNhc2UoKS5pbmNsdWRlcyhzZWFyY2gudG9Mb3dlckNhc2UoKSk7XHJcbiAgICAgIFxyXG4gICAgICByZXR1cm4gbWF0Y2hlc1NlYXJjaDtcclxuICAgIH1cclxuICApO1xyXG4gIGNvbnRhY3RzVG9EaXNwbGF5ID0gY29udGFjdHNUb0Rpc3BsYXkuc29ydCgoYSwgYikgPT4ge1xyXG4gICAgbGV0IGFWYWwgPSAoYSBhcyBhbnkpW3NvcnRCeV07XHJcbiAgICBsZXQgYlZhbCA9IChiIGFzIGFueSlbc29ydEJ5XTtcclxuICAgIFxyXG4gICAgLy8gSGFuZGxlIGRhdGUgc29ydGluZ1xyXG4gICAgaWYgKHNvcnRCeSA9PT0gJ2NyZWF0ZWRfYXQnKSB7XHJcbiAgICAgIGFWYWwgPSBuZXcgRGF0ZShhVmFsIHx8IDApO1xyXG4gICAgICBiVmFsID0gbmV3IERhdGUoYlZhbCB8fCAwKTtcclxuICAgIH1cclxuICAgIFxyXG4gICAgLy8gSGFuZGxlIG51bGwvdW5kZWZpbmVkIHZhbHVlc1xyXG4gICAgaWYgKCFhVmFsICYmICFiVmFsKSByZXR1cm4gMDtcclxuICAgIGlmICghYVZhbCkgcmV0dXJuIHNvcnREaXIgPT09IFwiYXNjXCIgPyAtMSA6IDE7XHJcbiAgICBpZiAoIWJWYWwpIHJldHVybiBzb3J0RGlyID09PSBcImFzY1wiID8gMSA6IC0xO1xyXG4gICAgXHJcbiAgICBpZiAoYVZhbCA8IGJWYWwpIHJldHVybiBzb3J0RGlyID09PSBcImFzY1wiID8gLTEgOiAxO1xyXG4gICAgaWYgKGFWYWwgPiBiVmFsKSByZXR1cm4gc29ydERpciA9PT0gXCJhc2NcIiA/IDEgOiAtMTtcclxuICAgIHJldHVybiAwO1xyXG4gIH0pO1xyXG5cclxuICAvLyBQYWdpbmF0aW9uXHJcbiAgY29uc3QgdG90YWxQYWdlcyA9IE1hdGguY2VpbChjb250YWN0c1RvRGlzcGxheS5sZW5ndGggLyBwYWdlU2l6ZSk7XHJcbiAgY29uc3QgcGFnZWRDb250YWN0cyA9IGNvbnRhY3RzVG9EaXNwbGF5LnNsaWNlKChwYWdlIC0gMSkgKiBwYWdlU2l6ZSwgcGFnZSAqIHBhZ2VTaXplKTtcclxuXHJcbiAgLy8gSGFuZGxlIGNvbHVtbiBzb3J0XHJcbiAgY29uc3QgaGFuZGxlU29ydCA9IChjb2w6IHN0cmluZykgPT4ge1xyXG4gICAgaWYgKHNvcnRCeSA9PT0gY29sKSB7XHJcbiAgICAgIHNldFNvcnREaXIoc29ydERpciA9PT0gXCJhc2NcIiA/IFwiZGVzY1wiIDogXCJhc2NcIik7XHJcbiAgICB9IGVsc2Uge1xyXG4gICAgICBzZXRTb3J0QnkoY29sKTtcclxuICAgICAgc2V0U29ydERpcihcImFzY1wiKTtcclxuICAgIH1cclxuICAgIHNldFBhZ2UoMSk7XHJcbiAgfTtcclxuXHJcbiAgLy8gQnVsayBzZWxlY3Rpb24gbG9naWNcclxuICBjb25zdCBhbGxTZWxlY3RlZCA9IHBhZ2VkQ29udGFjdHMubGVuZ3RoID4gMCAmJiBwYWdlZENvbnRhY3RzLmV2ZXJ5KChjb250YWN0KSA9PiBzZWxlY3RlZC5pbmNsdWRlcyhjb250YWN0LmlkKSk7XHJcbiAgY29uc3Qgc29tZVNlbGVjdGVkID0gcGFnZWRDb250YWN0cy5zb21lKChjb250YWN0KSA9PiBzZWxlY3RlZC5pbmNsdWRlcyhjb250YWN0LmlkKSk7XHJcbiAgY29uc3QgdG9nZ2xlQWxsID0gKCkgPT4ge1xyXG4gICAgaWYgKGFsbFNlbGVjdGVkKSB7XHJcbiAgICAgIHNldFNlbGVjdGVkKHNlbGVjdGVkLmZpbHRlcihpZCA9PiAhcGFnZWRDb250YWN0cy5zb21lKGwgPT4gbC5pZCA9PT0gaWQpKSk7XHJcbiAgICB9IGVsc2Uge1xyXG4gICAgICBzZXRTZWxlY3RlZChbLi4uc2VsZWN0ZWQsIC4uLnBhZ2VkQ29udGFjdHMuZmlsdGVyKGwgPT4gIXNlbGVjdGVkLmluY2x1ZGVzKGwuaWQpKS5tYXAobCA9PiBsLmlkKV0pO1xyXG4gICAgfVxyXG4gIH07XHJcbiAgY29uc3QgdG9nZ2xlT25lID0gKGlkOiBudW1iZXIpID0+IHtcclxuICAgIHNldFNlbGVjdGVkKHNlbGVjdGVkLmluY2x1ZGVzKGlkKSA/IHNlbGVjdGVkLmZpbHRlcihpID0+IGkgIT09IGlkKSA6IFsuLi5zZWxlY3RlZCwgaWRdKTtcclxuICB9O1xyXG4gIGNvbnN0IGNsZWFyU2VsZWN0ZWQgPSAoKSA9PiBzZXRTZWxlY3RlZChbXSk7XHJcbiAgY29uc3QgY29uZmlybUJ1bGtEZWxldGVBY3Rpb24gPSAoKSA9PiB7XHJcbiAgICBzZXRDb25maXJtQnVsa0RlbGV0ZSh0cnVlKTtcclxuICB9O1xyXG4gIFxyXG4gIGNvbnN0IGNhbmNlbEJ1bGtEZWxldGUgPSAoKSA9PiB7XHJcbiAgICBzZXRDb25maXJtQnVsa0RlbGV0ZShmYWxzZSk7XHJcbiAgfTtcclxuICBcclxuICBjb25zdCBkZWxldGVTZWxlY3RlZCA9IGFzeW5jICgpID0+IHtcclxuICAgIGlmIChzZWxlY3RlZC5sZW5ndGggPT09IDApIHJldHVybjtcclxuICAgIFxyXG4gICAgc2V0QWN0aW9uTG9hZGluZyh0cnVlKTtcclxuICAgIHRyeSB7XHJcbiAgICAgIGNvbnN0IGRlbGV0ZVByb21pc2VzID0gc2VsZWN0ZWQubWFwKGlkID0+IGRlbGV0ZUNvbnRhY3QoaWQpKTtcclxuICAgICAgYXdhaXQgUHJvbWlzZS5hbGwoZGVsZXRlUHJvbWlzZXMpO1xyXG4gICAgICBhd2FpdCBmZXRjaENvbnRhY3RzKCkudGhlbihzZXRDb250YWN0cyk7XHJcbiAgICAgIHNldFRvYXN0KGBTdWNjZXNzZnVsbHkgZGVsZXRlZCAke3NlbGVjdGVkLmxlbmd0aH0gY29udGFjdHNgKTtcclxuICAgICAgc2V0VGltZW91dCgoKSA9PiBzZXRUb2FzdChudWxsKSwgMjAwMCk7XHJcbiAgICAgIGNsZWFyU2VsZWN0ZWQoKTtcclxuICAgIH0gY2F0Y2ggKGUpIHtcclxuICAgICAgYWxlcnQoXCJGYWlsZWQgdG8gZGVsZXRlIHNlbGVjdGVkIGNvbnRhY3RzXCIpO1xyXG4gICAgfVxyXG4gICAgc2V0QWN0aW9uTG9hZGluZyhmYWxzZSk7XHJcbiAgICBzZXRDb25maXJtQnVsa0RlbGV0ZShmYWxzZSk7XHJcbiAgfTtcclxuXHJcbiAgLy8gQ2VsbCBlZGl0aW5nIGxvZ2ljXHJcbiAgY29uc3Qgc3RhcnRFZGl0Q2VsbCA9IChpZDogbnVtYmVyLCBmaWVsZDogc3RyaW5nLCB2YWx1ZTogc3RyaW5nKSA9PiB7XHJcbiAgICBzZXRFZGl0aW5nQ2VsbCh7IGlkLCBmaWVsZCB9KTtcclxuICAgIHNldEVkaXRDZWxsVmFsdWUodmFsdWUpO1xyXG4gIH07XHJcbiAgY29uc3Qgc2F2ZUVkaXRDZWxsID0gYXN5bmMgKGlkOiBudW1iZXIsIGZpZWxkOiBzdHJpbmcpID0+IHtcclxuICAgIHNldEFjdGlvbkxvYWRpbmcodHJ1ZSk7XHJcbiAgICB0cnkge1xyXG4gICAgICBhd2FpdCB1cGRhdGVDb250YWN0KGlkLCB7IFtmaWVsZF06IGVkaXRDZWxsVmFsdWUgfSk7XHJcbiAgICAgIGF3YWl0IGZldGNoQ29udGFjdHMoKS50aGVuKHNldENvbnRhY3RzKTtcclxuICAgICAgc2V0VG9hc3QoXCJDb250YWN0IHVwZGF0ZWQhXCIpO1xyXG4gICAgICBzZXRUaW1lb3V0KCgpID0+IHNldFRvYXN0KG51bGwpLCAyMDAwKTtcclxuICAgIH0gY2F0Y2ggKGUpIHtcclxuICAgICAgYWxlcnQoXCJGYWlsZWQgdG8gdXBkYXRlIGNvbnRhY3RcIik7XHJcbiAgICB9XHJcbiAgICBzZXRBY3Rpb25Mb2FkaW5nKGZhbHNlKTtcclxuICAgIHNldEVkaXRpbmdDZWxsKG51bGwpO1xyXG4gICAgc2V0RWRpdENlbGxWYWx1ZShcIlwiKTtcclxuICB9O1xyXG4gIGNvbnN0IGhhbmRsZUVkaXRDZWxsS2V5ID0gKGU6IFJlYWN0LktleWJvYXJkRXZlbnQsIGlkOiBudW1iZXIsIGZpZWxkOiBzdHJpbmcpID0+IHtcclxuICAgIGlmIChlLmtleSA9PT0gXCJFbnRlclwiKSB7XHJcbiAgICAgIHNhdmVFZGl0Q2VsbChpZCwgZmllbGQpO1xyXG4gICAgfSBlbHNlIGlmIChlLmtleSA9PT0gXCJFc2NhcGVcIikge1xyXG4gICAgICBzZXRFZGl0aW5nQ2VsbChudWxsKTtcclxuICAgICAgc2V0RWRpdENlbGxWYWx1ZShcIlwiKTtcclxuICAgIH1cclxuICB9O1xyXG5cclxuICAvLyBFeHBvcnQgZnVuY3Rpb25zXHJcbiAgZnVuY3Rpb24gZXhwb3J0Q1NWKCkge1xyXG4gICAgY29uc3QgaGVhZGVycyA9IFtcIk5hbWVcIiwgXCJFbWFpbFwiLCBcIkNvbXBhbnlcIiwgXCJPd25lclwiLCBcIkNyZWF0ZWRcIl07XHJcbiAgICBjb25zdCByb3dzID0gY29udGFjdHNUb0Rpc3BsYXkubWFwKGNvbnRhY3QgPT4gW1xyXG4gICAgICBjb250YWN0Lm5hbWUsXHJcbiAgICAgIGNvbnRhY3QuZW1haWwsXHJcbiAgICAgIGNvbnRhY3QuY29tcGFueSxcclxuICAgICAgY29udGFjdC5vd25lcl9uYW1lLFxyXG4gICAgICBjb250YWN0LmNyZWF0ZWRfYXQ/LnNsaWNlKDAsIDEwKSB8fCBcIlwiLFxyXG4gICAgXSk7XHJcbiAgICBjb25zdCBjc3ZDb250ZW50ID1cclxuICAgICAgW2hlYWRlcnMsIC4uLnJvd3NdXHJcbiAgICAgICAgLm1hcChyb3cgPT4gcm93Lm1hcChmaWVsZCA9PiBgXCIke1N0cmluZyhmaWVsZCkucmVwbGFjZSgvXCIvZywgJ1wiXCInKX1cImApLmpvaW4oXCIsXCIpKVxyXG4gICAgICAgIC5qb2luKFwiXFxuXCIpO1xyXG4gICAgY29uc3QgYmxvYiA9IG5ldyBCbG9iKFtjc3ZDb250ZW50XSwgeyB0eXBlOiBcInRleHQvY3N2XCIgfSk7XHJcbiAgICBjb25zdCB1cmwgPSBVUkwuY3JlYXRlT2JqZWN0VVJMKGJsb2IpO1xyXG4gICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoXCJhXCIpO1xyXG4gICAgYS5ocmVmID0gdXJsO1xyXG4gICAgYS5kb3dubG9hZCA9IFwiY29udGFjdHMuY3N2XCI7XHJcbiAgICBhLmNsaWNrKCk7XHJcbiAgICBVUkwucmV2b2tlT2JqZWN0VVJMKHVybCk7XHJcbiAgfVxyXG5cclxuICBmdW5jdGlvbiBleHBvcnRFeGNlbCgpIHtcclxuICAgIGNvbnN0IGhlYWRlcnMgPSBbXCJOYW1lXCIsIFwiRW1haWxcIiwgXCJDb21wYW55XCIsIFwiT3duZXJcIiwgXCJDcmVhdGVkXCJdO1xyXG4gICAgY29uc3Qgcm93cyA9IGNvbnRhY3RzVG9EaXNwbGF5Lm1hcChjb250YWN0ID0+IFtcclxuICAgICAgY29udGFjdC5uYW1lLFxyXG4gICAgICBjb250YWN0LmVtYWlsLFxyXG4gICAgICBjb250YWN0LmNvbXBhbnksXHJcbiAgICAgIGNvbnRhY3Qub3duZXJfbmFtZSxcclxuICAgICAgY29udGFjdC5jcmVhdGVkX2F0Py5zbGljZSgwLCAxMCkgfHwgXCJcIixcclxuICAgIF0pO1xyXG4gICAgY29uc3Qgd3MgPSBYTFNYLnV0aWxzLmFvYV90b19zaGVldChbaGVhZGVycywgLi4ucm93c10pO1xyXG4gICAgY29uc3Qgd2IgPSBYTFNYLnV0aWxzLmJvb2tfbmV3KCk7XHJcbiAgICBYTFNYLnV0aWxzLmJvb2tfYXBwZW5kX3NoZWV0KHdiLCB3cywgXCJDb250YWN0c1wiKTtcclxuICAgIFhMU1gud3JpdGVGaWxlKHdiLCBcImNvbnRhY3RzLnhsc3hcIik7XHJcbiAgfVxyXG5cclxuICAvLyBBY3Rpb24gaGFuZGxlcnNcclxuICBjb25zdCBoYW5kbGVWaWV3ID0gYXN5bmMgKGlkOiBudW1iZXIpID0+IHtcclxuICAgIHNldEFjdGlvbkxvYWRpbmcodHJ1ZSk7XHJcbiAgICB0cnkge1xyXG4gICAgICBjb25zdCBjb250YWN0ID0gYXdhaXQgZ2V0Q29udGFjdChpZCk7XHJcbiAgICAgIHNldERldGFpbENvbnRhY3QoY29udGFjdCk7XHJcbiAgICB9IGNhdGNoIChlKSB7XHJcbiAgICAgIGFsZXJ0KFwiRmFpbGVkIHRvIGZldGNoIGNvbnRhY3QgZGV0YWlsc1wiKTtcclxuICAgIH1cclxuICAgIHNldEFjdGlvbkxvYWRpbmcoZmFsc2UpO1xyXG4gIH07XHJcblxyXG4gIGNvbnN0IGhhbmRsZURlbGV0ZSA9IGFzeW5jIChpZDogbnVtYmVyKSA9PiB7XHJcbiAgICBzZXRDb25maXJtRGVsZXRlSWQoaWQpO1xyXG4gIH07XHJcblxyXG4gIGNvbnN0IGNvbmZpcm1EZWxldGUgPSBhc3luYyAoKSA9PiB7XHJcbiAgICBpZiAoY29uZmlybURlbGV0ZUlkID09PSBudWxsKSByZXR1cm47XHJcbiAgICBzZXRBY3Rpb25Mb2FkaW5nKHRydWUpO1xyXG4gICAgdHJ5IHtcclxuICAgICAgYXdhaXQgZGVsZXRlQ29udGFjdChjb25maXJtRGVsZXRlSWQpO1xyXG4gICAgICBmZXRjaENvbnRhY3RzKCkudGhlbihzZXRDb250YWN0cyk7XHJcbiAgICAgIHNldFRvYXN0KFwiQ29udGFjdCBkZWxldGVkIVwiKTtcclxuICAgICAgc2V0VGltZW91dCgoKSA9PiBzZXRUb2FzdChudWxsKSwgMjAwMCk7XHJcbiAgICB9IGNhdGNoIChlKSB7XHJcbiAgICAgIGFsZXJ0KFwiRmFpbGVkIHRvIGRlbGV0ZSBjb250YWN0XCIpO1xyXG4gICAgfVxyXG4gICAgc2V0QWN0aW9uTG9hZGluZyhmYWxzZSk7XHJcbiAgICBzZXRDb25maXJtRGVsZXRlSWQobnVsbCk7XHJcbiAgfTtcclxuXHJcbiAgY29uc3QgY2FuY2VsRGVsZXRlID0gKCkgPT4gc2V0Q29uZmlybURlbGV0ZUlkKG51bGwpO1xyXG5cclxuICBjb25zdCBoYW5kbGVDcmVhdGVDb250YWN0ID0gYXN5bmMgKCkgPT4ge1xyXG4gICAgaWYgKCFuZXdDb250YWN0Lm5hbWUudHJpbSgpKSB7XHJcbiAgICAgIHNldFRvYXN0KFwiTmFtZSBpcyByZXF1aXJlZFwiKTtcclxuICAgICAgcmV0dXJuO1xyXG4gICAgfVxyXG4gICAgXHJcbiAgICBzZXRBY3Rpb25Mb2FkaW5nKHRydWUpO1xyXG4gICAgdHJ5IHtcclxuICAgICAgY29uc3QgY3JlYXRlZENvbnRhY3QgPSBhd2FpdCBjcmVhdGVDb250YWN0KG5ld0NvbnRhY3QpO1xyXG4gICAgICBzZXRDb250YWN0cyhbLi4uY29udGFjdHMsIGNyZWF0ZWRDb250YWN0XSk7XHJcbiAgICAgIHNldFNob3dDcmVhdGVNb2RhbChmYWxzZSk7XHJcbiAgICAgIHNldE5ld0NvbnRhY3QoeyBuYW1lOiBcIlwiLCBlbWFpbDogXCJcIiwgY29tcGFueTogXCJcIiB9KTtcclxuICAgICAgc2V0VG9hc3QoXCJDb250YWN0IGNyZWF0ZWQgc3VjY2Vzc2Z1bGx5IVwiKTtcclxuICAgIH0gY2F0Y2ggKGVycm9yKSB7XHJcbiAgICAgIHNldFRvYXN0KFwiRmFpbGVkIHRvIGNyZWF0ZSBjb250YWN0XCIpO1xyXG4gICAgfSBmaW5hbGx5IHtcclxuICAgICAgc2V0QWN0aW9uTG9hZGluZyhmYWxzZSk7XHJcbiAgICB9XHJcbiAgfTtcclxuXHJcbiAgcmV0dXJuIChcclxuICAgIDxkaXYgY2xhc3NOYW1lPVwicC0yIG1kOnAtNlwiPlxyXG4gICAgICB7LyogQnVsayBBY3Rpb24gQmFyICovfVxyXG4gICAgICB7c2VsZWN0ZWQubGVuZ3RoID4gMCAmJiAoXHJcbiAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWJldHdlZW4gYmctcGluay01MCBkYXJrOmJnLXBpbmstOTAwLzMwIGJvcmRlciBib3JkZXItcGluay0yMDAgZGFyazpib3JkZXItcGluay04MDAgcm91bmRlZC14bCBweC00IHB5LTIgbWItNCBzaGFkb3cgYW5pbWF0ZS1mYWRlLWluXCI+XHJcbiAgICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0ZXh0LXBpbmstNzAwIGRhcms6dGV4dC1waW5rLTIwMCBmb250LXNlbWlib2xkXCI+e3NlbGVjdGVkLmxlbmd0aH0gc2VsZWN0ZWQ8L3NwYW4+XHJcbiAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImZsZXggZ2FwLTJcIj5cclxuICAgICAgICAgICAgPGJ1dHRvblxyXG4gICAgICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTQgcHktMSByb3VuZGVkLWZ1bGwgYmctcmVkLTUwMCB0ZXh0LXdoaXRlIGZvbnQtc2VtaWJvbGQgaG92ZXI6YmctcmVkLTYwMCB0cmFuc2l0aW9uIGRpc2FibGVkOm9wYWNpdHktNTAgZGlzYWJsZWQ6Y3Vyc29yLW5vdC1hbGxvd2VkXCJcclxuICAgICAgICAgICAgICBvbkNsaWNrPXtjb25maXJtQnVsa0RlbGV0ZUFjdGlvbn1cclxuICAgICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgIERlbGV0ZSBTZWxlY3RlZFxyXG4gICAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgICAgPGJ1dHRvblxyXG4gICAgICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTQgcHktMSByb3VuZGVkLWZ1bGwgYmctZ3JheS0yMDAgZGFyazpiZy1ncmF5LTgwMCB0ZXh0LWdyYXktNzAwIGRhcms6dGV4dC1ncmF5LTIwMCBmb250LXNlbWlib2xkIGhvdmVyOmJnLWdyYXktMzAwIGRhcms6aG92ZXI6YmctZ3JheS03MDAgdHJhbnNpdGlvbiBkaXNhYmxlZDpvcGFjaXR5LTUwIGRpc2FibGVkOmN1cnNvci1ub3QtYWxsb3dlZFwiXHJcbiAgICAgICAgICAgICAgb25DbGljaz17Y2xlYXJTZWxlY3RlZH1cclxuICAgICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgIENsZWFyXHJcbiAgICAgICAgICAgIDwvYnV0dG9uPlxyXG4gICAgICAgICAgPC9kaXY+XHJcbiAgICAgICAgPC9kaXY+XHJcbiAgICAgICl9XHJcblxyXG4gICAgICB7LyogSGVhZGVyIGFuZCBhY3Rpb25zICovfVxyXG4gICAgICA8ZGl2IGNsYXNzTmFtZT1cImZsZXggZmxleC1jb2wgZ2FwLTQgbWItNlwiPlxyXG4gICAgICAgIDxoMSBjbGFzc05hbWU9XCJ0ZXh0LTN4bCBmb250LWV4dHJhYm9sZCB0ZXh0LXJlZC02MDAgZGFyazp0ZXh0LXJlZC00MDBcIj5Db250YWN0cyAtIEFERCBDT05UQUNUIEJVVFRPTiBJUyBIRVJFITwvaDE+XHJcbiAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJmbGV4IGZsZXgtd3JhcCBnYXAtMiBpdGVtcy1jZW50ZXJcIj5cclxuICAgICAgICAgIHsvKiBBZGQgQ29udGFjdCBidXR0b24gLSBBbHdheXMgdmlzaWJsZSAtIFVwZGF0ZWQgKi99XHJcbiAgICAgICAgICA8YnV0dG9uXHJcbiAgICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTYgcHktMyByb3VuZGVkLWZ1bGwgYmctZ3JhZGllbnQtdG8tciBmcm9tLXJlZC01MDAgdG8tb3JhbmdlLTUwMCB0ZXh0LXdoaXRlIGZvbnQtYm9sZCBzaGFkb3ctbGcgaG92ZXI6ZnJvbS1yZWQtNjAwIGhvdmVyOnRvLW9yYW5nZS02MDAgdHJhbnNpdGlvbiBmbGV4IGl0ZW1zLWNlbnRlciBnYXAtMiB0ZXh0LWxnXCJcclxuICAgICAgICAgICAgb25DbGljaz17KCkgPT4gc2V0U2hvd0NyZWF0ZU1vZGFsKHRydWUpfVxyXG4gICAgICAgICAgPlxyXG4gICAgICAgICAgICA8UGx1cyBjbGFzc05hbWU9XCJ3LTUgaC01XCIgLz5cclxuICAgICAgICAgICAg4omhxpLDhMK7IEFERCBDT05UQUNUIEJVVFRPTiDiiaHGksOEwrtcclxuICAgICAgICAgIDwvYnV0dG9uPlxyXG4gICAgICAgICAgey8qIEFkZCBDb250YWN0IGJ1dHRvbiAtIEFsd2F5cyB2aXNpYmxlIC0gVXBkYXRlZCAqL31cclxuICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgY2xhc3NOYW1lPVwicHgtNiBweS0zIHJvdW5kZWQtZnVsbCBiZy1ncmFkaWVudC10by1yIGZyb20tcmVkLTUwMCB0by1vcmFuZ2UtNTAwIHRleHQtd2hpdGUgZm9udC1ib2xkIHNoYWRvdy1sZyBob3Zlcjpmcm9tLXJlZC02MDAgaG92ZXI6dG8tb3JhbmdlLTYwMCB0cmFuc2l0aW9uIGZsZXggaXRlbXMtY2VudGVyIGdhcC0yIHRleHQtbGdcIlxyXG4gICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBzZXRTaG93Q3JlYXRlTW9kYWwodHJ1ZSl9XHJcbiAgICAgICAgICA+XHJcbiAgICAgICAgICAgIDxQbHVzIGNsYXNzTmFtZT1cInctNSBoLTVcIiAvPlxyXG4gICAgICAgICAgICDiiaHGksOEwrsgQUREIENPTlRBQ1QgQlVUVE9OIOKJocaSw4TCu1xyXG4gICAgICAgICAgPC9idXR0b24+XHJcblxyXG4gICAgICAgICAgey8qIFNlYXJjaCBiYXIgKi99XHJcbiAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInJlbGF0aXZlXCI+XHJcbiAgICAgICAgICAgIDxpbnB1dFxyXG4gICAgICAgICAgICAgIHR5cGU9XCJ0ZXh0XCJcclxuICAgICAgICAgICAgICB2YWx1ZT17c2VhcmNofVxyXG4gICAgICAgICAgICAgIG9uQ2hhbmdlPXtlID0+IHNldFNlYXJjaChlLnRhcmdldC52YWx1ZSl9XHJcbiAgICAgICAgICAgICAgcGxhY2Vob2xkZXI9XCJTZWFyY2ggY29udGFjdHMuLi4gLSBVUERBVEVEXCJcclxuICAgICAgICAgICAgICBjbGFzc05hbWU9XCJyb3VuZGVkLWZ1bGwgcGwtMTAgcHItNCBweS0yIGJnLXdoaXRlLzgwIGRhcms6YmctZ3JheS04MDAvODAgdGV4dC1ncmF5LTkwMCBkYXJrOnRleHQtd2hpdGUgcGxhY2Vob2xkZXI6dGV4dC1ncmF5LTQwMCBmb2N1czpvdXRsaW5lLW5vbmUgZm9jdXM6cmluZy0yIGZvY3VzOnJpbmctcGluay00MDAgdy01NiBzaGFkb3dcIlxyXG4gICAgICAgICAgICAvPlxyXG4gICAgICAgICAgICA8U2VhcmNoIGNsYXNzTmFtZT1cImFic29sdXRlIGxlZnQtMyB0b3AtMi41IHctNSBoLTUgdGV4dC1ncmF5LTQwMFwiIC8+XHJcbiAgICAgICAgICA8L2Rpdj5cclxuXHJcbiAgICAgICAgICB7LyogRXhwb3J0IGJ1dHRvbnMgKi99XHJcbiAgICAgICAgICA8YnV0dG9uXHJcbiAgICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTQgcHktMiByb3VuZGVkLWZ1bGwgYmctZ3JhZGllbnQtdG8tciBmcm9tLWJsdWUtNTAwIHRvLXB1cnBsZS01MDAgdGV4dC13aGl0ZSBmb250LXNlbWlib2xkIHNoYWRvdyBob3Zlcjpmcm9tLWJsdWUtNjAwIGhvdmVyOnRvLXB1cnBsZS02MDAgdHJhbnNpdGlvbiBmbGV4IGl0ZW1zLWNlbnRlciBnYXAtMlwiXHJcbiAgICAgICAgICAgIG9uQ2xpY2s9e2V4cG9ydENTVn1cclxuICAgICAgICAgID5cclxuICAgICAgICAgICAgPERvd25sb2FkIGNsYXNzTmFtZT1cInctNCBoLTRcIiAvPlxyXG4gICAgICAgICAgICBFeHBvcnQgQ1NWXHJcbiAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgY2xhc3NOYW1lPVwicHgtNCBweS0yIHJvdW5kZWQtZnVsbCBiZy1ncmFkaWVudC10by1yIGZyb20tZ3JlZW4tNTAwIHRvLXRlYWwtNTAwIHRleHQtd2hpdGUgZm9udC1zZW1pYm9sZCBzaGFkb3cgaG92ZXI6ZnJvbS1ncmVlbi02MDAgaG92ZXI6dG8tdGVhbC02MDAgdHJhbnNpdGlvbiBmbGV4IGl0ZW1zLWNlbnRlciBnYXAtMlwiXHJcbiAgICAgICAgICAgIG9uQ2xpY2s9e2V4cG9ydEV4Y2VsfVxyXG4gICAgICAgICAgPlxyXG4gICAgICAgICAgICA8RG93bmxvYWQgY2xhc3NOYW1lPVwidy00IGgtNFwiIC8+XHJcbiAgICAgICAgICAgIEV4cG9ydCBFeGNlbFxyXG4gICAgICAgICAgPC9idXR0b24+XHJcbiAgICAgICAgPC9kaXY+XHJcbiAgICAgIDwvZGl2PlxyXG5cclxuICAgICAgey8qIFJlc3BvbnNpdmUgVGFibGU6IGhpZGRlbiBvbiBtb2JpbGUgKi99XHJcbiAgICAgIDxkaXYgY2xhc3NOYW1lPVwib3ZlcmZsb3cteC1hdXRvIHJvdW5kZWQtMnhsIHNoYWRvdyBib3JkZXIgYmctd2hpdGUgZGFyazpiZy1ncmF5LTkwMCBoaWRkZW4gc206YmxvY2tcIj5cclxuICAgICAgICA8dGFibGUgY2xhc3NOYW1lPVwibWluLXctZnVsbCBkaXZpZGUteSBkaXZpZGUtZ3JheS0yMDAgZGFyazpkaXZpZGUtZ3JheS04MDBcIj5cclxuICAgICAgICAgIDx0aGVhZCBjbGFzc05hbWU9XCJiZy1ncmF5LTUwIGRhcms6YmctZ3JheS04MDBcIj5cclxuICAgICAgICAgICAgPHRyPlxyXG4gICAgICAgICAgICAgIDx0aCBjbGFzc05hbWU9XCJweC00IHB5LTMgdGV4dC1jZW50ZXJcIj5cclxuICAgICAgICAgICAgICAgIDxpbnB1dFxyXG4gICAgICAgICAgICAgICAgICB0eXBlPVwiY2hlY2tib3hcIlxyXG4gICAgICAgICAgICAgICAgICBjaGVja2VkPXthbGxTZWxlY3RlZH1cclxuICAgICAgICAgICAgICAgICAgcmVmPXtlbCA9PiB7IGlmIChlbCkgZWwuaW5kZXRlcm1pbmF0ZSA9ICFhbGxTZWxlY3RlZCAmJiBzb21lU2VsZWN0ZWQ7IH19XHJcbiAgICAgICAgICAgICAgICAgIG9uQ2hhbmdlPXt0b2dnbGVBbGx9XHJcbiAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cImFjY2VudC1waW5rLTUwMCB3LTUgaC01IHJvdW5kZWQgZm9jdXM6cmluZy1waW5rLTQwMFwiXHJcbiAgICAgICAgICAgICAgICAvPlxyXG4gICAgICAgICAgICAgIDwvdGg+XHJcbiAgICAgICAgICAgICAge2NvbHVtbnMubWFwKChjb2wpID0+IChcclxuICAgICAgICAgICAgICAgIDx0aFxyXG4gICAgICAgICAgICAgICAgICBrZXk9e2NvbC5rZXl9XHJcbiAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTYgcHktMyB0ZXh0LWxlZnQgdGV4dC14cyBmb250LWJvbGQgdGV4dC1ncmF5LTUwMCBkYXJrOnRleHQtZ3JheS0zMDAgdXBwZXJjYXNlIHRyYWNraW5nLXdpZGVyIGN1cnNvci1wb2ludGVyIHNlbGVjdC1ub25lIGdyb3VwXCJcclxuICAgICAgICAgICAgICAgICAgb25DbGljaz17KCkgPT4gaGFuZGxlU29ydChjb2wua2V5KX1cclxuICAgICAgICAgICAgICAgID5cclxuICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3NOYW1lPVwiZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTFcIj5cclxuICAgICAgICAgICAgICAgICAgICB7Y29sLmxhYmVsfVxyXG4gICAgICAgICAgICAgICAgICAgIHtzb3J0QnkgPT09IGNvbC5rZXkgJiYgKFxyXG4gICAgICAgICAgICAgICAgICAgICAgc29ydERpciA9PT0gXCJhc2NcIiA/IChcclxuICAgICAgICAgICAgICAgICAgICAgICAgPENoZXZyb25VcCBjbGFzc05hbWU9XCJ3LTQgaC00IHRleHQtcGluay01MDBcIiAvPlxyXG4gICAgICAgICAgICAgICAgICAgICAgKSA6IChcclxuICAgICAgICAgICAgICAgICAgICAgICAgPENoZXZyb25Eb3duIGNsYXNzTmFtZT1cInctNCBoLTQgdGV4dC1waW5rLTUwMFwiIC8+XHJcbiAgICAgICAgICAgICAgICAgICAgICApXHJcbiAgICAgICAgICAgICAgICAgICAgKX1cclxuICAgICAgICAgICAgICAgICAgPC9zcGFuPlxyXG4gICAgICAgICAgICAgICAgPC90aD5cclxuICAgICAgICAgICAgICApKX1cclxuICAgICAgICAgICAgICA8dGggY2xhc3NOYW1lPVwicHgtNiBweS0zIHRleHQtcmlnaHQgdGV4dC14cyBmb250LWJvbGQgdGV4dC1ncmF5LTUwMCBkYXJrOnRleHQtZ3JheS0zMDAgdXBwZXJjYXNlIHRyYWNraW5nLXdpZGVyXCI+QWN0aW9uczwvdGg+XHJcbiAgICAgICAgICAgIDwvdHI+XHJcbiAgICAgICAgICA8L3RoZWFkPlxyXG4gICAgICAgICAgPHRib2R5IGNsYXNzTmFtZT1cImJnLXdoaXRlIGRhcms6YmctZ3JheS05MDAgZGl2aWRlLXkgZGl2aWRlLWdyYXktMTAwIGRhcms6ZGl2aWRlLWdyYXktODAwXCI+XHJcbiAgICAgICAgICAgIHtwYWdlZENvbnRhY3RzLm1hcCgoY29udGFjdCkgPT4gKFxyXG4gICAgICAgICAgICAgIDx0clxyXG4gICAgICAgICAgICAgICAga2V5PXtjb250YWN0LmlkfVxyXG4gICAgICAgICAgICAgICAgY2xhc3NOYW1lPXtgdHJhbnNpdGlvbiAke3NlbGVjdGVkLmluY2x1ZGVzKGNvbnRhY3QuaWQpID8gXCJiZy1waW5rLTEwMCBkYXJrOmJnLXBpbmstOTAwLzQwXCIgOiBcImhvdmVyOmJnLXBpbmstNTAgZGFyazpob3ZlcjpiZy1waW5rLTkwMC8yMFwifWB9XHJcbiAgICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgPHRkIGNsYXNzTmFtZT1cInB4LTQgcHktNCB0ZXh0LWNlbnRlclwiPlxyXG4gICAgICAgICAgICAgICAgICA8aW5wdXRcclxuICAgICAgICAgICAgICAgICAgICB0eXBlPVwiY2hlY2tib3hcIlxyXG4gICAgICAgICAgICAgICAgICAgIGNoZWNrZWQ9e3NlbGVjdGVkLmluY2x1ZGVzKGNvbnRhY3QuaWQpfVxyXG4gICAgICAgICAgICAgICAgICAgIG9uQ2hhbmdlPXsoKSA9PiB0b2dnbGVPbmUoY29udGFjdC5pZCl9XHJcbiAgICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwiYWNjZW50LXBpbmstNTAwIHctNSBoLTUgcm91bmRlZCBmb2N1czpyaW5nLXBpbmstNDAwXCJcclxuICAgICAgICAgICAgICAgICAgLz5cclxuICAgICAgICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICAgICAgICB7LyogTmFtZSAoaW5saW5lIGVkaXQpICovfVxyXG4gICAgICAgICAgICAgICAgPHRkIGNsYXNzTmFtZT1cInB4LTYgcHktNCB3aGl0ZXNwYWNlLW5vd3JhcCBmb250LXNlbWlib2xkIHRleHQtZ3JheS05MDAgZGFyazp0ZXh0LXdoaXRlXCI+XHJcbiAgICAgICAgICAgICAgICAgIHtlZGl0aW5nQ2VsbCAmJiBlZGl0aW5nQ2VsbC5pZCA9PT0gY29udGFjdC5pZCAmJiBlZGl0aW5nQ2VsbC5maWVsZCA9PT0gXCJuYW1lXCIgPyAoXHJcbiAgICAgICAgICAgICAgICAgICAgPGlucHV0XHJcbiAgICAgICAgICAgICAgICAgICAgICBhdXRvRm9jdXNcclxuICAgICAgICAgICAgICAgICAgICAgIHZhbHVlPXtlZGl0Q2VsbFZhbHVlfVxyXG4gICAgICAgICAgICAgICAgICAgICAgb25DaGFuZ2U9e2UgPT4gc2V0RWRpdENlbGxWYWx1ZShlLnRhcmdldC52YWx1ZSl9XHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkJsdXI9eygpID0+IHNhdmVFZGl0Q2VsbChjb250YWN0LmlkLCBcIm5hbWVcIil9XHJcbiAgICAgICAgICAgICAgICAgICAgICBvbktleURvd249e2UgPT4gaGFuZGxlRWRpdENlbGxLZXkoZSwgY29udGFjdC5pZCwgXCJuYW1lXCIpfVxyXG4gICAgICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwicm91bmRlZCBweC0yIHB5LTEgYm9yZGVyLTIgYm9yZGVyLXBpbmstNDAwIGZvY3VzOm91dGxpbmUtbm9uZSBmb2N1czpyaW5nLTIgZm9jdXM6cmluZy1waW5rLTQwMCBiZy13aGl0ZSBkYXJrOmJnLWdyYXktODAwIHRleHQtZ3JheS05MDAgZGFyazp0ZXh0LXdoaXRlXCJcclxuICAgICAgICAgICAgICAgICAgICAvPlxyXG4gICAgICAgICAgICAgICAgICApIDogKFxyXG4gICAgICAgICAgICAgICAgICAgIDxzcGFuXHJcbiAgICAgICAgICAgICAgICAgICAgICBjbGFzc05hbWU9XCJjdXJzb3ItcG9pbnRlciBob3Zlcjp1bmRlcmxpbmVcIlxyXG4gICAgICAgICAgICAgICAgICAgICAgb25DbGljaz17KCkgPT4gc3RhcnRFZGl0Q2VsbChjb250YWN0LmlkLCBcIm5hbWVcIiwgY29udGFjdC5uYW1lKX1cclxuICAgICAgICAgICAgICAgICAgICA+XHJcbiAgICAgICAgICAgICAgICAgICAgICB7Y29udGFjdC5uYW1lIHx8IGNvbnRhY3QuY29udGFjdF9uYW1lfVxyXG4gICAgICAgICAgICAgICAgICAgIDwvc3Bhbj5cclxuICAgICAgICAgICAgICAgICAgKX1cclxuICAgICAgICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICAgICAgICB7LyogRW1haWwgKGlubGluZSBlZGl0KSAqL31cclxuICAgICAgICAgICAgICAgIDx0ZCBjbGFzc05hbWU9XCJweC02IHB5LTQgd2hpdGVzcGFjZS1ub3dyYXAgdGV4dC1ncmF5LTcwMCBkYXJrOnRleHQtZ3JheS0yMDBcIj5cclxuICAgICAgICAgICAgICAgICAge2VkaXRpbmdDZWxsICYmIGVkaXRpbmdDZWxsLmlkID09PSBjb250YWN0LmlkICYmIGVkaXRpbmdDZWxsLmZpZWxkID09PSBcImVtYWlsXCIgPyAoXHJcbiAgICAgICAgICAgICAgICAgICAgPGlucHV0XHJcbiAgICAgICAgICAgICAgICAgICAgICBhdXRvRm9jdXNcclxuICAgICAgICAgICAgICAgICAgICAgIHZhbHVlPXtlZGl0Q2VsbFZhbHVlfVxyXG4gICAgICAgICAgICAgICAgICAgICAgb25DaGFuZ2U9e2UgPT4gc2V0RWRpdENlbGxWYWx1ZShlLnRhcmdldC52YWx1ZSl9XHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkJsdXI9eygpID0+IHNhdmVFZGl0Q2VsbChjb250YWN0LmlkLCBcImVtYWlsXCIpfVxyXG4gICAgICAgICAgICAgICAgICAgICAgb25LZXlEb3duPXtlID0+IGhhbmRsZUVkaXRDZWxsS2V5KGUsIGNvbnRhY3QuaWQsIFwiZW1haWxcIil9XHJcbiAgICAgICAgICAgICAgICAgICAgICBjbGFzc05hbWU9XCJyb3VuZGVkIHB4LTIgcHktMSBib3JkZXItMiBib3JkZXItcGluay00MDAgZm9jdXM6b3V0bGluZS1ub25lIGZvY3VzOnJpbmctMiBmb2N1czpyaW5nLXBpbmstNDAwIGJnLXdoaXRlIGRhcms6YmctZ3JheS04MDAgdGV4dC1ncmF5LTkwMCBkYXJrOnRleHQtd2hpdGVcIlxyXG4gICAgICAgICAgICAgICAgICAgIC8+XHJcbiAgICAgICAgICAgICAgICAgICkgOiAoXHJcbiAgICAgICAgICAgICAgICAgICAgPHNwYW5cclxuICAgICAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cImN1cnNvci1wb2ludGVyIGhvdmVyOnVuZGVybGluZVwiXHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBzdGFydEVkaXRDZWxsKGNvbnRhY3QuaWQsIFwiZW1haWxcIiwgY29udGFjdC5lbWFpbCl9XHJcbiAgICAgICAgICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgICAgICAge2NvbnRhY3QuZW1haWx9XHJcbiAgICAgICAgICAgICAgICAgICAgPC9zcGFuPlxyXG4gICAgICAgICAgICAgICAgICApfVxyXG4gICAgICAgICAgICAgICAgPC90ZD5cclxuICAgICAgICAgICAgICAgIHsvKiBDb21wYW55IChpbmxpbmUgZWRpdCkgKi99XHJcbiAgICAgICAgICAgICAgICA8dGQgY2xhc3NOYW1lPVwicHgtNiBweS00IHdoaXRlc3BhY2Utbm93cmFwIHRleHQtZ3JheS03MDAgZGFyazp0ZXh0LWdyYXktMjAwXCI+XHJcbiAgICAgICAgICAgICAgICAgIHtlZGl0aW5nQ2VsbCAmJiBlZGl0aW5nQ2VsbC5pZCA9PT0gY29udGFjdC5pZCAmJiBlZGl0aW5nQ2VsbC5maWVsZCA9PT0gXCJjb21wYW55XCIgPyAoXHJcbiAgICAgICAgICAgICAgICAgICAgPGlucHV0XHJcbiAgICAgICAgICAgICAgICAgICAgICBhdXRvRm9jdXNcclxuICAgICAgICAgICAgICAgICAgICAgIHZhbHVlPXtlZGl0Q2VsbFZhbHVlfVxyXG4gICAgICAgICAgICAgICAgICAgICAgb25DaGFuZ2U9e2UgPT4gc2V0RWRpdENlbGxWYWx1ZShlLnRhcmdldC52YWx1ZSl9XHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkJsdXI9eygpID0+IHNhdmVFZGl0Q2VsbChjb250YWN0LmlkLCBcImNvbXBhbnlcIil9XHJcbiAgICAgICAgICAgICAgICAgICAgICBvbktleURvd249e2UgPT4gaGFuZGxlRWRpdENlbGxLZXkoZSwgY29udGFjdC5pZCwgXCJjb21wYW55XCIpfVxyXG4gICAgICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwicm91bmRlZCBweC0yIHB5LTEgYm9yZGVyLTIgYm9yZGVyLXBpbmstNDAwIGZvY3VzOm91dGxpbmUtbm9uZSBmb2N1czpyaW5nLTIgZm9jdXM6cmluZy1waW5rLTQwMCBiZy13aGl0ZSBkYXJrOmJnLWdyYXktODAwIHRleHQtZ3JheS05MDAgZGFyazp0ZXh0LXdoaXRlXCJcclxuICAgICAgICAgICAgICAgICAgICAvPlxyXG4gICAgICAgICAgICAgICAgICApIDogKFxyXG4gICAgICAgICAgICAgICAgICAgIDxzcGFuXHJcbiAgICAgICAgICAgICAgICAgICAgICBjbGFzc05hbWU9XCJjdXJzb3ItcG9pbnRlciBob3Zlcjp1bmRlcmxpbmVcIlxyXG4gICAgICAgICAgICAgICAgICAgICAgb25DbGljaz17KCkgPT4gc3RhcnRFZGl0Q2VsbChjb250YWN0LmlkLCBcImNvbXBhbnlcIiwgY29udGFjdC5jb21wYW55KX1cclxuICAgICAgICAgICAgICAgICAgICA+XHJcbiAgICAgICAgICAgICAgICAgICAgICB7Y29udGFjdC5jb21wYW55fVxyXG4gICAgICAgICAgICAgICAgICAgIDwvc3Bhbj5cclxuICAgICAgICAgICAgICAgICAgKX1cclxuICAgICAgICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICAgICAgICB7LyogT3duZXIgKi99XHJcbiAgICAgICAgICAgICAgICA8dGQgY2xhc3NOYW1lPVwicHgtNiBweS00IHdoaXRlc3BhY2Utbm93cmFwIHRleHQtZ3JheS03MDAgZGFyazp0ZXh0LWdyYXktMjAwXCI+XHJcbiAgICAgICAgICAgICAgICAgIHtjb250YWN0Lm93bmVyX25hbWUgfHwgXCJOL0FcIn1cclxuICAgICAgICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICAgICAgICB7LyogQ3JlYXRlZCAqL31cclxuICAgICAgICAgICAgICAgIDx0ZCBjbGFzc05hbWU9XCJweC02IHB5LTQgd2hpdGVzcGFjZS1ub3dyYXAgdGV4dC1ncmF5LTUwMCBkYXJrOnRleHQtZ3JheS00MDAgdGV4dC1zbVwiPlxyXG4gICAgICAgICAgICAgICAgICB7Y29udGFjdC5jcmVhdGVkX2F0Py5zbGljZSgwLCAxMCkgfHwgXCJOL0FcIn1cclxuICAgICAgICAgICAgICAgIDwvdGQ+XHJcbiAgICAgICAgICAgICAgICB7LyogQWN0aW9ucyAqL31cclxuICAgICAgICAgICAgICAgIDx0ZCBjbGFzc05hbWU9XCJweC02IHB5LTQgd2hpdGVzcGFjZS1ub3dyYXAgdGV4dC1yaWdodCB0ZXh0LXNtIGZvbnQtbWVkaXVtXCI+XHJcbiAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBqdXN0aWZ5LWVuZCBnYXAtMlwiPlxyXG4gICAgICAgICAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cInAtMiByb3VuZGVkLWZ1bGwgaG92ZXI6YmctYmx1ZS0xMDAgZGFyazpob3ZlcjpiZy1ibHVlLTkwMCB0cmFuc2l0aW9uXCJcclxuICAgICAgICAgICAgICAgICAgICAgIHRpdGxlPVwiVmlld1wiXHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBoYW5kbGVWaWV3KGNvbnRhY3QuaWQpfVxyXG4gICAgICAgICAgICAgICAgICAgICAgZGlzYWJsZWQ9e2FjdGlvbkxvYWRpbmd9XHJcbiAgICAgICAgICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgICAgICAgPEV5ZSBjbGFzc05hbWU9XCJ3LTUgaC01IHRleHQtYmx1ZS01MDBcIiAvPlxyXG4gICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPlxyXG4gICAgICAgICAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cInAtMiByb3VuZGVkLWZ1bGwgaG92ZXI6YmctcmVkLTEwMCBkYXJrOmhvdmVyOmJnLXJlZC05MDAgdHJhbnNpdGlvblwiXHJcbiAgICAgICAgICAgICAgICAgICAgICB0aXRsZT1cIkRlbGV0ZVwiXHJcbiAgICAgICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBoYW5kbGVEZWxldGUoY29udGFjdC5pZCl9XHJcbiAgICAgICAgICAgICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgICAgICAgICAgICA+XHJcbiAgICAgICAgICAgICAgICAgICAgICA8VHJhc2gyIGNsYXNzTmFtZT1cInctNSBoLTUgdGV4dC1yZWQtNTAwXCIgLz5cclxuICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgICAgICAgICAgPC9kaXY+XHJcbiAgICAgICAgICAgICAgICA8L3RkPlxyXG4gICAgICAgICAgICAgIDwvdHI+XHJcbiAgICAgICAgICAgICkpfVxyXG4gICAgICAgICAgICB7cGFnZWRDb250YWN0cy5sZW5ndGggPT09IDAgJiYgKFxyXG4gICAgICAgICAgICAgIDx0cj5cclxuICAgICAgICAgICAgICAgIDx0ZCBjb2xTcGFuPXtjb2x1bW5zLmxlbmd0aCArIDJ9IGNsYXNzTmFtZT1cInRleHQtY2VudGVyIHB5LTggdGV4dC1ncmF5LTQwMCBkYXJrOnRleHQtZ3JheS02MDBcIj5ObyBjb250YWN0cyBmb3VuZC48L3RkPlxyXG4gICAgICAgICAgICAgIDwvdHI+XHJcbiAgICAgICAgICAgICl9XHJcbiAgICAgICAgICA8L3Rib2R5PlxyXG4gICAgICAgIDwvdGFibGU+XHJcbiAgICAgIDwvZGl2PlxyXG5cclxuICAgICAgey8qIFJlc3BvbnNpdmUgQ2FyZCBWaWV3OiBvbmx5IG9uIG1vYmlsZSAqL31cclxuICAgICAgPGRpdiBjbGFzc05hbWU9XCJzbTpoaWRkZW4gc3BhY2UteS00XCI+XHJcbiAgICAgICAge3BhZ2VkQ29udGFjdHMubWFwKChjb250YWN0KSA9PiAoXHJcbiAgICAgICAgICA8ZGl2XHJcbiAgICAgICAgICAgIGtleT17Y29udGFjdC5pZH1cclxuICAgICAgICAgICAgY2xhc3NOYW1lPXtgcm91bmRlZC0yeGwgc2hhZG93IGJvcmRlciBwLTQgYmctd2hpdGUgZGFyazpiZy1ncmF5LTkwMCB0cmFuc2l0aW9uICR7c2VsZWN0ZWQuaW5jbHVkZXMoY29udGFjdC5pZCkgPyBcImJnLXBpbmstMTAwIGRhcms6YmctcGluay05MDAvNDAgYm9yZGVyLXBpbmstMzAwIGRhcms6Ym9yZGVyLXBpbmstODAwXCIgOiBcImhvdmVyOmJnLXBpbmstNTAgZGFyazpob3ZlcjpiZy1waW5rLTkwMC8yMFwifWB9XHJcbiAgICAgICAgICA+XHJcbiAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBpdGVtcy1jZW50ZXIganVzdGlmeS1iZXR3ZWVuIG1iLTJcIj5cclxuICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImZsZXggaXRlbXMtY2VudGVyIGdhcC0yXCI+XHJcbiAgICAgICAgICAgICAgICA8aW5wdXRcclxuICAgICAgICAgICAgICAgICAgdHlwZT1cImNoZWNrYm94XCJcclxuICAgICAgICAgICAgICAgICAgY2hlY2tlZD17c2VsZWN0ZWQuaW5jbHVkZXMoY29udGFjdC5pZCl9XHJcbiAgICAgICAgICAgICAgICAgIG9uQ2hhbmdlPXsoKSA9PiB0b2dnbGVPbmUoY29udGFjdC5pZCl9XHJcbiAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cImFjY2VudC1waW5rLTUwMCB3LTUgaC01IHJvdW5kZWQgZm9jdXM6cmluZy1waW5rLTQwMFwiXHJcbiAgICAgICAgICAgICAgICAvPlxyXG4gICAgICAgICAgICAgICAgPHNwYW4gY2xhc3NOYW1lPVwiZm9udC1ib2xkIHRleHQtbGcgdGV4dC1ncmF5LTkwMCBkYXJrOnRleHQtd2hpdGVcIj57Y29udGFjdC5uYW1lIHx8IGNvbnRhY3QuY29udGFjdF9uYW1lfTwvc3Bhbj5cclxuICAgICAgICAgICAgICA8L2Rpdj5cclxuICAgICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImZsZXggZ2FwLTJcIj5cclxuICAgICAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwicC0yIHJvdW5kZWQtZnVsbCBob3ZlcjpiZy1ibHVlLTEwMCBkYXJrOmhvdmVyOmJnLWJsdWUtOTAwIHRyYW5zaXRpb25cIlxyXG4gICAgICAgICAgICAgICAgICB0aXRsZT1cIlZpZXdcIlxyXG4gICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBoYW5kbGVWaWV3KGNvbnRhY3QuaWQpfVxyXG4gICAgICAgICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgICAgICAgID5cclxuICAgICAgICAgICAgICAgICAgPEV5ZSBjbGFzc05hbWU9XCJ3LTUgaC01IHRleHQtYmx1ZS01MDBcIiAvPlxyXG4gICAgICAgICAgICAgICAgPC9idXR0b24+XHJcbiAgICAgICAgICAgICAgICA8YnV0dG9uXHJcbiAgICAgICAgICAgICAgICAgIGNsYXNzTmFtZT1cInAtMiByb3VuZGVkLWZ1bGwgaG92ZXI6YmcteWVsbG93LTEwMCBkYXJrOmhvdmVyOmJnLXllbGxvdy05MDAgdHJhbnNpdGlvblwiXHJcbiAgICAgICAgICAgICAgICAgIHRpdGxlPVwiRWRpdFwiXHJcbiAgICAgICAgICAgICAgICAgIGRpc2FibGVkPXthY3Rpb25Mb2FkaW5nfVxyXG4gICAgICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgICA8RWRpdCBjbGFzc05hbWU9XCJ3LTUgaC01IHRleHQteWVsbG93LTUwMFwiIC8+XHJcbiAgICAgICAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICAgICAgY2xhc3NOYW1lPVwicC0yIHJvdW5kZWQtZnVsbCBob3ZlcjpiZy1yZWQtMTAwIGRhcms6aG92ZXI6YmctcmVkLTkwMCB0cmFuc2l0aW9uXCJcclxuICAgICAgICAgICAgICAgICAgdGl0bGU9XCJEZWxldGVcIlxyXG4gICAgICAgICAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBoYW5kbGVEZWxldGUoY29udGFjdC5pZCl9XHJcbiAgICAgICAgICAgICAgICAgIGRpc2FibGVkPXthY3Rpb25Mb2FkaW5nfVxyXG4gICAgICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgICA8VHJhc2gyIGNsYXNzTmFtZT1cInctNSBoLTUgdGV4dC1yZWQtNTAwXCIgLz5cclxuICAgICAgICAgICAgICAgIDwvYnV0dG9uPlxyXG4gICAgICAgICAgICAgIDwvZGl2PlxyXG4gICAgICAgICAgICA8L2Rpdj5cclxuICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ0ZXh0LWdyYXktNzAwIGRhcms6dGV4dC1ncmF5LTIwMCB0ZXh0LXNtIG1iLTFcIj48c3BhbiBjbGFzc05hbWU9XCJmb250LXNlbWlib2xkXCI+RW1haWw6PC9zcGFuPiB7Y29udGFjdC5lbWFpbH08L2Rpdj5cclxuICAgICAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJ0ZXh0LWdyYXktNzAwIGRhcms6dGV4dC1ncmF5LTIwMCB0ZXh0LXNtIG1iLTFcIj48c3BhbiBjbGFzc05hbWU9XCJmb250LXNlbWlib2xkXCI+Q29tcGFueTo8L3NwYW4+IHtjb250YWN0LmNvbXBhbnl9PC9kaXY+XHJcbiAgICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidGV4dC1ncmF5LTcwMCBkYXJrOnRleHQtZ3JheS0yMDAgdGV4dC1zbSBtYi0xXCI+PHNwYW4gY2xhc3NOYW1lPVwiZm9udC1zZW1pYm9sZFwiPk93bmVyOjwvc3Bhbj4ge2NvbnRhY3Qub3duZXJfbmFtZSB8fCBcIk4vQVwifTwvZGl2PlxyXG4gICAgICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInRleHQtZ3JheS01MDAgZGFyazp0ZXh0LWdyYXktNDAwIHRleHQteHNcIj48c3BhbiBjbGFzc05hbWU9XCJmb250LXNlbWlib2xkXCI+Q3JlYXRlZDo8L3NwYW4+IHtjb250YWN0LmNyZWF0ZWRfYXQ/LnNsaWNlKDAsIDEwKSB8fCBcIk4vQVwifTwvZGl2PlxyXG4gICAgICAgICAgPC9kaXY+XHJcbiAgICAgICAgKSl9XHJcbiAgICAgICAge3BhZ2VkQ29udGFjdHMubGVuZ3RoID09PSAwICYmIChcclxuICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwidGV4dC1jZW50ZXIgcHktOCB0ZXh0LWdyYXktNDAwIGRhcms6dGV4dC1ncmF5LTYwMFwiPk5vIGNvbnRhY3RzIGZvdW5kLjwvZGl2PlxyXG4gICAgICAgICl9XHJcbiAgICAgIDwvZGl2PlxyXG5cclxuICAgICAgey8qIFBhZ2luYXRpb24gQ29udHJvbHMgKi99XHJcbiAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBqdXN0aWZ5LWVuZCBpdGVtcy1jZW50ZXIgZ2FwLTIgbXQtNFwiPlxyXG4gICAgICAgIDxidXR0b25cclxuICAgICAgICAgIGNsYXNzTmFtZT1cInB4LTMgcHktMSByb3VuZGVkLWZ1bGwgYmctZ3JheS0xMDAgZGFyazpiZy1ncmF5LTgwMCB0ZXh0LWdyYXktNTAwIGRhcms6dGV4dC1ncmF5LTMwMCBmb250LXNlbWlib2xkIGRpc2FibGVkOm9wYWNpdHktNTBcIlxyXG4gICAgICAgICAgb25DbGljaz17KCkgPT4gc2V0UGFnZSgocCkgPT4gTWF0aC5tYXgoMSwgcCAtIDEpKX1cclxuICAgICAgICAgIGRpc2FibGVkPXtwYWdlID09PSAxfVxyXG4gICAgICAgID5cclxuICAgICAgICAgIFByZXZcclxuICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICA8c3BhbiBjbGFzc05hbWU9XCJ0ZXh0LWdyYXktNzAwIGRhcms6dGV4dC1ncmF5LTIwMCB0ZXh0LXNtXCI+XHJcbiAgICAgICAgICBQYWdlIHtwYWdlfSBvZiB7dG90YWxQYWdlc31cclxuICAgICAgICA8L3NwYW4+XHJcbiAgICAgICAgPGJ1dHRvblxyXG4gICAgICAgICAgY2xhc3NOYW1lPVwicHgtMyBweS0xIHJvdW5kZWQtZnVsbCBiZy1ncmF5LTEwMCBkYXJrOmJnLWdyYXktODAwIHRleHQtZ3JheS01MDAgZGFyazp0ZXh0LWdyYXktMzAwIGZvbnQtc2VtaWJvbGQgZGlzYWJsZWQ6b3BhY2l0eS01MFwiXHJcbiAgICAgICAgICBvbkNsaWNrPXsoKSA9PiBzZXRQYWdlKChwKSA9PiBNYXRoLm1pbih0b3RhbFBhZ2VzLCBwICsgMSkpfVxyXG4gICAgICAgICAgZGlzYWJsZWQ9e3BhZ2UgPT09IHRvdGFsUGFnZXN9XHJcbiAgICAgICAgPlxyXG4gICAgICAgICAgTmV4dFxyXG4gICAgICAgIDwvYnV0dG9uPlxyXG4gICAgICA8L2Rpdj5cclxuXHJcbiAgICAgIHsvKiBEZXRhaWwgTW9kYWwgdXNpbmcgdGhlIERldGFpbE1vZGFsIGNvbXBvbmVudCAqL31cclxuICAgICAgPERldGFpbE1vZGFsIG9wZW49eyEhZGV0YWlsQ29udGFjdH0gb25DbG9zZT17KCkgPT4gc2V0RGV0YWlsQ29udGFjdChudWxsKX0gdGl0bGU9XCJDb250YWN0IERldGFpbHNcIj5cclxuICAgICAgICB7ZGV0YWlsQ29udGFjdCAmJiAoXHJcbiAgICAgICAgICA8PlxyXG4gICAgICAgICAgICA8ZGl2PjxiPk5hbWU6PC9iPiB7ZGV0YWlsQ29udGFjdC5uYW1lfTwvZGl2PlxyXG4gICAgICAgICAgICA8ZGl2PjxiPkVtYWlsOjwvYj4ge2RldGFpbENvbnRhY3QuZW1haWx9PC9kaXY+XHJcbiAgICAgICAgICAgIDxkaXY+PGI+Q29tcGFueTo8L2I+IHtkZXRhaWxDb250YWN0LmNvbXBhbnl9PC9kaXY+XHJcbiAgICAgICAgICAgIDxkaXY+PGI+T3duZXI6PC9iPiB7ZGV0YWlsQ29udGFjdC5vd25lcl9uYW1lIHx8IGRldGFpbENvbnRhY3Qub3duZXJ9PC9kaXY+XHJcbiAgICAgICAgICAgIDxkaXY+PGI+Q3JlYXRlZDo8L2I+IHtkZXRhaWxDb250YWN0LmNyZWF0ZWRfYXQ/LnNsaWNlKDAsIDEwKSB8fCBkZXRhaWxDb250YWN0LmNyZWF0ZWR9PC9kaXY+XHJcbiAgICAgICAgICA8Lz5cclxuICAgICAgICApfVxyXG4gICAgICA8L0RldGFpbE1vZGFsPlxyXG5cclxuICAgICAgey8qIENvbmZpcm1hdGlvbiBNb2RhbCBmb3IgU2luZ2xlIERlbGV0ZSAqL31cclxuICAgICAgPERldGFpbE1vZGFsIG9wZW49e2NvbmZpcm1EZWxldGVJZCAhPT0gbnVsbH0gb25DbG9zZT17Y2FuY2VsRGVsZXRlfSB0aXRsZT1cIkRlbGV0ZSBDb250YWN0P1wiPlxyXG4gICAgICAgIDxkaXY+QXJlIHlvdSBzdXJlIHlvdSB3YW50IHRvIGRlbGV0ZSB0aGlzIGNvbnRhY3Q/PC9kaXY+XHJcbiAgICAgICAgPGRpdiBjbGFzc05hbWU9XCJmbGV4IGdhcC00IG10LTYganVzdGlmeS1lbmRcIj5cclxuICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgY2xhc3NOYW1lPVwicHgtNCBweS0yIHJvdW5kZWQtZnVsbCBiZy1ncmF5LTIwMCBkYXJrOmJnLWdyYXktODAwIHRleHQtZ3JheS03MDAgZGFyazp0ZXh0LWdyYXktMjAwIGZvbnQtc2VtaWJvbGQgaG92ZXI6YmctZ3JheS0zMDAgZGFyazpob3ZlcjpiZy1ncmF5LTcwMCB0cmFuc2l0aW9uXCJcclxuICAgICAgICAgICAgb25DbGljaz17Y2FuY2VsRGVsZXRlfVxyXG4gICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgID5cclxuICAgICAgICAgICAgQ2FuY2VsXHJcbiAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgY2xhc3NOYW1lPVwicHgtNCBweS0yIHJvdW5kZWQtZnVsbCBiZy1yZWQtNTAwIHRleHQtd2hpdGUgZm9udC1zZW1pYm9sZCBob3ZlcjpiZy1yZWQtNjAwIHRyYW5zaXRpb25cIlxyXG4gICAgICAgICAgICBvbkNsaWNrPXtjb25maXJtRGVsZXRlfVxyXG4gICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgID5cclxuICAgICAgICAgICAgRGVsZXRlXHJcbiAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICA8L2Rpdj5cclxuICAgICAgPC9EZXRhaWxNb2RhbD5cclxuXHJcbiAgICAgIHsvKiBDb25maXJtYXRpb24gTW9kYWwgZm9yIEJ1bGsgRGVsZXRlICovfVxyXG4gICAgICA8RGV0YWlsTW9kYWwgb3Blbj17Y29uZmlybUJ1bGtEZWxldGV9IG9uQ2xvc2U9e2NhbmNlbEJ1bGtEZWxldGV9IHRpdGxlPVwiRGVsZXRlIE11bHRpcGxlIENvbnRhY3RzP1wiPlxyXG4gICAgICAgIDxkaXY+QXJlIHlvdSBzdXJlIHlvdSB3YW50IHRvIGRlbGV0ZSB7c2VsZWN0ZWQubGVuZ3RofSBjb250YWN0cz8gVGhpcyBhY3Rpb24gY2Fubm90IGJlIHVuZG9uZS48L2Rpdj5cclxuICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImZsZXggZ2FwLTQgbXQtNiBqdXN0aWZ5LWVuZFwiPlxyXG4gICAgICAgICAgPGJ1dHRvblxyXG4gICAgICAgICAgICBjbGFzc05hbWU9XCJweC00IHB5LTIgcm91bmRlZC1mdWxsIGJnLWdyYXktMjAwIGRhcms6YmctZ3JheS04MDAgdGV4dC1ncmF5LTcwMCBkYXJrOnRleHQtZ3JheS0yMDAgZm9udC1zZW1pYm9sZCBob3ZlcjpiZy1ncmF5LTMwMCBkYXJrOmhvdmVyOmJnLWdyYXktNzAwIHRyYW5zaXRpb25cIlxyXG4gICAgICAgICAgICBvbkNsaWNrPXtjYW5jZWxCdWxrRGVsZXRlfVxyXG4gICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgID5cclxuICAgICAgICAgICAgQ2FuY2VsXHJcbiAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgY2xhc3NOYW1lPVwicHgtNCBweS0yIHJvdW5kZWQtZnVsbCBiZy1yZWQtNTAwIHRleHQtd2hpdGUgZm9udC1zZW1pYm9sZCBob3ZlcjpiZy1yZWQtNjAwIHRyYW5zaXRpb25cIlxyXG4gICAgICAgICAgICBvbkNsaWNrPXtkZWxldGVTZWxlY3RlZH1cclxuICAgICAgICAgICAgZGlzYWJsZWQ9e2FjdGlvbkxvYWRpbmd9XHJcbiAgICAgICAgICA+XHJcbiAgICAgICAgICAgIHthY3Rpb25Mb2FkaW5nID8gXCJEZWxldGluZy4uLlwiIDogXCJEZWxldGUgQWxsXCJ9XHJcbiAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICA8L2Rpdj5cclxuICAgICAgPC9EZXRhaWxNb2RhbD5cclxuXHJcbiAgICAgIHsvKiBDcmVhdGUgQ29udGFjdCBNb2RhbCAqL31cclxuICAgICAgPERldGFpbE1vZGFsIG9wZW49e3Nob3dDcmVhdGVNb2RhbH0gb25DbG9zZT17KCkgPT4gc2V0U2hvd0NyZWF0ZU1vZGFsKGZhbHNlKX0gdGl0bGU9XCJDcmVhdGUgTmV3IENvbnRhY3RcIj5cclxuICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cInNwYWNlLXktNFwiPlxyXG4gICAgICAgICAgPGRpdj5cclxuICAgICAgICAgICAgPGxhYmVsIGNsYXNzTmFtZT1cImJsb2NrIHRleHQtc20gZm9udC1tZWRpdW0gdGV4dC1ncmF5LTcwMCBkYXJrOnRleHQtZ3JheS0zMDAgbWItMVwiPlxyXG4gICAgICAgICAgICAgIE5hbWUgKlxyXG4gICAgICAgICAgICA8L2xhYmVsPlxyXG4gICAgICAgICAgICA8aW5wdXRcclxuICAgICAgICAgICAgICB0eXBlPVwidGV4dFwiXHJcbiAgICAgICAgICAgICAgdmFsdWU9e25ld0NvbnRhY3QubmFtZX1cclxuICAgICAgICAgICAgICBvbkNoYW5nZT17KGUpID0+IHNldE5ld0NvbnRhY3QoeyAuLi5uZXdDb250YWN0LCBuYW1lOiBlLnRhcmdldC52YWx1ZSB9KX1cclxuICAgICAgICAgICAgICBjbGFzc05hbWU9XCJ3LWZ1bGwgcHgtMyBweS0yIGJvcmRlciBib3JkZXItZ3JheS0zMDAgZGFyazpib3JkZXItZ3JheS02MDAgcm91bmRlZC1sZyBiZy13aGl0ZSBkYXJrOmJnLWdyYXktODAwIHRleHQtZ3JheS05MDAgZGFyazp0ZXh0LXdoaXRlIGZvY3VzOm91dGxpbmUtbm9uZSBmb2N1czpyaW5nLTIgZm9jdXM6cmluZy1waW5rLTQwMFwiXHJcbiAgICAgICAgICAgICAgcGxhY2Vob2xkZXI9XCJFbnRlciBjb250YWN0IG5hbWVcIlxyXG4gICAgICAgICAgICAvPlxyXG4gICAgICAgICAgPC9kaXY+XHJcbiAgICAgICAgICA8ZGl2PlxyXG4gICAgICAgICAgICA8bGFiZWwgY2xhc3NOYW1lPVwiYmxvY2sgdGV4dC1zbSBmb250LW1lZGl1bSB0ZXh0LWdyYXktNzAwIGRhcms6dGV4dC1ncmF5LTMwMCBtYi0xXCI+XHJcbiAgICAgICAgICAgICAgRW1haWxcclxuICAgICAgICAgICAgPC9sYWJlbD5cclxuICAgICAgICAgICAgPGlucHV0XHJcbiAgICAgICAgICAgICAgdHlwZT1cImVtYWlsXCJcclxuICAgICAgICAgICAgICB2YWx1ZT17bmV3Q29udGFjdC5lbWFpbH1cclxuICAgICAgICAgICAgICBvbkNoYW5nZT17KGUpID0+IHNldE5ld0NvbnRhY3QoeyAuLi5uZXdDb250YWN0LCBlbWFpbDogZS50YXJnZXQudmFsdWUgfSl9XHJcbiAgICAgICAgICAgICAgY2xhc3NOYW1lPVwidy1mdWxsIHB4LTMgcHktMiBib3JkZXIgYm9yZGVyLWdyYXktMzAwIGRhcms6Ym9yZGVyLWdyYXktNjAwIHJvdW5kZWQtbGcgYmctd2hpdGUgZGFyazpiZy1ncmF5LTgwMCB0ZXh0LWdyYXktOTAwIGRhcms6dGV4dC13aGl0ZSBmb2N1czpvdXRsaW5lLW5vbmUgZm9jdXM6cmluZy0yIGZvY3VzOnJpbmctcGluay00MDBcIlxyXG4gICAgICAgICAgICAgIHBsYWNlaG9sZGVyPVwiRW50ZXIgZW1haWwgYWRkcmVzc1wiXHJcbiAgICAgICAgICAgIC8+XHJcbiAgICAgICAgICA8L2Rpdj5cclxuICAgICAgICAgIDxkaXY+XHJcbiAgICAgICAgICAgIDxsYWJlbCBjbGFzc05hbWU9XCJibG9jayB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtZ3JheS03MDAgZGFyazp0ZXh0LWdyYXktMzAwIG1iLTFcIj5cclxuICAgICAgICAgICAgICBDb21wYW55XHJcbiAgICAgICAgICAgIDwvbGFiZWw+XHJcbiAgICAgICAgICAgIDxpbnB1dFxyXG4gICAgICAgICAgICAgIHR5cGU9XCJ0ZXh0XCJcclxuICAgICAgICAgICAgICB2YWx1ZT17bmV3Q29udGFjdC5jb21wYW55fVxyXG4gICAgICAgICAgICAgIG9uQ2hhbmdlPXsoZSkgPT4gc2V0TmV3Q29udGFjdCh7IC4uLm5ld0NvbnRhY3QsIGNvbXBhbnk6IGUudGFyZ2V0LnZhbHVlIH0pfVxyXG4gICAgICAgICAgICAgIGNsYXNzTmFtZT1cInctZnVsbCBweC0zIHB5LTIgYm9yZGVyIGJvcmRlci1ncmF5LTMwMCBkYXJrOmJvcmRlci1ncmF5LTYwMCByb3VuZGVkLWxnIGJnLXdoaXRlIGRhcms6YmctZ3JheS04MDAgdGV4dC1ncmF5LTkwMCBkYXJrOnRleHQtd2hpdGUgZm9jdXM6b3V0bGluZS1ub25lIGZvY3VzOnJpbmctMiBmb2N1czpyaW5nLXBpbmstNDAwXCJcclxuICAgICAgICAgICAgICBwbGFjZWhvbGRlcj1cIkVudGVyIGNvbXBhbnkgbmFtZVwiXHJcbiAgICAgICAgICAgIC8+XHJcbiAgICAgICAgICA8L2Rpdj5cclxuICAgICAgICAgIDxkaXYgY2xhc3NOYW1lPVwiZmxleCBnYXAtNCBtdC02IGp1c3RpZnktZW5kXCI+XHJcbiAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICBjbGFzc05hbWU9XCJweC00IHB5LTIgcm91bmRlZC1mdWxsIGJnLWdyYXktMjAwIGRhcms6YmctZ3JheS04MDAgdGV4dC1ncmF5LTcwMCBkYXJrOnRleHQtZ3JheS0yMDAgZm9udC1zZW1pYm9sZCBob3ZlcjpiZy1ncmF5LTMwMCBkYXJrOmhvdmVyOmJnLWdyYXktNzAwIHRyYW5zaXRpb25cIlxyXG4gICAgICAgICAgICAgIG9uQ2xpY2s9eygpID0+IHNldFNob3dDcmVhdGVNb2RhbChmYWxzZSl9XHJcbiAgICAgICAgICAgICAgZGlzYWJsZWQ9e2FjdGlvbkxvYWRpbmd9XHJcbiAgICAgICAgICAgID5cclxuICAgICAgICAgICAgICBDYW5jZWxcclxuICAgICAgICAgICAgPC9idXR0b24+XHJcbiAgICAgICAgICAgIDxidXR0b25cclxuICAgICAgICAgICAgICBjbGFzc05hbWU9XCJweC00IHB5LTIgcm91bmRlZC1mdWxsIGJnLWdyYWRpZW50LXRvLXIgZnJvbS1waW5rLTUwMCB0by1wdXJwbGUtNTAwIHRleHQtd2hpdGUgZm9udC1zZW1pYm9sZCBob3Zlcjpmcm9tLXBpbmstNjAwIGhvdmVyOnRvLXB1cnBsZS02MDAgdHJhbnNpdGlvblwiXHJcbiAgICAgICAgICAgICAgb25DbGljaz17aGFuZGxlQ3JlYXRlQ29udGFjdH1cclxuICAgICAgICAgICAgICBkaXNhYmxlZD17YWN0aW9uTG9hZGluZ31cclxuICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgIHthY3Rpb25Mb2FkaW5nID8gXCJDcmVhdGluZy4uLlwiIDogXCJDcmVhdGUgQ29udGFjdFwifVxyXG4gICAgICAgICAgICA8L2J1dHRvbj5cclxuICAgICAgICAgIDwvZGl2PlxyXG4gICAgICAgIDwvZGl2PlxyXG4gICAgICA8L0RldGFpbE1vZGFsPlxyXG5cclxuICAgICAgey8qIFRvYXN0IE5vdGlmaWNhdGlvbiAqL31cclxuICAgICAge3RvYXN0ICYmIChcclxuICAgICAgICA8ZGl2IGNsYXNzTmFtZT1cImZpeGVkIGJvdHRvbS02IHJpZ2h0LTYgYmctZ3JlZW4tNjAwIHRleHQtd2hpdGUgcHgtNiBweS0zIHJvdW5kZWQteGwgc2hhZG93LWxnIHotNTAgYW5pbWF0ZS1mYWRlLWluXCI+XHJcbiAgICAgICAgICB7dG9hc3R9XHJcbiAgICAgICAgPC9kaXY+XHJcbiAgICAgICl9XHJcbiAgICA8L2Rpdj5cclxuICApO1xyXG59IFxyXG4iXSwiZmlsZSI6IkM6L1VzZXJzL0toYW5hL3NtYXJ0X2NybS9mcm9udGVuZC9zcmMvcGFnZXMvQ29udGFjdHMudHN4In0=
