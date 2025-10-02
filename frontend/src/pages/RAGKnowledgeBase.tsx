import React, { useState, useEffect } from 'react';
import { Search, Upload, MessageSquare, BookOpen, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface SearchResult {
  chunk_id: string;
  score: number;
  text: string;
  metadata: any;
}

interface QAResponse {
  answer: string;
  citations: any[];
  sources_used: number;
  confidence_score: number;
  question: string;
}

const RAGKnowledgeBase: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'search' | 'qa' | 'upload'>('search');
  const [query, setQuery] = useState('');
  const [question, setQuestion] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [qaResponse, setQaResponse] = useState<QAResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('general');
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/rag/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Search failed:', error);
      showToast('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQA = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/rag/qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setQaResponse(data);
    } catch (error) {
      console.error('Q&A failed:', error);
      showToast('Q&A failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!uploadFile || !uploadTitle.trim()) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('title', uploadTitle);
      formData.append('category', uploadCategory);

      const response = await fetch('/api/rag/ingest/document', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.message) {
        showToast('Document uploaded successfully!');
        setUploadFile(null);
        setUploadTitle('');
        setUploadCategory('general');
      } else {
        showToast('Upload failed. Please try again.');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      showToast('Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1) + '%';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">RAG Knowledge Base</h1>
              <p className="text-gray-600">Intelligent customer support with AI-powered Q&A</p>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex gap-4 border-b">
            {[
              { id: 'search', label: 'Search Knowledge', icon: Search },
              { id: 'qa', label: 'Ask Questions', icon: MessageSquare },
              { id: 'upload', label: 'Upload Documents', icon: Upload }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex gap-4 mb-6">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search the knowledge base..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <button
                onClick={handleSearch}
                disabled={loading || !query.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Search className="h-4 w-4" />
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Search Results</h3>
                {searchResults.map((result, index) => (
                  <div key={result.chunk_id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900">
                          {result.metadata.document_title || 'Unknown Document'}
                        </span>
                        <span className="text-xs text-gray-500">
                          {result.metadata.category}
                        </span>
                      </div>
                      <span className="text-sm text-green-600 font-medium">
                        {formatScore(result.score)} relevant
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm leading-relaxed">{result.text}</p>
                  </div>
                ))}
              </div>
            )}

            {searchResults.length === 0 && query && !loading && (
              <div className="text-center py-8">
                <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No results found. Try different keywords.</p>
              </div>
            )}
          </div>
        )}

        {/* Q&A Tab */}
        {activeTab === 'qa' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex gap-4 mb-6">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about NeuraCRM..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && handleQA()}
              />
              <button
                onClick={handleQA}
                disabled={loading || !question.trim()}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <MessageSquare className="h-4 w-4" />
                {loading ? 'Thinking...' : 'Ask'}
              </button>
            </div>

            {/* Q&A Response */}
            {qaResponse && (
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-medium text-gray-900">AI Answer</span>
                  <span className="text-sm text-gray-500">
                    Confidence: {(qaResponse.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>

                <div className="prose prose-sm max-w-none mb-4">
                  <p className="text-gray-700 leading-relaxed">{qaResponse.answer}</p>
                </div>

                {qaResponse.citations.length > 0 && (
                  <div className="border-t pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Sources:</h4>
                    <div className="space-y-1">
                      {qaResponse.citations.map((citation, index) => (
                        <div key={index} className="text-xs text-gray-600">
                          • {citation.document_title} ({citation.relevance_score?.toFixed(3)})
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!qaResponse && question && !loading && (
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Ask a question to get AI-powered answers from the knowledge base.</p>
              </div>
            )}
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Knowledge Base Documents</h3>
              <p className="text-gray-600 text-sm">
                Upload PDF, DOCX, or TXT files to expand the knowledge base. Supported formats help customers get accurate answers.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Title</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="Enter document title..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="general">General</option>
                  <option value="documentation">Documentation</option>
                  <option value="support">Support</option>
                  <option value="features">Features</option>
                  <option value="troubleshooting">Troubleshooting</option>
                  <option value="billing">Billing</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">File</label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Supported formats: PDF, DOCX, TXT (max 10MB)</p>
              </div>

              <button
                onClick={handleFileUpload}
                disabled={loading || !uploadFile || !uploadTitle.trim()}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Upload className="h-4 w-4" />
                {loading ? 'Uploading...' : 'Upload Document'}
              </button>
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
    </div>
  );
};

export default RAGKnowledgeBase;