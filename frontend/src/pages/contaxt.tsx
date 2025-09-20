import { useEffect, useMemo, useState } from 'react';
import { Search, Eye, Plus, Trash2, X, Download, ArrowRight } from 'lucide-react';
import * as XLSX from 'xlsx';
import { fetchContacts, getContact, createContact, updateContact, deleteContact } from '../services/contacts';
import { convertContactToLead } from '../services/leads';
import DetailModal from '../components/DetailModal';
import AnimatedModal from '../components/AnimatedModal';

interface Contact {
  id: number;
  name: string;
  email: string;
  phone: string;
  company: string;
  owner_name: string;
  created_at: string;
}

interface NewContact {
  name: string;
  email: string;
  phone: string;
  company: string;
  owner_id: number;
}

export default function Contacts() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [detailContact, setDetailContact] = useState<Contact | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editingCell, setEditingCell] = useState<{ id: number; field: string } | null>(null);
  const [editCellValue, setEditCellValue] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [newContact, setNewContact] = useState<NewContact>({
    name: '',
    email: '',
    phone: '',
    company: '',
    owner_id: 1,
  });
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    fetchContacts()
      .then((data) => {
        setContacts(data as any);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load contacts');
        setLoading(false);
      });
  }, []);

  const filtered = useMemo(() => {
    if (!search) return contacts;
    const q = search.toLowerCase();
    return contacts.filter((c) =>
      (c.name || '').toLowerCase().includes(q) ||
      (c.email || '').toLowerCase().includes(q) ||
      (c.phone || '').toLowerCase().includes(q) ||
      (c.company || '').toLowerCase().includes(q)
    );
  }, [contacts, search]);

  const handleCreate = async () => {
    if (!newContact.name.trim()) {
      setToast('Name is required');
      setTimeout(() => setToast(null), 3000);
      return;
    }
    setCreating(true);
    try {
      const created = await createContact(newContact);
      setContacts((prev) => [created as any, ...prev]);
      setShowCreate(false);
      setNewContact({ name: '', email: '', phone: '', company: '', owner_id: 1 });
      setToast('Contact created successfully!');
      setTimeout(() => setToast(null), 3000);
    } catch {
      setToast('Failed to create contact');
      setTimeout(() => setToast(null), 3000);
    } finally {
      setCreating(false);
    }
  };

  const handleView = async (id: number) => {
    try {
      const full = await getContact(id);
      setDetailContact(full as any);
    } catch {
      setToast('Failed to fetch contact details');
      setTimeout(() => setToast(null), 3000);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this contact?')) return;
    try {
      await deleteContact(id);
      setContacts((prev) => prev.filter((c) => c.id !== id));
      setToast('Contact deleted successfully!');
      setTimeout(() => setToast(null), 3000);
    } catch {
      setToast('Failed to delete contact');
      setTimeout(() => setToast(null), 3000);
    }
  };

  // Convert contact to lead
  const handleConvertToLead = async (contact: Contact) => {
    setActionLoading(true);
    try {
      const leadData = {
        title: `${contact.name} - ${contact.company}`,
        status: 'new',
        source: 'contact_conversion',
        score: 75
      };
      
      const result = await convertContactToLead(contact.id, leadData);
      setToast(`Contact converted to lead: ${result.message}`);
      setTimeout(() => setToast(null), 3000);
    } catch (e) {
      alert('Failed to create lead from contact');
    }
    setActionLoading(false);
  };

  // Inline edit handlers
  const startEditCell = (id: number, field: string, value: string) => {
    setEditingCell({ id, field });
    setEditCellValue(value || '');
  };

  const saveEditCell = async (id: number, field: string) => {
    setActionLoading(true);
    try {
      await updateContact(id, { [field]: editCellValue });
      setContacts(prev =>
        prev.map(contact =>
          contact.id === id ? { ...contact, [field]: editCellValue } : contact
        )
      );
      setToast('Contact updated successfully!');
      setTimeout(() => setToast(null), 3000);
    } catch {
      setToast('Failed to update contact');
      setTimeout(() => setToast(null), 3000);
    }
    setEditingCell(null);
    setEditCellValue('');
    setActionLoading(false);
  };

  const handleEditCellKey = (e: React.KeyboardEvent, id: number, field: string) => {
    if (e.key === 'Enter') saveEditCell(id, field);
    if (e.key === 'Escape') setEditingCell(null);
  };

  // CSV Export
  function exportCSV() {
    const headers = ['Name', 'Email', 'Phone', 'Company', 'Owner', 'Created'];
    const rows = filtered.map(contact => [
      contact.name,
      contact.email,
      contact.phone,
      contact.company,
      contact.owner_name,
      contact.created_at?.slice(0, 10),
    ]);
    const csvContent =
      [headers, ...rows]
        .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(','))
        .join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'contacts.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  // Excel Export
  function exportExcel() {
    const headers = ['Name', 'Email', 'Phone', 'Company', 'Owner', 'Created'];
    const rows = filtered.map(contact => [
      contact.name,
      contact.email,
      contact.phone,
      contact.company,
      contact.owner_name,
      contact.created_at?.slice(0, 10),
    ]);
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Contacts');
    XLSX.writeFile(wb, 'contacts.xlsx');
  }

  if (loading) return <div className='p-8 text-lg'>Loading...</div>;

  return (
    <div className='p-6'>
      {/* Toast Notification */}
      {toast && (
        <div className='fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50'>
          {toast}
        </div>
      )}
      
      {/* Error Display */}
      {error && (
        <div className='mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg'>
          {error}
          <button 
            onClick={() => setError(null)}
            className='ml-2 text-red-500 hover:text-red-700'
          >
            ×
          </button>
        </div>
      )}
      <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6'>
        <h1 className='text-3xl font-extrabold text-gray-900 dark:text-white'>Contacts</h1>
        <div className='flex items-center gap-3'>
          <div className='relative'>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder='Search name, email, phone, company...'
              className='rounded-full pl-10 pr-4 py-2 bg-white/80 dark:bg-gray-800/80 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 w-72 shadow'
            />
            <Search className='absolute left-3 top-2.5 w-5 h-5 text-gray-400' />
          </div>
          <button
            onClick={exportCSV}
            className='flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700'
          >
            <Download className='w-4 h-4' /> Export CSV
          </button>
          <button
            onClick={exportExcel}
            className='flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700'
          >
            <Download className='w-4 h-4' /> Export XLS
          </button>
          <button
            onClick={(e) => { setAnchorRect((e.currentTarget as HTMLButtonElement).getBoundingClientRect()); setShowCreate(true); }}
            className='flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700'
          >
            <Plus className='w-4 h-4' /> Add Contact
          </button>
        </div>
      </div>

      <div className='overflow-x-auto rounded-2xl shadow border bg-white dark:bg-gray-900'>
        <table className='min-w-full'>
          <thead>
            <tr className='bg-gray-50 dark:bg-gray-800'>
              <th className='px-6 py-3 text-left text-sm font-semibold'>Name</th>
              <th className='px-6 py-3 text-left text-sm font-semibold'>Email</th>
              <th className='px-6 py-3 text-left text-sm font-semibold'>Phone</th>
              <th className='px-6 py-3 text-left text-sm font-semibold'>Company</th>
              <th className='px-6 py-3 text-left text-sm font-semibold'>Actions</th>
            </tr>
          </thead>
          <tbody className='divide-y divide-gray-200 dark:divide-gray-800'>
            {filtered.map((c) => (
              <tr key={c.id} className='hover:bg-gray-50 dark:hover:bg-gray-800'>
                <td className='px-6 py-3'>
                  {editingCell && editingCell.id === c.id && editingCell.field === 'name' ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={(e) => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(c.id, 'name')}
                      onKeyDown={(e) => handleEditCellKey(e, c.id, 'name')}
                      className='rounded px-2 py-1 border-2 border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                    />
                  ) : (
                    <span
                      className='cursor-pointer hover:underline'
                      onClick={() => startEditCell(c.id, 'name', c.name)}
                    >
                      {c.name}
                    </span>
                  )}
                </td>
                <td className='px-6 py-3'>
                  {editingCell && editingCell.id === c.id && editingCell.field === 'email' ? (
                    <input
                      autoFocus
                      type='email'
                      value={editCellValue}
                      onChange={(e) => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(c.id, 'email')}
                      onKeyDown={(e) => handleEditCellKey(e, c.id, 'email')}
                      className='rounded px-2 py-1 border-2 border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                    />
                  ) : (
                    <span
                      className='cursor-pointer hover:underline'
                      onClick={() => startEditCell(c.id, 'email', c.email)}
                    >
                      {c.email}
                    </span>
                  )}
                </td>
                <td className='px-6 py-3'>
                  {editingCell && editingCell.id === c.id && editingCell.field === 'phone' ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={(e) => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(c.id, 'phone')}
                      onKeyDown={(e) => handleEditCellKey(e, c.id, 'phone')}
                      className='rounded px-2 py-1 border-2 border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                    />
                  ) : (
                    <span
                      className='cursor-pointer hover:underline'
                      onClick={() => startEditCell(c.id, 'phone', c.phone)}
                    >
                      {c.phone}
                    </span>
                  )}
                </td>
                <td className='px-6 py-3'>
                  {editingCell && editingCell.id === c.id && editingCell.field === 'company' ? (
                    <input
                      autoFocus
                      value={editCellValue}
                      onChange={(e) => setEditCellValue(e.target.value)}
                      onBlur={() => saveEditCell(c.id, 'company')}
                      onKeyDown={(e) => handleEditCellKey(e, c.id, 'company')}
                      className='rounded px-2 py-1 border-2 border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                    />
                  ) : (
                    <span
                      className='cursor-pointer hover:underline'
                      onClick={() => startEditCell(c.id, 'company', c.company)}
                    >
                      {c.company}
                    </span>
                  )}
                </td>
                <td className='px-6 py-3'>
                  <div className='flex gap-2'>
                    <button 
                      className='text-blue-600 hover:text-blue-800' 
                      onClick={() => handleView(c.id)}
                      disabled={actionLoading}
                      title="View Contact"
                    >
                      <Eye className='w-4 h-4' />
                    </button>
                    <button 
                      className='text-green-600 hover:text-green-800' 
                      onClick={() => handleConvertToLead(c)}
                      disabled={actionLoading}
                      title="Create Lead"
                    >
                      <ArrowRight className='w-4 h-4' />
                    </button>
                    <button 
                      className='text-red-600 hover:text-red-800' 
                      onClick={() => handleDelete(c.id)}
                      disabled={actionLoading}
                      title="Delete Contact"
                    >
                      <Trash2 className='w-4 h-4' />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <AnimatedModal open={showCreate} onClose={() => setShowCreate(false)} title="Create Contact">
        <div className='p-6 w-full max-w-md'>
          <div className='flex items-center justify-between mb-4'>
            <h2 className='text-xl font-bold'>Create Contact</h2>
            <button className='p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg' onClick={() => setShowCreate(false)}>
              <X className='w-5 h-5 text-gray-500' />
            </button>
          </div>
          <div className='space-y-4'>
            <div>
              <label className='block text-sm font-medium mb-1'>Name *</label>
              <input
                value={newContact.name}
                onChange={(e) => setNewContact({ ...newContact, name: e.target.value })}
                className='w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800'
                placeholder='Full name'
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-1'>Email</label>
              <input
                type='email'
                value={newContact.email}
                onChange={(e) => setNewContact({ ...newContact, email: e.target.value })}
                className='w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800'
                placeholder='name@company.com'
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-1'>Phone</label>
              <input
                value={newContact.phone}
                onChange={(e) => setNewContact({ ...newContact, phone: e.target.value })}
                className='w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800'
                placeholder='+1 555 123 4567'
              />
            </div>
            <div>
              <label className='block text-sm font-medium mb-1'>Company</label>
              <input
                value={newContact.company}
                onChange={(e) => setNewContact({ ...newContact, company: e.target.value })}
                className='w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800'
                placeholder='Company name'
              />
            </div>
          </div>
          <div className='flex gap-3 mt-6'>
            <button className='flex-1 px-4 py-2 border rounded-lg' onClick={() => setShowCreate(false)}>Cancel</button>
            <button
              className='flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50'
              onClick={handleCreate}
              disabled={creating || !newContact.name.trim()}
            >
              {creating ? 'Creating…' : 'Create Contact'}
            </button>
          </div>
        </div>
      </AnimatedModal>

      <DetailModal open={!!detailContact} onClose={() => setDetailContact(null)} title='Contact Details'>
        {detailContact && (
          <>
            <div><b>Name:</b> {detailContact.name}</div>
            <div><b>Email:</b> {detailContact.email}</div>
            <div><b>Phone:</b> {detailContact.phone}</div>
            <div><b>Company:</b> {detailContact.company}</div>
            <div><b>Owner:</b> {detailContact.owner_name}</div>
            <div><b>Created:</b> {detailContact.created_at?.slice(0, 10)}</div>
          </>
        )}
      </DetailModal>
    </div>
  );
}
