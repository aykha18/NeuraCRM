import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  FileText,
  CreditCard,
  TrendingUp,
  Calendar,
  Plus,
  Eye,
  Edit,
  Trash2,
  Download,
  Send,
  CheckCircle,
  AlertTriangle,
  Clock,
  BarChart3,
  BarChart,
  PieChart,
  LineChart,
  Filter,
  Search,
  RefreshCw,
  Activity,
  Target,
  Users,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
  TrendingDown,
  Settings
} from 'lucide-react';
import { apiRequest } from '../utils/api';
import AnimatedModal from '../components/AnimatedModal';
import Button from '../components/Button';
import { companySettingsService, type CompanySettings } from '../services/companySettings';

interface Invoice {
  id: number;
  invoice_number: string;
  deal_id: number;
  customer_account_id?: number;
  issue_date: string;
  due_date: string;
  status: 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  balance_due: number;
  description?: string;
  notes?: string;
  created_at: string;
  sent_at?: string;
  paid_at?: string;
}

interface Payment {
  id: number;
  invoice_id: number;
  payment_number: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  payment_reference?: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  notes?: string;
  created_at: string;
}

interface Revenue {
  id: number;
  invoice_id: number;
  deal_id: number;
  amount: number;
  recognition_date: string;
  recognition_type: string;
  recognition_period?: string;
  revenue_type: string;
  revenue_category?: string;
  status: string;
  created_at: string;
}

interface FinancialDashboard {
  revenue_metrics: {
    total_revenue: number;
    monthly_revenue: number;
    revenue_growth: number;
  };
  invoice_metrics: {
    total_invoices: number;
    paid_invoices: number;
    overdue_invoices: number;
    collection_rate: number;
  };
  payment_metrics: {
    total_payments: number;
    average_payment_time: number;
    payment_success_rate: number;
  };
  outstanding_amounts: {
    total_outstanding: number;
    overdue_amount: number;
    current_amount: number;
  };
}

interface Deal {
  id: number;
  title: string;
  value: number;
  status: string;
  contact_id?: number;
  contact_name?: string;
  customer_account_id?: number;
  customer_account_name?: string;
}

interface CustomerAccount {
  id: number;
  account_name: string;
  deal_id: number;
  contact_id?: number;
  contact_name?: string;
}

const FinancialManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'invoices' | 'payments' | 'revenue' | 'reports' | 'profit-loss' | 'cash-flow' | 'aging' | 'settings'>('dashboard');
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [revenue, setRevenue] = useState<Revenue[]>([]);
  const [dashboard, setDashboard] = useState<FinancialDashboard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dashboard analytics states
  const [recentActivities, setRecentActivities] = useState<any[]>([]);
  const [revenueTrend, setRevenueTrend] = useState<any[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<any[]>([]);
  const [invoiceStatusBreakdown, setInvoiceStatusBreakdown] = useState<any[]>([]);
  
  // Revenue form states
  const [showCreateRevenue, setShowCreateRevenue] = useState(false);
  const [revenueForm, setRevenueForm] = useState({
    invoice_id: '',
    amount: '',
    recognition_date: '',
    recognition_type: 'immediate',
    recognition_period: '',
    revenue_type: 'product',
    revenue_category: '',
    notes: ''
  });
  
  // Revenue invoice selection states
  const [availableInvoicesForRevenue, setAvailableInvoicesForRevenue] = useState<Invoice[]>([]);
  const [filteredInvoicesForRevenue, setFilteredInvoicesForRevenue] = useState<Invoice[]>([]);
  const [invoiceSearchTermForRevenue, setInvoiceSearchTermForRevenue] = useState('');
  const [showInvoiceDropdownForRevenue, setShowInvoiceDropdownForRevenue] = useState(false);
  const [selectedInvoiceForRevenue, setSelectedInvoiceForRevenue] = useState<Invoice | null>(null);
  
  // Reports states
  const [reports, setReports] = useState<any[]>([]);
  const [showGenerateReport, setShowGenerateReport] = useState(false);
  const [reportForm, setReportForm] = useState({
    report_type: 'profit_loss',
    report_name: '',
    start_date: '',
    end_date: '',
    include_charts: true
  });
  
  // Enhanced Financial Reports states
  const [profitLossData, setProfitLossData] = useState<any>(null);
  const [cashFlowData, setCashFlowData] = useState<any>(null);
  const [agingData, setAgingData] = useState<any>(null);
  const [financialSummary, setFinancialSummary] = useState<any>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportDateRange, setReportDateRange] = useState({
    start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  
  // Data for dropdowns
  const [wonDeals, setWonDeals] = useState<Deal[]>([]);
  const [customerAccounts, setCustomerAccounts] = useState<CustomerAccount[]>([]);
  const [filteredDeals, setFilteredDeals] = useState<Deal[]>([]);
  const [filteredAccounts, setFilteredAccounts] = useState<CustomerAccount[]>([]);
  
  // Modal states
  const [showCreateInvoice, setShowCreateInvoice] = useState(false);
  const [showCreatePayment, setShowCreatePayment] = useState(false);
  const [showInvoiceDetails, setShowInvoiceDetails] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [showDealSelectionModal, setShowDealSelectionModal] = useState(false);
  const [accountDealsForSelection, setAccountDealsForSelection] = useState<Deal[]>([]);
  const [showNoDealsMessage, setShowNoDealsMessage] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Payment form states
  const [availableInvoices, setAvailableInvoices] = useState<Invoice[]>([]);
  const [filteredInvoices, setFilteredInvoices] = useState<Invoice[]>([]);
  const [invoiceSearchTerm, setInvoiceSearchTerm] = useState('');
  const [showInvoiceDropdown, setShowInvoiceDropdown] = useState(false);
  const [selectedInvoiceForPayment, setSelectedInvoiceForPayment] = useState<Invoice | null>(null);
  
  // Form states
  const [invoiceForm, setInvoiceForm] = useState({
    deal_id: '',
    customer_account_id: '',
    due_date: '',
    subtotal: '',
    tax_rate: '',
    discount_amount: '',
    discount_type: 'percentage', // 'percentage' or 'fixed'
    advance_payment: '',
    recurring_invoice: false,
    recurring_frequency: 'monthly', // 'weekly', 'monthly', 'quarterly', 'yearly'
    recurring_end_date: '',
    description: '',
    notes: '',
    terms_conditions: ''
  });
  
  // Search states for dropdowns
  const [dealSearchTerm, setDealSearchTerm] = useState('');
  const [accountSearchTerm, setAccountSearchTerm] = useState('');
  const [showDealDropdown, setShowDealDropdown] = useState(false);
  const [showAccountDropdown, setShowAccountDropdown] = useState(false);
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<CustomerAccount | null>(null);
  
  const [paymentForm, setPaymentForm] = useState({
    invoice_id: '',
    amount: '',
    payment_date: '',
    payment_method: 'credit_card',
    payment_reference: '',
    notes: ''
  });

  // Company Settings form states
  const [companyForm, setCompanyForm] = useState({
    company_name: '',
    company_mobile: '',
    city: '',
    area: '',
    complete_address: '',
    trn: '',
    currency: 'AED - UAE Dirham (د.إ)',
    timezone: 'Dubai (UAE)'
  });

  const [billingConfig, setBillingConfig] = useState({
    trial_date_enabled: true,
    trial_date_days: '3',
    delivery_date_enabled: true,
    delivery_date_days: '3',
    advance_payment_enabled: true
  });

  // Company settings state
  const [companySettings, setCompanySettings] = useState<CompanySettings | null>(null);
  const [settingsLoading, setSettingsLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchWonDeals();
    fetchCustomerAccounts();
    fetchAvailableInvoices();
    fetchAvailableInvoicesForRevenue();
    fetchReports();
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.dropdown-container')) {
        setShowDealDropdown(false);
        setShowAccountDropdown(false);
        setShowInvoiceDropdown(false);
        setShowInvoiceDropdownForRevenue(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (activeTab === 'invoices') {
      fetchInvoices();
    } else if (activeTab === 'payments') {
      fetchPayments();
    } else if (activeTab === 'revenue') {
      fetchRevenue();
    } else if (activeTab === 'profit-loss') {
      fetchProfitLossReport(reportDateRange.start_date, reportDateRange.end_date);
    } else if (activeTab === 'cash-flow') {
      fetchCashFlowReport(reportDateRange.start_date, reportDateRange.end_date);
    } else if (activeTab === 'aging') {
      fetchAgingReport('receivables');
    }
  }, [activeTab]);

  // Regenerate analytics when data changes
  useEffect(() => {
    if (invoices.length > 0 || payments.length > 0 || revenue.length > 0) {
      generateDashboardAnalytics();
    }
  }, [invoices, payments, revenue]);

  // Load company settings when settings tab is active
  useEffect(() => {
    if (activeTab === 'settings') {
      fetchCompanySettings();
    }
  }, [activeTab]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/financial/dashboard') as FinancialDashboard;
      setDashboard(data);
      
      // Generate analytics from existing data
      generateDashboardAnalytics();
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // Enhanced Financial Reports fetch functions
  const fetchProfitLossReport = async (startDate?: string, endDate?: string) => {
    try {
      setReportLoading(true);
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const data = await apiRequest(`/api/financial/reports/profit-loss?${params.toString()}`);
      setProfitLossData(data);
    } catch (err) {
      console.error('Error fetching P&L report:', err);
      setError('Failed to fetch Profit & Loss report');
    } finally {
      setReportLoading(false);
    }
  };

  const fetchCashFlowReport = async (startDate?: string, endDate?: string) => {
    try {
      setReportLoading(true);
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      
      const data = await apiRequest(`/api/financial/reports/cash-flow?${params.toString()}`);
      setCashFlowData(data);
    } catch (err) {
      console.error('Error fetching cash flow report:', err);
      setError('Failed to fetch Cash Flow report');
    } finally {
      setReportLoading(false);
    }
  };

  const fetchAgingReport = async (reportType: string = 'receivables') => {
    try {
      setReportLoading(true);
      const data = await apiRequest(`/api/financial/reports/aging?report_type=${reportType}`);
      setAgingData(data);
    } catch (err) {
      console.error('Error fetching aging report:', err);
      setError('Failed to fetch Aging report');
    } finally {
      setReportLoading(false);
    }
  };

  const fetchFinancialSummary = async (period: string = 'month') => {
    try {
      setReportLoading(true);
      const data = await apiRequest(`/api/financial/reports/summary?period=${period}`);
      setFinancialSummary(data);
    } catch (err) {
      console.error('Error fetching financial summary:', err);
      setError('Failed to fetch Financial Summary');
    } finally {
      setReportLoading(false);
    }
  };

  const fetchCompanySettings = async () => {
    try {
      setSettingsLoading(true);
      const settings = await companySettingsService.getSettings();
      setCompanySettings(settings);
      
      // Update form states with loaded settings
      setCompanyForm({
        company_name: settings.company_name || '',
        company_mobile: settings.company_mobile || '',
        city: settings.city || '',
        area: settings.area || '',
        complete_address: settings.complete_address || '',
        trn: settings.trn || '',
        currency: settings.currency || 'AED - UAE Dirham (د.إ)',
        timezone: settings.timezone || 'Dubai (UAE)'
      });
      
      setBillingConfig({
        trial_date_enabled: settings.trial_date_enabled,
        trial_date_days: settings.trial_date_days.toString(),
        delivery_date_enabled: settings.delivery_date_enabled,
        delivery_date_days: settings.delivery_date_days.toString(),
        advance_payment_enabled: settings.advance_payment_enabled
      });
      
    } catch (err) {
      console.error('Error fetching company settings:', err);
      setError('Failed to fetch company settings');
    } finally {
      setSettingsLoading(false);
    }
  };

  const generateDashboardAnalytics = () => {
    // Generate revenue trend data (last 6 months)
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    const revenueData = months.map((month, index) => ({
      month,
      revenue: Math.floor(Math.random() * 50000) + 20000, // Mock data
      invoices: Math.floor(Math.random() * 20) + 10
    }));
    setRevenueTrend(revenueData);

    // Generate payment methods distribution
    const paymentMethodsData = [
      { method: 'Credit Card', count: payments.filter(p => p.payment_method === 'credit_card').length, amount: 45000 },
      { method: 'Bank Transfer', count: payments.filter(p => p.payment_method === 'bank_transfer').length, amount: 32000 },
      { method: 'Cash', count: payments.filter(p => p.payment_method === 'cash').length, amount: 15000 },
      { method: 'Check', count: payments.filter(p => p.payment_method === 'check').length, amount: 8000 }
    ];
    setPaymentMethods(paymentMethodsData);

    // Generate invoice status breakdown
    const statusBreakdown = [
      { status: 'Paid', count: invoices.filter(i => i.status === 'paid').length, amount: invoices.filter(i => i.status === 'paid').reduce((sum, i) => sum + i.total_amount, 0) },
      { status: 'Sent', count: invoices.filter(i => i.status === 'sent').length, amount: invoices.filter(i => i.status === 'sent').reduce((sum, i) => sum + i.total_amount, 0) },
      { status: 'Overdue', count: invoices.filter(i => i.status === 'overdue').length, amount: invoices.filter(i => i.status === 'overdue').reduce((sum, i) => sum + i.total_amount, 0) },
      { status: 'Draft', count: invoices.filter(i => i.status === 'draft').length, amount: invoices.filter(i => i.status === 'draft').reduce((sum, i) => sum + i.total_amount, 0) }
    ];
    setInvoiceStatusBreakdown(statusBreakdown);

    // Generate recent activities
    const activities: any[] = [];
    
    // Add recent invoices
    invoices.slice(0, 3).forEach(invoice => {
      activities.push({
        id: `invoice-${invoice.id}`,
        type: 'invoice',
        title: `Invoice ${invoice.invoice_number} created`,
        description: `Amount: ${formatCurrency(invoice.total_amount)}`,
        timestamp: new Date(invoice.created_at),
        icon: FileText,
        color: 'blue'
      });
    });

    // Add recent payments
    payments.slice(0, 3).forEach(payment => {
      activities.push({
        id: `payment-${payment.id}`,
        type: 'payment',
        title: `Payment ${payment.payment_number} received`,
        description: `Amount: ${formatCurrency(payment.amount)}`,
        timestamp: new Date(payment.payment_date),
        icon: CreditCard,
        color: 'green'
      });
    });

    // Add recent revenue
    revenue.slice(0, 2).forEach(rev => {
      activities.push({
        id: `revenue-${rev.id}`,
        type: 'revenue',
        title: `Revenue recognized`,
        description: `Amount: ${formatCurrency(rev.amount)}`,
        timestamp: new Date(rev.recognition_date),
        icon: TrendingUp,
        color: 'purple'
      });
    });

    // Sort by timestamp and take latest 8
    activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    setRecentActivities(activities.slice(0, 8));
  };

  const fetchWonDeals = async () => {
    try {
      const data = await apiRequest('/api/kanban/board') as any;
      if (data && data.stages && data.deals) {
        // Find deals in "Won" stage
        const wonStage = data.stages.find((stage: any) => 
          stage.name.toLowerCase() === 'won' || stage.name.toLowerCase() === 'closed won'
        );
        if (wonStage) {
          // Filter deals by stage_id instead of looking for wonStage.deals
          const wonDealsFromData = data.deals.filter((deal: any) => deal.stage_id === wonStage.id);
          
          const deals = wonDealsFromData.map((deal: any) => ({
            id: deal.id,
            title: deal.title,
            value: deal.value || 0,
            status: deal.status || 'won',
            contact_id: deal.contact_id,
            contact_name: deal.contact_name,
            customer_account_id: deal.customer_account_id,
            customer_account_name: deal.customer_account_name
          }));
          setWonDeals(deals);
          setFilteredDeals(deals);
        }
      }
    } catch (err) {
      console.error('Error fetching won deals:', err);
    }
  };

  const fetchCustomerAccounts = async () => {
    try {
      const data = await apiRequest('/api/customer-accounts') as CustomerAccount[];
      if (Array.isArray(data)) {
        setCustomerAccounts(data);
        setFilteredAccounts(data);
      }
    } catch (err) {
      console.error('Error fetching customer accounts:', err);
    }
  };

  const fetchAvailableInvoices = async () => {
    try {
      const data = await apiRequest('/api/invoices') as Invoice[];
      if (Array.isArray(data)) {
        // Only show invoices that have a balance due (not fully paid)
        const unpaidInvoices = data.filter(invoice => invoice.balance_due > 0);
        setAvailableInvoices(unpaidInvoices);
        setFilteredInvoices(unpaidInvoices);
      }
    } catch (err) {
      console.error('Error fetching available invoices:', err);
    }
  };

  const fetchAvailableInvoicesForRevenue = async () => {
    try {
      const [invoicesData, revenueData] = await Promise.all([
        apiRequest('/api/invoices') as Promise<Invoice[]>,
        apiRequest('/api/revenue') as Promise<Revenue[]>
      ]);
      
      
      if (Array.isArray(invoicesData) && Array.isArray(revenueData)) {
        // Get invoice IDs that already have revenue entries
        const recognizedInvoiceIds = new Set(revenueData.map(revenue => revenue.invoice_id));
        
        // Only show invoices that are paid AND not already recognized
        const availableInvoices = invoicesData.filter(invoice => 
          invoice.status === 'paid' && !recognizedInvoiceIds.has(invoice.id)
        );
        
        setAvailableInvoicesForRevenue(availableInvoices);
        setFilteredInvoicesForRevenue(availableInvoices);
      }
    } catch (err) {
      console.error('Error fetching available invoices for revenue:', err);
    }
  };

  // Search functionality
  const handleDealSearch = (term: string) => {
    setDealSearchTerm(term);
    setShowNoDealsMessage(false); // Hide message when user starts searching
    const filtered = wonDeals.filter(deal => 
      deal.title.toLowerCase().includes(term.toLowerCase()) ||
      deal.id.toString().includes(term) ||
      (deal.contact_name && deal.contact_name.toLowerCase().includes(term.toLowerCase()))
    );
    setFilteredDeals(filtered);
  };

  const handleAccountSearch = (term: string) => {
    setAccountSearchTerm(term);
    const filtered = customerAccounts.filter(account => 
      account.account_name.toLowerCase().includes(term.toLowerCase()) ||
      account.id.toString().includes(term) ||
      (account.contact_name && account.contact_name.toLowerCase().includes(term.toLowerCase()))
    );
    setFilteredAccounts(filtered);
  };

  const handleInvoiceSearch = (term: string) => {
    setInvoiceSearchTerm(term);
    const filtered = availableInvoices.filter(invoice => 
      invoice.invoice_number.toLowerCase().includes(term.toLowerCase()) ||
      invoice.id.toString().includes(term) ||
      invoice.deal_id.toString().includes(term)
    );
    setFilteredInvoices(filtered);
  };

  const handleInvoiceSearchForRevenue = (term: string) => {
    setInvoiceSearchTermForRevenue(term);
    const filtered = availableInvoicesForRevenue.filter(invoice => 
      invoice.invoice_number.toLowerCase().includes(term.toLowerCase()) ||
      invoice.id.toString().includes(term) ||
      invoice.deal_id.toString().includes(term)
    );
    setFilteredInvoicesForRevenue(filtered);
  };

  const selectInvoiceForPayment = (invoice: Invoice) => {
    setSelectedInvoiceForPayment(invoice);
    setInvoiceSearchTerm(`${invoice.invoice_number} - Balance: ${formatCurrency(invoice.balance_due)}`);
    setShowInvoiceDropdown(false);
    
    // Auto-populate payment form
    setPaymentForm(prev => ({
      ...prev,
      invoice_id: invoice.id.toString(),
      amount: invoice.balance_due.toString() // Default to full balance
    }));
  };

  const selectInvoiceForRevenue = (invoice: Invoice) => {
    setSelectedInvoiceForRevenue(invoice);
    setInvoiceSearchTermForRevenue(`${invoice.invoice_number} - Amount: ${formatCurrency(invoice.total_amount)}`);
    setShowInvoiceDropdownForRevenue(false);
    
    // Auto-populate revenue form
    setRevenueForm(prev => ({
      ...prev,
      invoice_id: invoice.id.toString(),
      amount: invoice.total_amount.toString() // Default to full amount
    }));
  };

  const selectDeal = (deal: Deal) => {
    setSelectedDeal(deal);
    setDealSearchTerm(`${deal.title} ($${formatCurrency(deal.value)})`);
    setShowDealDropdown(false);
    
    // Auto-populate customer account if available
    if (deal.customer_account_id) {
      const account = customerAccounts.find(acc => acc.id === deal.customer_account_id);
      if (account) {
        setSelectedAccount(account);
        setAccountSearchTerm(account.account_name);
        setInvoiceForm(prev => ({
          ...prev,
          deal_id: deal.id.toString(),
          customer_account_id: account.id.toString()
        }));
      } else {
        setInvoiceForm(prev => ({
          ...prev,
          deal_id: deal.id.toString()
        }));
      }
    } else {
      setInvoiceForm(prev => ({
        ...prev,
        deal_id: deal.id.toString()
      }));
    }
    
    // Auto-populate subtotal with deal value
    if (deal.value > 0) {
      setInvoiceForm(prev => ({
        ...prev,
        subtotal: deal.value.toString()
      }));
    }
  };

  const selectAccount = (account: CustomerAccount) => {
    setSelectedAccount(account);
    setAccountSearchTerm(account.account_name);
    setShowAccountDropdown(false);
    
    // Find the deal that this customer account was created from
    const accountDeals = wonDeals.filter(deal => deal.id === account.deal_id);
    
    if (accountDeals.length === 0) {
      // No deals found for this account - allow manual deal selection
      setInvoiceForm(prev => ({
        ...prev,
        customer_account_id: account.id.toString(),
        deal_id: '',
        subtotal: ''
      }));
      setSelectedDeal(null);
      setDealSearchTerm('');
      // Show a message that they can manually select any won deal
      setShowNoDealsMessage(true);
    } else if (accountDeals.length === 1) {
      // Only one deal - auto-select it
      const deal = accountDeals[0];
      setSelectedDeal(deal);
      setDealSearchTerm(`${deal.title} ($${formatCurrency(deal.value)})`);
      setInvoiceForm(prev => ({
        ...prev,
        customer_account_id: account.id.toString(),
        deal_id: deal.id.toString(),
        subtotal: deal.value.toString()
      }));
    } else {
      // Multiple deals - show selection dialog
      setInvoiceForm(prev => ({
        ...prev,
        customer_account_id: account.id.toString(),
        deal_id: '',
        subtotal: ''
      }));
      setSelectedDeal(null);
      setDealSearchTerm('');
      setShowDealSelectionModal(true);
      setAccountDealsForSelection(accountDeals);
    }
  };

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/invoices');
      setInvoices(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching invoices:', err);
      setError('Failed to fetch invoices');
    } finally {
      setLoading(false);
    }
  };

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/payments');
      setPayments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching payments:', err);
      setError('Failed to fetch payments');
    } finally {
      setLoading(false);
    }
  };

  const fetchRevenue = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/revenue');
      setRevenue(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching revenue:', err);
      setError('Failed to fetch revenue');
    } finally {
      setLoading(false);
    }
  };

  const fetchReports = async () => {
    try {
      const data = await apiRequest('/api/financial/reports');
      setReports(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching reports:', err);
    }
  };

  const handleCreateRevenue = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Check for duplicate revenue entry
      const invoiceId = parseInt(revenueForm.invoice_id);
      const existingRevenue = revenue.find(r => r.invoice_id === invoiceId);
      
      if (existingRevenue) {
        setError('Revenue for this invoice has already been recognized');
        setSuccessMessage('Revenue for this invoice has already been recognized. Please select a different invoice.');
        setShowSuccessModal(true);
        setLoading(false);
        return;
      }
      
      const revenueData = {
        ...revenueForm,
        invoice_id: invoiceId,
        amount: parseFloat(revenueForm.amount),
        recognition_date: revenueForm.recognition_date + 'T00:00:00Z'
      };
      
      const response = await apiRequest('/api/revenue/recognize', {
        method: 'POST',
        body: JSON.stringify(revenueData)
      });
      
      setError(null);
      setSuccessMessage('Revenue recognized successfully!');
      setShowSuccessModal(true);
      
      setShowCreateRevenue(false);
      setRevenueForm({
        invoice_id: '',
        amount: '',
        recognition_date: '',
        recognition_type: 'immediate',
        recognition_period: '',
        revenue_type: 'product',
        revenue_category: '',
        notes: ''
      });
      
      // Reset revenue form states
      setInvoiceSearchTermForRevenue('');
      setSelectedInvoiceForRevenue(null);
      setShowInvoiceDropdownForRevenue(false);
      
      setActiveTab('revenue');
      fetchRevenue();
      fetchAvailableInvoicesForRevenue(); // Refresh available invoices to exclude the newly recognized one
    } catch (err) {
      console.error('Error creating revenue:', err);
      setError('Failed to recognize revenue');
      setSuccessMessage('Failed to recognize revenue. Please try again.');
      setShowSuccessModal(true);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const reportData = {
        ...reportForm,
        start_date: reportForm.start_date + 'T00:00:00Z',
        end_date: reportForm.end_date + 'T23:59:59Z'
      };
      
      const response = await apiRequest('/api/financial/reports/generate', {
        method: 'POST',
        body: JSON.stringify(reportData)
      });
      
      setError(null);
      setSuccessMessage('Financial report generated successfully!');
      setShowSuccessModal(true);
      
      setShowGenerateReport(false);
      setReportForm({
        report_type: 'profit_loss',
        report_name: '',
        start_date: '',
        end_date: '',
        include_charts: true
      });
      
      setActiveTab('reports');
      fetchReports();
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report');
      setSuccessMessage('Failed to generate report. Please try again.');
      setShowSuccessModal(true);
    } finally {
      setLoading(false);
    }
  };

  const selectDealFromModal = (deal: Deal) => {
    setSelectedDeal(deal);
    setDealSearchTerm(`${deal.title} ($${formatCurrency(deal.value)})`);
    setInvoiceForm(prev => ({
      ...prev,
      deal_id: deal.id.toString(),
      subtotal: deal.value.toString()
    }));
    setShowDealSelectionModal(false);
  };

  // Calculate grand total with discount and tax
  const calculateGrandTotal = () => {
    const subtotal = parseFloat(invoiceForm.subtotal) || 0;
    const taxRate = parseFloat(invoiceForm.tax_rate) || 0;
    const advancePayment = parseFloat(invoiceForm.advance_payment) || 0;
    
    let discountAmount = 0;
    if (invoiceForm.discount_amount) {
      const discount = parseFloat(invoiceForm.discount_amount) || 0;
      if (invoiceForm.discount_type === 'percentage') {
        discountAmount = (subtotal * discount) / 100;
      } else {
        discountAmount = discount;
      }
    }
    
    const afterDiscount = subtotal - discountAmount;
    const taxAmount = (afterDiscount * taxRate) / 100;
    const grandTotal = afterDiscount + taxAmount - advancePayment;
    
    return {
      subtotal,
      discountAmount,
      afterDiscount,
      taxAmount,
      advancePayment,
      grandTotal: Math.max(0, grandTotal) // Ensure non-negative
    };
  };

  const resetInvoiceForm = () => {
    setInvoiceForm({
      deal_id: '',
      customer_account_id: '',
      due_date: '',
      subtotal: '',
      tax_rate: '',
      discount_amount: '',
      discount_type: 'percentage',
      advance_payment: '',
      recurring_invoice: false,
      recurring_frequency: 'monthly',
      recurring_end_date: '',
      description: '',
      notes: '',
      terms_conditions: ''
    });
    setDealSearchTerm('');
    setAccountSearchTerm('');
    setSelectedDeal(null);
    setSelectedAccount(null);
    setShowDealDropdown(false);
    setShowAccountDropdown(false);
    setShowDealSelectionModal(false);
    setAccountDealsForSelection([]);
    setShowNoDealsMessage(false);
    
    // Reset payment form states
    setInvoiceSearchTerm('');
    setSelectedInvoiceForPayment(null);
    setShowInvoiceDropdown(false);
    
    // Reset revenue form states
    setInvoiceSearchTermForRevenue('');
    setSelectedInvoiceForRevenue(null);
    setShowInvoiceDropdownForRevenue(false);
  };

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      // Convert string values to proper types for backend
      const invoiceData = {
        ...invoiceForm,
        deal_id: invoiceForm.deal_id ? parseInt(invoiceForm.deal_id) : null,
        customer_account_id: invoiceForm.customer_account_id ? parseInt(invoiceForm.customer_account_id) : null,
        subtotal: parseFloat(invoiceForm.subtotal) || 0,
        tax_rate: parseFloat(invoiceForm.tax_rate) || 0
      };
      
      const response = await apiRequest('/api/invoices', {
        method: 'POST',
        body: JSON.stringify(invoiceData)
      });
      
      // Show success message
      setError(null);
      setSuccessMessage('Invoice created successfully!');
      setShowSuccessModal(true);
      
      setShowCreateInvoice(false);
      resetInvoiceForm();
      
      // Switch to invoices tab to show the new invoice
      setActiveTab('invoices');
      fetchInvoices();
    } catch (err) {
      console.error('Error creating invoice:', err);
      setError('Failed to create invoice');
      setSuccessMessage('Failed to create invoice. Please try again.');
      setShowSuccessModal(true);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Convert string values to proper types for backend
      const paymentData = {
        ...paymentForm,
        invoice_id: parseInt(paymentForm.invoice_id),
        amount: parseFloat(paymentForm.amount),
        payment_date: paymentForm.payment_date + 'T00:00:00Z' // Convert to ISO format
      };
      
      const response = await apiRequest('/api/payments', {
        method: 'POST',
        body: JSON.stringify(paymentData)
      });
      
      // Show success message
      setError(null);
      setSuccessMessage('Payment recorded successfully!');
      setShowSuccessModal(true);
      
      setShowCreatePayment(false);
      setPaymentForm({
        invoice_id: '',
        amount: '',
        payment_date: '',
        payment_method: 'credit_card',
        payment_reference: '',
        notes: ''
      });
      
      // Reset payment form states
      setInvoiceSearchTerm('');
      setSelectedInvoiceForPayment(null);
      setShowInvoiceDropdown(false);
      
      // Switch to payments tab and refresh data
      setActiveTab('payments');
      fetchPayments();
      fetchAvailableInvoices(); // Refresh available invoices
      fetchInvoices(); // Refresh invoices to update payment status
    } catch (err) {
      console.error('Error creating payment:', err);
      setError('Failed to create payment');
      setSuccessMessage('Failed to record payment. Please try again.');
      setShowSuccessModal(true);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateInvoiceStatus = async (invoiceId: number, status: string) => {
    try {
      await apiRequest(`/api/invoices/${invoiceId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
      });
      fetchInvoices();
    } catch (err) {
      console.error('Error updating invoice status:', err);
      setError('Failed to update invoice status');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800';
      case 'sent': return 'bg-blue-100 text-blue-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid': return <CheckCircle className="w-4 h-4" />;
      case 'sent': return <Send className="w-4 h-4" />;
      case 'overdue': return <AlertTriangle className="w-4 h-4" />;
      case 'draft': return <Edit className="w-4 h-4" />;
      case 'cancelled': return <Trash2 className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: <BarChart3 className="w-5 h-5" /> },
    { id: 'invoices', name: 'Invoices', icon: <FileText className="w-5 h-5" /> },
    { id: 'payments', name: 'Payments', icon: <CreditCard className="w-5 h-5" /> },
    { id: 'revenue', name: 'Revenue', icon: <TrendingUp className="w-5 h-5" /> },
    { id: 'profit-loss', name: 'P&L Statement', icon: <BarChart className="w-5 h-5" /> },
    { id: 'cash-flow', name: 'Cash Flow', icon: <TrendingUp className="w-5 h-5" /> },
    { id: 'aging', name: 'Aging Reports', icon: <Clock className="w-5 h-5" /> },
    { id: 'reports', name: 'Legacy Reports', icon: <PieChart className="w-5 h-5" /> },
    { id: 'settings', name: 'Settings', icon: <Settings className="w-5 h-5" /> }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Financial Management
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage invoices, payments, revenue recognition, and financial reporting
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              {tab.icon}
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-500 hover:text-red-700"
          >
            ×
          </button>
        </div>
      )}

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : dashboard ? (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Revenue</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {formatCurrency(dashboard.revenue_metrics?.total_revenue || 0)}
                      </p>
                    </div>
                    <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
                      <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm">
                    <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                    <span className="text-green-600 dark:text-green-400">
                      +{dashboard.revenue_metrics?.revenue_growth || 0}% from last month
                    </span>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Outstanding Amount</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {formatCurrency(dashboard.outstanding_amounts?.total_outstanding || 0)}
                      </p>
                    </div>
                    <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                      <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                    {dashboard.invoice_metrics?.overdue_invoices || 0} overdue invoices
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Collection Rate</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {(dashboard.invoice_metrics?.collection_rate || 0).toFixed(1)}%
                      </p>
                    </div>
                    <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
                      <CheckCircle className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                    {dashboard.invoice_metrics?.paid_invoices || 0} of {dashboard.invoice_metrics?.total_invoices || 0} invoices paid
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Payment Success Rate</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">
                        {(dashboard.payment_metrics?.payment_success_rate || 0).toFixed(1)}%
                      </p>
                    </div>
                    <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
                      <CreditCard className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                  <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                    Avg. {dashboard.payment_metrics?.average_payment_time || 0} days to payment
                  </div>
                </div>
              </div>

              {/* Enhanced Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Revenue Trend</h3>
                    <div className="flex items-center text-sm text-green-600 dark:text-green-400">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      +12.5% vs last month
                    </div>
                  </div>
                  <div className="h-64">
                    <div className="flex items-end justify-between h-full space-x-2">
                      {revenueTrend.map((item, index) => (
                        <div key={index} className="flex flex-col items-center flex-1">
                          <div 
                            className="bg-blue-500 rounded-t w-full mb-2 transition-all duration-300 hover:bg-blue-600"
                            style={{ height: `${(item.revenue / 70000) * 200}px` }}
                            title={`${item.month}: ${formatCurrency(item.revenue)}`}
                          ></div>
                          <span className="text-xs text-gray-600 dark:text-gray-400">{item.month}</span>
                          <span className="text-xs font-medium text-gray-900 dark:text-white">
                            {formatCurrency(item.revenue / 1000)}k
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payment Methods</h3>
                  <div className="h-64">
                    <div className="space-y-4">
                      {paymentMethods.map((method, index) => {
                        const colors = ['bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500'];
                        const totalAmount = paymentMethods.reduce((sum, m) => sum + m.amount, 0);
                        const percentage = (method.amount / totalAmount) * 100;
                        
                        return (
                          <div key={index} className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div className={`w-4 h-4 rounded-full ${colors[index]} mr-3`}></div>
                              <span className="text-sm font-medium text-gray-900 dark:text-white">
                                {method.method}
                              </span>
                            </div>
                            <div className="flex items-center space-x-3">
                              <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${colors[index]}`}
                                  style={{ width: `${percentage}%` }}
                                ></div>
                              </div>
                              <span className="text-sm text-gray-600 dark:text-gray-400 w-16 text-right">
                                {formatCurrency(method.amount)}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {/* Additional Dashboard Sections */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Invoice Status Breakdown */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Invoice Status</h3>
                  <div className="space-y-3">
                    {invoiceStatusBreakdown.map((status, index) => {
                      const colors = ['text-green-600', 'text-blue-600', 'text-red-600', 'text-gray-600'];
                      const bgColors = ['bg-green-100', 'bg-blue-100', 'bg-red-100', 'bg-gray-100'];
                      const darkColors = ['dark:text-green-400', 'dark:text-blue-400', 'dark:text-red-400', 'dark:text-gray-400'];
                      const darkBgColors = ['dark:bg-green-900', 'dark:bg-blue-900', 'dark:bg-red-900', 'dark:bg-gray-900'];
                      
                      return (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className={`w-3 h-3 rounded-full ${bgColors[index]} ${darkBgColors[index]} mr-3`}></div>
                            <span className={`text-sm font-medium ${colors[index]} ${darkColors[index]}`}>
                              {status.status}
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {status.count}
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">
                              {formatCurrency(status.amount)}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Recent Activities */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Activities</h3>
                    <Activity className="w-5 h-5 text-gray-400" />
                  </div>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {recentActivities.length > 0 ? (
                      recentActivities.map((activity) => {
                        const IconComponent = activity.icon;
                        const colorClasses = {
                          blue: 'text-blue-600 dark:text-blue-400',
                          green: 'text-green-600 dark:text-green-400',
                          purple: 'text-purple-600 dark:text-purple-400'
                        };
                        
                        return (
                          <div key={activity.id} className="flex items-start space-x-3">
                            <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-700`}>
                              <IconComponent className={`w-4 h-4 ${colorClasses[activity.color as keyof typeof colorClasses]}`} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {activity.title}
                              </p>
                              <p className="text-xs text-gray-600 dark:text-gray-400">
                                {activity.description}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-500">
                                {activity.timestamp.toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center py-4">
                        <Activity className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">No recent activities</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    <button
                      onClick={() => setShowCreateInvoice(true)}
                      className="w-full flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                    >
                      <div className="flex items-center">
                        <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3" />
                        <span className="text-sm font-medium text-blue-900 dark:text-blue-100">Create Invoice</span>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    </button>

                    <button
                      onClick={() => setShowCreatePayment(true)}
                      className="w-full flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
                    >
                      <div className="flex items-center">
                        <CreditCard className="w-5 h-5 text-green-600 dark:text-green-400 mr-3" />
                        <span className="text-sm font-medium text-green-900 dark:text-green-100">Record Payment</span>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-green-600 dark:text-green-400" />
                    </button>

                    <button
                      onClick={() => setShowCreateRevenue(true)}
                      className="w-full flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
                    >
                      <div className="flex items-center">
                        <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400 mr-3" />
                        <span className="text-sm font-medium text-purple-900 dark:text-purple-100">Recognize Revenue</span>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                    </button>

                    <button
                      onClick={() => setShowGenerateReport(true)}
                      className="w-full flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-colors"
                    >
                      <div className="flex items-center">
                        <BarChart3 className="w-5 h-5 text-orange-600 dark:text-orange-400 mr-3" />
                        <span className="text-sm font-medium text-orange-900 dark:text-orange-100">Generate Report</span>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">No dashboard data available</p>
            </div>
          )}
        </div>
      )}

      {/* Invoices Tab */}
      {activeTab === 'invoices' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Invoices</h2>
            <button
              onClick={() => setShowCreateInvoice(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Invoice
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Invoice
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Due Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {invoices.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center space-y-3">
                            <FileText className="w-12 h-12 text-gray-400" />
                            <div>
                              <h3 className="text-lg font-medium text-gray-900 dark:text-white">No invoices found</h3>
                              <p className="text-gray-500 dark:text-gray-400">Get started by creating your first invoice.</p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      invoices.map((invoice) => (
                      <tr key={invoice.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {invoice.invoice_number}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Deal #{invoice.deal_id}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 dark:text-white">
                            {formatCurrency(invoice.total_amount)}
                          </div>
                          {invoice.balance_due > 0 && (
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Balance: {formatCurrency(invoice.balance_due)}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(invoice.status)}`}>
                            {getStatusIcon(invoice.status)}
                            {invoice.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {formatDate(invoice.due_date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => {
                                setSelectedInvoice(invoice);
                                setShowInvoiceDetails(true);
                              }}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            {invoice.status === 'draft' && (
                              <button
                                onClick={() => handleUpdateInvoiceStatus(invoice.id, 'sent')}
                                className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                              >
                                <Send className="w-4 h-4" />
                              </button>
                            )}
                            {invoice.status === 'sent' && (
                              <button
                                onClick={() => handleUpdateInvoiceStatus(invoice.id, 'paid')}
                                className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                              >
                                <CheckCircle className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Payments Tab */}
      {activeTab === 'payments' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Payments</h2>
            <button
              onClick={() => setShowCreatePayment(true)}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Record Payment
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Payment
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Method
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {payments.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center space-y-3">
                            <CreditCard className="w-12 h-12 text-gray-400" />
                            <div>
                              <h3 className="text-lg font-medium text-gray-900 dark:text-white">No payments found</h3>
                              <p className="text-gray-500 dark:text-gray-400">Record payments for your invoices to get started.</p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      payments.map((payment) => (
                      <tr key={payment.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {payment.payment_number}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Invoice #{payment.invoice_id}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {formatCurrency(payment.amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {payment.payment_method.replace('_', ' ')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {formatDate(payment.payment_date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(payment.status)}`}>
                            {getStatusIcon(payment.status)}
                            {payment.status}
                          </span>
                        </td>
                      </tr>
                    ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Revenue Tab */}
      {activeTab === 'revenue' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Revenue Recognition</h2>
            <button
              onClick={() => setShowCreateRevenue(true)}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Recognize Revenue
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Revenue Entry
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Recognition Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {revenue.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center space-y-3">
                            <TrendingUp className="w-12 h-12 text-gray-400" />
                            <div>
                              <h3 className="text-lg font-medium text-gray-900 dark:text-white">No revenue entries found</h3>
                              <p className="text-gray-500 dark:text-gray-400">Recognize revenue from your paid invoices to get started.</p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      revenue.map((entry) => (
                      <tr key={entry.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              Invoice #{entry.invoice_id}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              Deal #{entry.deal_id}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {formatCurrency(entry.amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {entry.revenue_type} - {entry.revenue_category || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {formatDate(entry.recognition_date)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(entry.status)}`}>
                            {getStatusIcon(entry.status)}
                            {entry.status}
                          </span>
                        </td>
                      </tr>
                    ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reports Tab */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Financial Reports</h2>
            <button
              onClick={() => setShowGenerateReport(true)}
              className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Generate Report
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Report Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Period
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Generated
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {reports.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center space-y-3">
                            <PieChart className="w-12 h-12 text-gray-400" />
                            <div>
                              <h3 className="text-lg font-medium text-gray-900 dark:text-white">No reports generated yet</h3>
                              <p className="text-gray-500 dark:text-gray-400">Generate your first financial report to get started.</p>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      reports.map((report) => (
                        <tr key={report.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {report.report_name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              {report.report_type.replace('_', ' ').toUpperCase()}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {report.report_period}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                            {formatDate(report.created_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                              {getStatusIcon(report.status)}
                              {report.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <div className="flex space-x-2">
                              <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">
                                View
                              </button>
                              <button className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">
                                Export
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Profit & Loss Statement Tab */}
      {activeTab === 'profit-loss' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Profit & Loss Statement</h2>
            <div className="flex gap-2">
              <input
                type="date"
                value={reportDateRange.start_date}
                onChange={(e) => setReportDateRange({...reportDateRange, start_date: e.target.value})}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
              <input
                type="date"
                value={reportDateRange.end_date}
                onChange={(e) => setReportDateRange({...reportDateRange, end_date: e.target.value})}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
              <Button
                variant="primary"
                onClick={() => fetchProfitLossReport(reportDateRange.start_date, reportDateRange.end_date)}
                disabled={reportLoading}
              >
                {reportLoading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>
          </div>

          {reportLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Generating report...</span>
            </div>
          ) : profitLossData && !profitLossData.error ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  P&L Statement for {profitLossData.report_period?.start_date} to {profitLossData.report_period?.end_date}
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Revenue */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Total Revenue</span>
                  <span className="font-semibold text-green-600 dark:text-green-400">
                    {formatCurrency(profitLossData.revenue?.total_revenue || 0)}
                  </span>
                </div>
                
                {/* Cost of Goods Sold */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="text-gray-700 dark:text-gray-300 ml-4">Cost of Goods Sold</span>
                  <span className="text-red-600 dark:text-red-400">
                    {formatCurrency(profitLossData.cost_of_goods_sold?.total_cogs || 0)}
                  </span>
                </div>
                
                {/* Gross Profit */}
                <div className="flex justify-between items-center py-2 border-b-2 border-gray-300 dark:border-gray-600">
                  <span className="font-semibold text-gray-900 dark:text-white">Gross Profit</span>
                  <span className="font-semibold text-blue-600 dark:text-blue-400">
                    {formatCurrency(profitLossData.gross_profit?.amount || 0)}
                  </span>
                </div>
                
                {/* Operating Expenses */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="text-gray-700 dark:text-gray-300 ml-4">Operating Expenses</span>
                  <span className="text-red-600 dark:text-red-400">
                    {formatCurrency(profitLossData.operating_expenses?.amount || 0)}
                  </span>
                </div>
                
                {/* Operating Income */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Operating Income</span>
                  <span className="font-medium text-blue-600 dark:text-blue-400">
                    {formatCurrency(profitLossData.operating_income?.amount || 0)}
                  </span>
                </div>
                
                {/* Net Income */}
                <div className="flex justify-between items-center py-2 border-b-2 border-gray-300 dark:border-gray-600">
                  <span className="font-bold text-gray-900 dark:text-white">Net Income</span>
                  <span className="font-bold text-green-600 dark:text-green-400">
                    {formatCurrency(profitLossData.net_income?.amount || 0)}
                  </span>
                </div>
              </div>
              
              {/* Key Metrics */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Gross Profit Margin</h4>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {profitLossData.gross_profit?.margin_percentage || 0}%
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Operating Margin</h4>
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {profitLossData.operating_income?.margin_percentage || 0}%
                  </p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Net Margin</h4>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {profitLossData.net_income?.margin_percentage || 0}%
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6 text-center">
              <p className="text-gray-600 dark:text-gray-400">No data available for the selected period.</p>
            </div>
          )}
        </div>
      )}

      {/* Cash Flow Statement Tab */}
      {activeTab === 'cash-flow' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Cash Flow Statement</h2>
            <div className="flex gap-2">
              <input
                type="date"
                value={reportDateRange.start_date}
                onChange={(e) => setReportDateRange({...reportDateRange, start_date: e.target.value})}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
              <input
                type="date"
                value={reportDateRange.end_date}
                onChange={(e) => setReportDateRange({...reportDateRange, end_date: e.target.value})}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
              <Button
                variant="primary"
                onClick={() => fetchCashFlowReport(reportDateRange.start_date, reportDateRange.end_date)}
                disabled={reportLoading}
              >
                {reportLoading ? 'Loading...' : 'Refresh'}
              </Button>
            </div>
          </div>

          {reportLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Generating report...</span>
            </div>
          ) : cashFlowData && !cashFlowData.error ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  Cash Flow Statement for {cashFlowData.report_period?.start_date} to {cashFlowData.report_period?.end_date}
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Beginning Cash */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Beginning Cash</span>
                  <span className="font-semibold text-gray-600 dark:text-gray-400">
                    {formatCurrency(cashFlowData.beginning_cash || 0)}
                  </span>
                </div>
                
                {/* Cash from Operations */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Cash from Operations</span>
                  <span className="font-semibold text-green-600 dark:text-green-400">
                    {formatCurrency(cashFlowData.cash_from_operations?.amount || 0)}
                  </span>
                </div>
                
                {/* Cash from Investing */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Cash from Investing</span>
                  <span className="font-semibold text-blue-600 dark:text-blue-400">
                    {formatCurrency(cashFlowData.cash_from_investing?.amount || 0)}
                  </span>
                </div>
                
                {/* Cash from Financing */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Cash from Financing</span>
                  <span className="font-semibold text-purple-600 dark:text-purple-400">
                    {formatCurrency(cashFlowData.cash_from_financing?.amount || 0)}
                  </span>
                </div>
                
                {/* Cash Outflows */}
                <div className="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span className="font-medium text-gray-900 dark:text-white">Cash Outflows</span>
                  <span className="font-semibold text-red-600 dark:text-red-400">
                    {formatCurrency(cashFlowData.cash_outflows?.amount || 0)}
                  </span>
                </div>
                
                {/* Net Cash Flow */}
                <div className="flex justify-between items-center py-2 border-b-2 border-gray-300 dark:border-gray-600">
                  <span className="font-bold text-gray-900 dark:text-white">Net Cash Flow</span>
                  <span className={`font-bold ${(cashFlowData.net_cash_flow || 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {formatCurrency(cashFlowData.net_cash_flow || 0)}
                  </span>
                </div>
                
                {/* Ending Cash */}
                <div className="flex justify-between items-center py-2 border-b-2 border-gray-300 dark:border-gray-600">
                  <span className="font-bold text-gray-900 dark:text-white">Ending Cash</span>
                  <span className="font-bold text-blue-600 dark:text-blue-400">
                    {formatCurrency(cashFlowData.ending_cash || 0)}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6 text-center">
              <p className="text-gray-600 dark:text-gray-400">No data available for the selected period.</p>
            </div>
          )}
        </div>
      )}

      {/* Aging Reports Tab */}
      {activeTab === 'aging' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Aging Reports</h2>
            <Button
              variant="primary"
              onClick={() => fetchAgingReport('receivables')}
              disabled={reportLoading}
            >
              {reportLoading ? 'Loading...' : 'Refresh'}
            </Button>
          </div>

          {reportLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Generating report...</span>
            </div>
          ) : agingData && !agingData.error ? (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-4">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Current</h3>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {formatCurrency(agingData.aging_summary?.current?.amount || 0)}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {agingData.aging_summary?.current?.count || 0} invoices
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-4">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">1-30 Days</h3>
                  <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {formatCurrency(agingData.aging_summary?.days_1_30?.amount || 0)}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {agingData.aging_summary?.days_1_30?.count || 0} invoices
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-4">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">31-60 Days</h3>
                  <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {formatCurrency(agingData.aging_summary?.days_31_60?.amount || 0)}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {agingData.aging_summary?.days_31_60?.count || 0} invoices
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-4">
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">90+ Days</h3>
                  <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {formatCurrency(agingData.aging_summary?.days_90_plus?.amount || 0)}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {agingData.aging_summary?.days_90_plus?.count || 0} invoices
                  </p>
                </div>
              </div>

              {/* Detailed Invoices */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Detailed Invoice Aging</h3>
                
                {/* Current Invoices */}
                {agingData.detailed_invoices?.current?.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-medium text-green-600 dark:text-green-400 mb-3">Current (0 days overdue)</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Invoice</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Customer</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Amount</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Due Date</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {agingData.detailed_invoices.current.map((invoice: any) => (
                            <tr key={invoice.id}>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{invoice.invoice_number}</td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{invoice.customer_name}</td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{formatCurrency(invoice.outstanding_amount)}</td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{invoice.due_date}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Overdue Invoices */}
                {agingData.detailed_invoices?.days_1_30?.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-medium text-yellow-600 dark:text-yellow-400 mb-3">1-30 Days Overdue</h4>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Invoice</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Customer</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Amount</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Days Overdue</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {agingData.detailed_invoices.days_1_30.map((invoice: any) => (
                            <tr key={invoice.id}>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{invoice.invoice_number}</td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{invoice.customer_name}</td>
                              <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{formatCurrency(invoice.outstanding_amount)}</td>
                              <td className="px-4 py-3 text-sm text-yellow-600 dark:text-yellow-400">{invoice.days_overdue} days</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6 text-center">
              <p className="text-gray-600 dark:text-gray-400">No aging data available.</p>
            </div>
          )}
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Company Settings</h2>
          
          {settingsLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Loading settings...</span>
            </div>
          ) : (
            <>
          
          {/* General Information Section */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">General Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Company Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  value={companyForm.company_name}
                  onChange={(e) => setCompanyForm({...companyForm, company_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter company name"
                />
              </div>

              {/* Company Mobile */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Company Mobile
                </label>
                <input
                  type="tel"
                  value={companyForm.company_mobile}
                  onChange={(e) => setCompanyForm({...companyForm, company_mobile: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter mobile number"
                />
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  City
                </label>
                <input
                  type="text"
                  value={companyForm.city}
                  onChange={(e) => setCompanyForm({...companyForm, city: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter city"
                />
              </div>

              {/* Area */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Area
                </label>
                <input
                  type="text"
                  value={companyForm.area}
                  onChange={(e) => setCompanyForm({...companyForm, area: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter area"
                />
              </div>

              {/* Complete Address - Full width */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Complete Address
                </label>
                <textarea
                  value={companyForm.complete_address}
                  onChange={(e) => setCompanyForm({...companyForm, complete_address: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter complete address"
                />
              </div>

              {/* TRN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  TRN
                </label>
                <input
                  type="text"
                  value={companyForm.trn}
                  onChange={(e) => setCompanyForm({...companyForm, trn: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter Tax Registration Number"
                />
              </div>

              {/* Currency */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Currency
                </label>
                <select
                  value={companyForm.currency}
                  onChange={(e) => setCompanyForm({...companyForm, currency: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="AED - UAE Dirham (د.إ)">AED - UAE Dirham (د.إ)</option>
                  <option value="USD - US Dollar ($)">USD - US Dollar ($)</option>
                  <option value="EUR - Euro (€)">EUR - Euro (€)</option>
                  <option value="GBP - British Pound (£)">GBP - British Pound (£)</option>
                  <option value="SAR - Saudi Riyal (﷼)">SAR - Saudi Riyal (﷼)</option>
                  <option value="KWD - Kuwaiti Dinar (د.ك)">KWD - Kuwaiti Dinar (د.ك)</option>
                </select>
              </div>

              {/* Timezone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Timezone
                </label>
                <select
                  value={companyForm.timezone}
                  onChange={(e) => setCompanyForm({...companyForm, timezone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="Dubai (UAE)">Dubai (UAE)</option>
                  <option value="Abu Dhabi (UAE)">Abu Dhabi (UAE)</option>
                  <option value="New York (USA)">New York (USA)</option>
                  <option value="London (UK)">London (UK)</option>
                  <option value="Paris (France)">Paris (France)</option>
                  <option value="Tokyo (Japan)">Tokyo (Japan)</option>
                  <option value="Singapore">Singapore</option>
                </select>
              </div>
            </div>
          </div>

          {/* Billing Configuration Section */}
          <div className="bg-gradient-to-r from-blue-900 to-blue-800 rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white">Billing Configuration</h3>
            </div>
            
            <div className="space-y-4">
              {/* Trial Date */}
              <div className="bg-blue-800 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={billingConfig.trial_date_enabled}
                    onChange={(e) => setBillingConfig({...billingConfig, trial_date_enabled: e.target.checked})}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="text-white font-medium">Trial Date</span>
                </div>
                {billingConfig.trial_date_enabled && (
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={billingConfig.trial_date_days}
                      onChange={(e) => setBillingConfig({...billingConfig, trial_date_days: e.target.value})}
                      className="w-16 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      min="1"
                      max="30"
                    />
                    <span className="text-white text-sm">days</span>
                  </div>
                )}
              </div>

              {/* Delivery Date */}
              <div className="bg-blue-800 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={billingConfig.delivery_date_enabled}
                    onChange={(e) => setBillingConfig({...billingConfig, delivery_date_enabled: e.target.checked})}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="text-white font-medium">Delivery Date</span>
                </div>
                {billingConfig.delivery_date_enabled && (
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={billingConfig.delivery_date_days}
                      onChange={(e) => setBillingConfig({...billingConfig, delivery_date_days: e.target.value})}
                      className="w-16 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      min="1"
                      max="30"
                    />
                    <span className="text-white text-sm">days</span>
                  </div>
                )}
              </div>

              {/* Advance Payment */}
              <div className="bg-green-800 rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={billingConfig.advance_payment_enabled}
                    onChange={(e) => setBillingConfig({...billingConfig, advance_payment_enabled: e.target.checked})}
                    className="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <span className="text-white font-medium">Advance Payment</span>
                </div>
                <span className="text-gray-300 text-sm">Allow partial payments</span>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button
              variant="primary"
              onClick={async () => {
                try {
                  // Prepare settings data
                  const settingsData = {
                    company_name: companyForm.company_name,
                    company_mobile: companyForm.company_mobile,
                    city: companyForm.city,
                    area: companyForm.area,
                    complete_address: companyForm.complete_address,
                    trn: companyForm.trn,
                    currency: companyForm.currency,
                    timezone: companyForm.timezone,
                    trial_date_enabled: billingConfig.trial_date_enabled,
                    trial_date_days: parseInt(billingConfig.trial_date_days),
                    delivery_date_enabled: billingConfig.delivery_date_enabled,
                    delivery_date_days: parseInt(billingConfig.delivery_date_days),
                    advance_payment_enabled: billingConfig.advance_payment_enabled
                  };

                  // Save settings
                  await companySettingsService.updateSettings(settingsData);
                  
                  setSuccessMessage('Settings saved successfully!');
                  setShowSuccessModal(true);
                  
                  // Reload settings to get updated data
                  fetchCompanySettings();
                  
                } catch (error) {
                  console.error('Error saving settings:', error);
                  setError('Failed to save settings. Please try again.');
                }
              }}
              className="px-6 py-2"
              disabled={settingsLoading}
            >
              {settingsLoading ? 'Saving...' : 'Save Settings'}
            </Button>
          </div>
            </>
          )}
        </div>
      )}

      {/* Create Invoice Modal */}
      <AnimatedModal
        open={showCreateInvoice}
        onClose={() => {
          setShowCreateInvoice(false);
          resetInvoiceForm();
        }}
        title="Create Invoice"
        animationType="scale"
        size="xl"
      >
        <form onSubmit={handleCreateInvoice} className="space-y-6">
          {/* Row 1: Customer Account & Won Deal */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative dropdown-container">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Customer Account *
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={accountSearchTerm}
                  onChange={(e) => {
                    handleAccountSearch(e.target.value);
                    setShowAccountDropdown(true);
                  }}
                  onFocus={() => setShowAccountDropdown(true)}
                  placeholder="Search customer accounts..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  required
                />
                {showAccountDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto">
                    {filteredAccounts.length > 0 ? (
                      filteredAccounts.map((account) => (
                        <div
                          key={account.id}
                          onClick={() => selectAccount(account)}
                          className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                        >
                          <div className="font-medium text-gray-900 dark:text-white">
                            {account.account_name}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            Account #{account.id}
                            {account.contact_name && ` • ${account.contact_name}`}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="px-3 py-2 text-gray-500 dark:text-gray-400">
                        No customer accounts found
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="relative dropdown-container">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Won Deal {!showNoDealsMessage && <span className="text-red-500">*</span>}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={dealSearchTerm}
                  onChange={(e) => {
                    handleDealSearch(e.target.value);
                    setShowDealDropdown(true);
                  }}
                  onFocus={() => setShowDealDropdown(true)}
                  placeholder="Search won deals..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
                {showDealDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto">
                    {filteredDeals.length > 0 ? (
                      filteredDeals.map((deal) => (
                        <div
                          key={deal.id}
                          onClick={() => selectDeal(deal)}
                          className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                        >
                          <div className="font-medium text-gray-900 dark:text-white">
                            {deal.title}
                          </div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            Deal #{deal.id} • {formatCurrency(deal.value)}
                            {deal.contact_name && ` • ${deal.contact_name}`}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="px-3 py-2 text-gray-500 dark:text-gray-400">
                        {dealSearchTerm ? 'No won deals found matching your search' : 'No won deals found'}
                      </div>
                    )}
                  </div>
                )}
                {showNoDealsMessage && !showDealDropdown && (
                  <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                          No won deals for this account
                        </h3>
                        <div className="mt-1 text-sm text-blue-700 dark:text-blue-300">
                          <p>You can still create an invoice by:</p>
                          <ul className="list-disc list-inside mt-1 space-y-1">
                            <li>Searching for any won deal in the system</li>
                            <li>Manually entering the deal details</li>
                            <li>Creating a general invoice for this account</li>
                          </ul>
                          <div className="mt-3">
                            <Button
                              variant="info"
                              size="sm"
                              onClick={() => {
                                setShowNoDealsMessage(false);
                                setShowDealDropdown(true);
                                setDealSearchTerm('');
                                setFilteredDeals(wonDeals);
                              }}
                            >
                              Browse All Won Deals
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Row 2: Due Date & Tax Rate */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Due Date *
              </label>
              <input
                type="date"
                value={invoiceForm.due_date}
                onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tax Rate (%)
              </label>
              <input
                type="number"
                step="0.01"
                value={invoiceForm.tax_rate}
                onChange={(e) => setInvoiceForm({ ...invoiceForm, tax_rate: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="0.00"
              />
            </div>
          </div>

          {/* Row 3: Subtotal & Discount */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Subtotal *
              </label>
              <input
                type="number"
                step="0.01"
                value={invoiceForm.subtotal}
                onChange={(e) => setInvoiceForm({ ...invoiceForm, subtotal: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="0.00"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Discount
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  step="0.01"
                  value={invoiceForm.discount_amount}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, discount_amount: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="0.00"
                />
                <select
                  value={invoiceForm.discount_type}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, discount_type: e.target.value })}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="percentage">%</option>
                  <option value="fixed">$</option>
                </select>
              </div>
            </div>
          </div>

          {/* Row 4: Advance Payment & Recurring Invoice */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Advance Payment
              </label>
              <input
                type="number"
                step="0.01"
                value={invoiceForm.advance_payment}
                onChange={(e) => setInvoiceForm({ ...invoiceForm, advance_payment: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="0.00"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Recurring Invoice
              </label>
              <div className="flex items-center gap-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={invoiceForm.recurring_invoice}
                    onChange={(e) => setInvoiceForm({ ...invoiceForm, recurring_invoice: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Enable Recurring</span>
                </label>
              </div>
            </div>
          </div>

          {/* Recurring Settings (conditional) */}
          {invoiceForm.recurring_invoice && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Frequency
                </label>
                <select
                  value={invoiceForm.recurring_frequency}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, recurring_frequency: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="quarterly">Quarterly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={invoiceForm.recurring_end_date}
                  onChange={(e) => setInvoiceForm({ ...invoiceForm, recurring_end_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          )}

          {/* Grand Total Display */}
          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Invoice Summary</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Subtotal:</span>
                <span className="font-medium">${formatCurrency(calculateGrandTotal().subtotal)}</span>
              </div>
              {calculateGrandTotal().discountAmount > 0 && (
                <div className="flex justify-between text-green-600 dark:text-green-400">
                  <span>Discount:</span>
                  <span>-${formatCurrency(calculateGrandTotal().discountAmount)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Tax:</span>
                <span className="font-medium">${formatCurrency(calculateGrandTotal().taxAmount)}</span>
              </div>
              {calculateGrandTotal().advancePayment > 0 && (
                <div className="flex justify-between text-blue-600 dark:text-blue-400">
                  <span>Advance Payment:</span>
                  <span>-${formatCurrency(calculateGrandTotal().advancePayment)}</span>
                </div>
              )}
              <div className="border-t border-gray-200 dark:border-gray-600 pt-2 flex justify-between">
                <span className="font-semibold text-gray-900 dark:text-white">Grand Total:</span>
                <span className="font-bold text-lg text-blue-600 dark:text-blue-400">
                  ${formatCurrency(calculateGrandTotal().grandTotal)}
                </span>
              </div>
            </div>
          </div>

          {/* Row 5: Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={invoiceForm.description}
              onChange={(e) => setInvoiceForm({ ...invoiceForm, description: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="Invoice description..."
            />
          </div>

          {/* Row 6: Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={invoiceForm.notes}
              onChange={(e) => setInvoiceForm({ ...invoiceForm, notes: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="Additional notes..."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-600">
            <Button
              variant="secondary"
              size="md"
              onClick={() => setShowCreateInvoice(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="md"
              type="submit"
              disabled={loading}
              loading={loading}
            >
              Create Invoice
            </Button>
          </div>
        </form>
      </AnimatedModal>

      {/* Create Payment Modal */}
      <AnimatedModal
        open={showCreatePayment}
        onClose={() => setShowCreatePayment(false)}
        title="Record Payment"
        animationType="scale"
        size="md"
      >
        <form onSubmit={handleCreatePayment} className="space-y-4">
          <div className="relative dropdown-container">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Invoice *
            </label>
            <div className="relative">
              <input
                type="text"
                value={invoiceSearchTerm}
                onChange={(e) => {
                  handleInvoiceSearch(e.target.value);
                  setShowInvoiceDropdown(true);
                }}
                onFocus={() => setShowInvoiceDropdown(true)}
                placeholder="Search unpaid invoices..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
              {showInvoiceDropdown && (
                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto">
                  {filteredInvoices.length > 0 ? (
                    filteredInvoices.map((invoice) => (
                      <div
                        key={invoice.id}
                        onClick={() => selectInvoiceForPayment(invoice)}
                        className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                      >
                        <div className="font-medium text-gray-900 dark:text-white">
                          {invoice.invoice_number}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Deal #{invoice.deal_id} • Balance: {formatCurrency(invoice.balance_due)}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="px-3 py-2 text-gray-500 dark:text-gray-400">
                      No unpaid invoices found
                    </div>
                  )}
                </div>
              )}
            </div>
            {selectedInvoiceForPayment && (
              <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      Invoice Details
                    </h3>
                    <div className="mt-1 text-sm text-blue-700 dark:text-blue-300">
                      <p>Total Amount: {formatCurrency(selectedInvoiceForPayment.total_amount)}</p>
                      <p>Balance Due: {formatCurrency(selectedInvoiceForPayment.balance_due)}</p>
                      <p>Due Date: {formatDate(selectedInvoiceForPayment.due_date)}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Amount
              </label>
              <input
                type="number"
                step="0.01"
                value={paymentForm.amount}
                onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:border-transparent dark:bg-gray-700 dark:text-white ${
                  selectedInvoiceForPayment && parseFloat(paymentForm.amount) > selectedInvoiceForPayment.balance_due
                    ? 'border-red-300 focus:ring-red-500'
                    : 'border-gray-300 focus:ring-blue-500'
                }`}
                required
              />
              {selectedInvoiceForPayment && parseFloat(paymentForm.amount) > selectedInvoiceForPayment.balance_due && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  Payment amount exceeds balance due ({formatCurrency(selectedInvoiceForPayment.balance_due)})
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Payment Date
              </label>
              <input
                type="date"
                value={paymentForm.payment_date}
                onChange={(e) => setPaymentForm({ ...paymentForm, payment_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Payment Method
            </label>
            <select
              value={paymentForm.payment_method}
              onChange={(e) => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              <option value="credit_card">Credit Card</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="check">Check</option>
              <option value="cash">Cash</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Payment Reference
            </label>
            <input
              type="text"
              value={paymentForm.payment_reference}
              onChange={(e) => setPaymentForm({ ...paymentForm, payment_reference: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="Transaction ID, check number, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={paymentForm.notes}
              onChange={(e) => setPaymentForm({ ...paymentForm, notes: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setShowCreatePayment(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Recording...' : 'Record Payment'}
            </button>
          </div>
        </form>
      </AnimatedModal>

      {/* Invoice Details Modal */}
      <AnimatedModal
        open={showInvoiceDetails}
        onClose={() => setShowInvoiceDetails(false)}
        title={selectedInvoice ? `Invoice ${selectedInvoice.invoice_number}` : 'Invoice Details'}
        animationType="slideUp"
        size="lg"
      >
        {selectedInvoice && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedInvoice.status)}`}>
                  {getStatusIcon(selectedInvoice.status)}
                  {selectedInvoice.status}
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Total Amount</label>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(selectedInvoice.total_amount)}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Issue Date</label>
                <p className="text-gray-900 dark:text-white">{formatDate(selectedInvoice.issue_date)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Due Date</label>
                <p className="text-gray-900 dark:text-white">{formatDate(selectedInvoice.due_date)}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Subtotal</label>
                <p className="text-gray-900 dark:text-white">{formatCurrency(selectedInvoice.subtotal)}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Tax ({selectedInvoice.tax_rate}%)</label>
                <p className="text-gray-900 dark:text-white">{formatCurrency(selectedInvoice.tax_amount)}</p>
              </div>
            </div>

            {selectedInvoice.balance_due > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Balance Due</label>
                <p className="text-lg font-semibold text-red-600 dark:text-red-400">
                  {formatCurrency(selectedInvoice.balance_due)}
                </p>
              </div>
            )}

            {selectedInvoice.description && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                <p className="text-gray-900 dark:text-white">{selectedInvoice.description}</p>
              </div>
            )}

            {selectedInvoice.notes && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Notes</label>
                <p className="text-gray-900 dark:text-white">{selectedInvoice.notes}</p>
              </div>
            )}
          </div>
        )}
      </AnimatedModal>

      {/* Deal Selection Modal */}
      <AnimatedModal
        open={showDealSelectionModal}
        onClose={() => setShowDealSelectionModal(false)}
        title="Select Deal"
        animationType="scale"
        size="lg"
      >
        <div className="space-y-4">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            This customer account has multiple won deals. Please select which deal to create an invoice for:
          </div>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {accountDealsForSelection.map((deal) => (
              <div
                key={deal.id}
                onClick={() => selectDealFromModal(deal)}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors duration-200"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {deal.title}
                    </h3>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Deal #{deal.id}
                      {deal.contact_name && ` • ${deal.contact_name}`}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-green-600 dark:text-green-400">
                      {formatCurrency(deal.value)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Won Deal
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex justify-end pt-4">
            <button
              onClick={() => setShowDealSelectionModal(false)}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors duration-200"
            >
              Cancel
            </button>
          </div>
        </div>
      </AnimatedModal>

      {/* Create Revenue Modal */}
      <AnimatedModal
        open={showCreateRevenue}
        onClose={() => setShowCreateRevenue(false)}
        title="Recognize Revenue"
        animationType="scale"
        size="md"
      >
        <form onSubmit={handleCreateRevenue} className="space-y-4">
          <div className="relative dropdown-container">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Invoice *
            </label>
            <div className="relative">
              <input
                type="text"
                value={invoiceSearchTermForRevenue}
                onChange={(e) => {
                  handleInvoiceSearchForRevenue(e.target.value);
                  setShowInvoiceDropdownForRevenue(true);
                }}
                onFocus={() => setShowInvoiceDropdownForRevenue(true)}
                placeholder="Search paid invoices..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
              {showInvoiceDropdownForRevenue && (
                <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto">
                  {filteredInvoicesForRevenue.length > 0 ? (
                    filteredInvoicesForRevenue.map((invoice) => (
                      <div
                        key={invoice.id}
                        onClick={() => selectInvoiceForRevenue(invoice)}
                        className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 last:border-b-0"
                      >
                        <div className="font-medium text-gray-900 dark:text-white">
                          {invoice.invoice_number}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Deal #{invoice.deal_id} • Amount: {formatCurrency(invoice.total_amount)}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="px-3 py-2 text-gray-500 dark:text-gray-400">
                      {availableInvoicesForRevenue.length === 0 
                        ? "No paid invoices available for revenue recognition" 
                        : "No matching invoices found"}
                    </div>
                  )}
                </div>
              )}
            </div>
            {selectedInvoiceForRevenue && (
              <div className="mt-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                      Invoice Details
                    </h3>
                    <div className="mt-1 text-sm text-blue-700 dark:text-blue-300">
                      <p>Total Amount: {formatCurrency(selectedInvoiceForRevenue.total_amount)}</p>
                      <p>Status: {selectedInvoiceForRevenue.status}</p>
                      <p>Due Date: {formatDate(selectedInvoiceForRevenue.due_date)}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Amount *
              </label>
              <input
                type="number"
                step="0.01"
                value={revenueForm.amount}
                onChange={(e) => setRevenueForm({ ...revenueForm, amount: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Recognition Date *
              </label>
              <input
                type="date"
                value={revenueForm.recognition_date}
                onChange={(e) => setRevenueForm({ ...revenueForm, recognition_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Recognition Type
              </label>
              <select
                value={revenueForm.recognition_type}
                onChange={(e) => setRevenueForm({ ...revenueForm, recognition_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="immediate">Immediate</option>
                <option value="deferred">Deferred</option>
                <option value="milestone">Milestone-based</option>
                <option value="subscription">Subscription</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Revenue Type
              </label>
              <select
                value={revenueForm.revenue_type}
                onChange={(e) => setRevenueForm({ ...revenueForm, revenue_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="product">Product</option>
                <option value="service">Service</option>
                <option value="subscription">Subscription</option>
                <option value="consulting">Consulting</option>
                <option value="support">Support</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Revenue Category
            </label>
            <input
              type="text"
              value={revenueForm.revenue_category}
              onChange={(e) => setRevenueForm({ ...revenueForm, revenue_category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="e.g., Software License, Implementation, Training"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={revenueForm.notes}
              onChange={(e) => setRevenueForm({ ...revenueForm, notes: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="Additional notes about revenue recognition"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowCreateRevenue(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Recognizing...' : 'Recognize Revenue'}
            </button>
          </div>
        </form>
      </AnimatedModal>

      {/* Generate Report Modal */}
      <AnimatedModal
        open={showGenerateReport}
        onClose={() => setShowGenerateReport(false)}
        title="Generate Financial Report"
        animationType="scale"
        size="lg"
      >
        <form onSubmit={handleGenerateReport} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Report Type *
              </label>
              <select
                value={reportForm.report_type}
                onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              >
                <option value="profit_loss">Profit & Loss Statement</option>
                <option value="cash_flow">Cash Flow Statement</option>
                <option value="balance_sheet">Balance Sheet</option>
                <option value="revenue_analysis">Revenue Analysis</option>
                <option value="payment_summary">Payment Summary</option>
                <option value="invoice_summary">Invoice Summary</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Report Name *
              </label>
              <input
                type="text"
                value={reportForm.report_name}
                onChange={(e) => setReportForm({ ...reportForm, report_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="e.g., Q1 2024 P&L Report"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Start Date *
              </label>
              <input
                type="date"
                value={reportForm.start_date}
                onChange={(e) => setReportForm({ ...reportForm, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                End Date *
              </label>
              <input
                type="date"
                value={reportForm.end_date}
                onChange={(e) => setReportForm({ ...reportForm, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="include_charts"
              checked={reportForm.include_charts}
              onChange={(e) => setReportForm({ ...reportForm, include_charts: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="include_charts" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Include charts and visualizations
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowGenerateReport(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </form>
      </AnimatedModal>

      {/* Success Modal */}
      <AnimatedModal
        open={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title="Success"
        animationType="scale"
        size="sm"
      >
        <div className="text-center space-y-4">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 dark:bg-green-900">
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-lg text-gray-900 dark:text-white">
            {successMessage}
          </p>
          <button
            onClick={() => setShowSuccessModal(false)}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
          >
            OK
          </button>
        </div>
      </AnimatedModal>
    </div>
  );
};

export default FinancialManagement;
