import { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Upload,
  Search,
  Download,
  Trash2,
  Brain,
  Eye,
  File,
  AlertCircle,
  CheckCircle,
  Clock,
  X
} from 'lucide-react';

// Type definitions
interface DocumentMetadata {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  organization_id: number;
  user_id: number;
  content_hash: string;
  extracted_text: string;
  summary?: string;
  key_entities: any[];
  sentiment_score?: number;
  language: string;
  page_count: number;
  processing_status: string;
}

interface DocumentAnalysis {
  summary: string;
  key_points: string[];
  entities: any[];
  sentiment: any;
  categories: string[];
  confidence_scores: any;
}

interface DocumentStats {
  total_documents: number;
  total_size_mb: number;
  by_type: Record<string, number>;
  processing_status: Record<string, number>;
  recent_uploads: number;
}

export default function DocumentProcessing() {
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<DocumentMetadata | null>(null);
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [stats, setStats] = useState<DocumentStats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/documents', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      } else {
        console.error('Error loading documents:', response.status, response.statusText);
        // Set empty documents array if API fails
        setDocuments([]);
      }
    } catch (err) {
      console.error('Error loading documents:', err);
      // Set empty documents array if fetch fails
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/documents/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        console.error('Error loading stats:', response.status, response.statusText);
        // Set default stats if API fails
        setStats({
          total_documents: 0,
          total_size_mb: 0,
          by_type: {},
          processing_status: { completed: 0, processing: 0, failed: 0 },
          recent_uploads: 0
        });
      }
    } catch (err) {
      console.error('Error loading stats:', err);
      // Set default stats if fetch fails
      setStats({
        total_documents: 0,
        total_size_mb: 0,
        by_type: {},
        processing_status: { completed: 0, processing: 0, failed: 0 },
        recent_uploads: 0
      });
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const newDoc = await response.json();
        setDocuments(prev => [newDoc, ...prev]);
        loadStats();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
      }
    } catch (err) {
      setError('Upload failed');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAnalyze = async (docId: string) => {
    setAnalyzing(docId);
    setError(null);

    try {
      const response = await fetch(`/api/documents/${docId}/analyze`, {
        method: 'POST',
      });

      if (response.ok) {
        const analysisData = await response.json();
        setAnalysis(analysisData);
        setSelectedDocument(documents.find(d => d.id === docId) || null);
        // Refresh documents to get updated metadata
        loadDocuments();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Analysis failed');
      }
    } catch (err) {
      setError('Analysis failed');
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(null);
    }
  };

  const handleDownload = async (docId: string, filename: string) => {
    try {
      const response = await fetch(`/api/documents/${docId}/download`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Download error:', err);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      const response = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setDocuments(prev => prev.filter(d => d.id !== docId));
        loadStats();
        if (selectedDocument?.id === docId) {
          setSelectedDocument(null);
          setAnalysis(null);
        }
      }
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadDocuments();
      return;
    }

    try {
      const response = await fetch(`/api/documents/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.ok) {
        const results = await response.json();
        setDocuments(results);
      }
    } catch (err) {
      console.error('Search error:', err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'processing':
      case 'running':
        return <Clock className="w-4 h-4 text-blue-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Document Processing</h1>
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
            AI-Powered Analysis
          </span>
        </div>
        <p className="text-gray-600">
          Upload, analyze, and search through documents using AI-powered processing and insights
        </p>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm">
            <strong>Demo Mode:</strong> Upload documents for AI analysis including summarization, entity extraction, and sentiment analysis.
          </p>
        </div>
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">
              <strong>Error:</strong> {error}
            </p>
          </div>
        )}
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_documents}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Size</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_size_mb.toFixed(1)} MB</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Upload className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Processed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.processing_status.completed || 0}
                </p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recent Uploads</p>
                <p className="text-2xl font-bold text-gray-900">{stats.recent_uploads}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload and Search Section */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4">
          {/* File Upload */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Document
            </label>
            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Upload className="w-4 h-4" />
                )}
                {uploading ? 'Uploading...' : 'Choose File'}
              </button>
              <span className="text-sm text-gray-500 self-center">
                PDF, DOCX, DOC, TXT (max 10MB)
              </span>
            </div>
          </div>

          {/* Search */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Documents
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search by content or filename..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Documents List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold">Documents</h2>
            </div>
            <div className="divide-y">
              {documents.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No documents uploaded yet</p>
                  <p className="text-sm">Upload a document to get started</p>
                </div>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <File className="w-4 h-4 text-gray-400" />
                          <h3 className="font-medium text-gray-900">{doc.filename}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(doc.processing_status)}`}>
                            {doc.processing_status}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>{formatFileSize(doc.file_size)} • {doc.file_type.toUpperCase()} • {doc.page_count} pages</p>
                          <p>Uploaded {new Date(doc.upload_date).toLocaleDateString()}</p>
                          {doc.summary && (
                            <p className="text-gray-700 italic">"{doc.summary.substring(0, 100)}..."</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => handleAnalyze(doc.id)}
                          disabled={analyzing === doc.id}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg disabled:opacity-50"
                          title="Analyze with AI"
                        >
                          {analyzing === doc.id ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          ) : (
                            <Brain className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => handleDownload(doc.id, doc.filename)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Analysis Panel */}
        <div className="lg:col-span-1">
          {selectedDocument && analysis ? (
            <div className="bg-white rounded-xl shadow-sm border">
              <div className="p-6 border-b">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">AI Analysis</h2>
                  <button
                    onClick={() => {
                      setSelectedDocument(null);
                      setAnalysis(null);
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-sm text-gray-600">{selectedDocument.filename}</p>
              </div>
              <div className="p-6 space-y-6">
                {/* Summary */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Summary</h3>
                  <p className="text-sm text-gray-700">{analysis.summary}</p>
                </div>

                {/* Key Points */}
                {analysis.key_points.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Key Points</h3>
                    <ul className="space-y-1">
                      {analysis.key_points.map((point, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-blue-500 mt-1">•</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Sentiment */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">Sentiment</h3>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      analysis.sentiment.label === 'positive' ? 'bg-green-100 text-green-800' :
                      analysis.sentiment.label === 'negative' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {analysis.sentiment.label}
                    </span>
                    <span className="text-sm text-gray-600">
                      Score: {analysis.sentiment.score?.toFixed(2)}
                    </span>
                  </div>
                </div>

                {/* Categories */}
                {analysis.categories.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Categories</h3>
                    <div className="flex flex-wrap gap-1">
                      {analysis.categories.map((category, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {category}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Entities */}
                {analysis.entities.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Entities Found</h3>
                    <div className="space-y-1">
                      {analysis.entities.slice(0, 5).map((entity, index) => (
                        <div key={index} className="text-sm text-gray-700">
                          <span className="font-medium">{entity.name || entity}</span>
                          {entity.type && <span className="text-gray-500"> ({entity.type})</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis</h3>
              <p className="text-sm text-gray-600">
                Select a document and click the brain icon to analyze it with AI
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}