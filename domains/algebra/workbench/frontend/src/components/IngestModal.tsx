import React, { useState, useEffect } from 'react';
import { X, Play, RefreshCw, CheckCircle, AlertCircle, FileText, Database, Layers } from 'lucide-react';
import { fetchSourcePdfs, triggerIngest, fetchIngestStatus } from '../api/client';
import { SourcePdf, IngestStatus } from '../types';

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onIngestComplete: () => void;
}

export const IngestModal: React.FC<IngestModalProps> = ({
  isOpen,
  onClose,
  onIngestComplete,
}) => {
  const [sources, setSources] = useState<SourcePdf[]>([]);
  const [selectedPdf, setSelectedPdf] = useState<string>('elementary-algebra-2e_-_WEB.pdf');
  const [pageRangeMode, setPageRangeMode] = useState<'all' | 'custom'>('custom');
  const [customRange, setCustomRange] = useState<string>('1-50');
  const [resetDb, setResetDb] = useState<boolean>(true);
  
  const [status, setStatus] = useState<IngestStatus | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchSourcePdfs()
        .then((data) => {
          setSources(data);
          if (data.length > 0 && !data.some((s) => s.filename === selectedPdf)) {
            setSelectedPdf(data[0].filename);
          }
        })
        .catch(console.error);

      // Check current ingestion status on open
      fetchIngestStatus()
        .then(setStatus)
        .catch(console.error);
    }
  }, [isOpen]);

  // Polling loop when status is 'running'
  useEffect(() => {
    if (!isOpen || !status || status.status !== 'running') return;

    const interval = setInterval(() => {
      fetchIngestStatus()
        .then((newStatus) => {
          setStatus(newStatus);
          if (newStatus.status === 'completed') {
            onIngestComplete();
          }
        })
        .catch(console.error);
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, status?.status]);

  if (!isOpen) return null;

  const handleStartIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMessage(null);

    const pagesRange = pageRangeMode === 'all' ? undefined : customRange.trim() || undefined;

    try {
      await triggerIngest({
        pdf_filename: selectedPdf,
        pages_range: pagesRange,
        reset_db: resetDb,
      });

      const initialStatus = await fetchIngestStatus();
      setStatus(initialStatus);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to start ingestion');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isRunning = status?.status === 'running';
  const isCompleted = status?.status === 'completed';
  const isFailed = status?.status === 'failed';

  const pagesProcessed = status?.pages_processed || 0;
  const totalPages = status?.total_pages || 1;
  const progressPercent = totalPages > 0 ? Math.min(100, Math.round((pagesProcessed / totalPages) * 100)) : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 bg-gray-800/90 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600/20 p-2 rounded-lg text-blue-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Stage 1 PDF Ingestion Control</h2>
              <p className="text-xs text-gray-400">Process raw textbook evidence into single-page artifacts</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-700 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {errorMessage && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg flex items-center space-x-3 text-sm">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Form setup (when not actively running) */}
          {!isRunning && (
            <form onSubmit={handleStartIngest} className="space-y-5">
              {/* Document Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2 flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-blue-400" />
                  <span>Select Source PDF Document</span>
                </label>
                <select
                  value={selectedPdf}
                  onChange={(e) => setSelectedPdf(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                >
                  {sources.length > 0 ? (
                    sources.map((s) => (
                      <option key={s.filename} value={s.filename}>
                        {s.filename} ({(s.size_bytes / (1024 * 1024)).toFixed(1)} MB)
                      </option>
                    ))
                  ) : (
                    <option value="elementary-algebra-2e_-_WEB.pdf">
                      elementary-algebra-2e_-_WEB.pdf (Default)
                    </option>
                  )}
                </select>
              </div>

              {/* Page Range Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2 flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span>Page Ingestion Range</span>
                </label>
                <div className="grid grid-cols-2 gap-3 mb-2">
                  <button
                    type="button"
                    onClick={() => setPageRangeMode('custom')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium border transition ${
                      pageRangeMode === 'custom'
                        ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                        : 'bg-gray-900 border-gray-700 text-gray-400 hover:text-white'
                    }`}
                  >
                    Custom Page Range
                  </button>
                  <button
                    type="button"
                    onClick={() => setPageRangeMode('all')}
                    className={`px-3 py-2 rounded-lg text-sm font-medium border transition ${
                      pageRangeMode === 'all'
                        ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                        : 'bg-gray-900 border-gray-700 text-gray-400 hover:text-white'
                    }`}
                  >
                    All Pages (1,290 Pages)
                  </button>
                </div>

                {pageRangeMode === 'custom' && (
                  <input
                    type="text"
                    value={customRange}
                    onChange={(e) => setCustomRange(e.target.value)}
                    placeholder="e.g. 1-50 or 1,2,5"
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 placeholder-gray-500"
                  />
                )}
              </div>

              {/* Reset Database Checkbox */}
              <div className="bg-gray-900/60 border border-gray-700 p-4 rounded-lg flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="resetDb"
                  checked={resetDb}
                  onChange={(e) => setResetDb(e.target.checked)}
                  className="mt-1 rounded bg-gray-800 border-gray-600 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="resetDb" className="text-sm cursor-pointer select-none">
                  <span className="font-semibold text-white block mb-0.5">
                    Reset Database (Clear Mock Seed Data)
                  </span>
                  <span className="text-xs text-gray-400 block">
                    Flushes existing mock records so real parsed textbook entities, chapters, and sections are indexed cleanly into SQLite.
                  </span>
                </label>
              </div>

              {/* Action Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-2.5 px-4 rounded-lg transition flex items-center justify-center space-x-2 shadow-lg"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Launching Ingestion Task...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 fill-current" />
                    <span>Start Stage 1 Ingestion</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Live Progress Bar & Dashboard Card */}
          {status && (
            <div className="bg-gray-900 border border-gray-700 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {isRunning && <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />}
                  {isCompleted && <CheckCircle className="w-4 h-4 text-emerald-400" />}
                  {isFailed && <AlertCircle className="w-4 h-4 text-red-400" />}
                  <span className="text-sm font-semibold text-white capitalize">
                    Status: {status.status}
                  </span>
                </div>
                {status.run_id && (
                  <span className="text-xs text-gray-500 font-mono">
                    ID: {status.run_id.slice(0, 8)}...
                  </span>
                )}
              </div>

              {/* Animated Progress Bar */}
              <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1">
                  <span>Pages Processed: {pagesProcessed} / {totalPages}</span>
                  <span>{progressPercent}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden border border-gray-700">
                  <div
                    className={`h-full transition-all duration-500 ${
                      isCompleted ? 'bg-emerald-500' : isFailed ? 'bg-red-500' : 'bg-blue-500 animate-pulse'
                    }`}
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
              </div>

              {/* Status Stats Grid */}
              <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
                <div className="bg-gray-800/80 p-3 rounded-lg border border-gray-700/50">
                  <span className="text-gray-400 block mb-1">Current Page Number</span>
                  <span className="text-sm font-bold text-white">
                    {status.current_page_number > 0 ? `Page ${status.current_page_number}` : '-'}
                  </span>
                </div>

                <div className="bg-gray-800/80 p-3 rounded-lg border border-gray-700/50">
                  <span className="text-gray-400 block mb-1">Ingestion Run State</span>
                  <span className={`text-sm font-bold capitalize ${
                    isCompleted ? 'text-emerald-400' : isFailed ? 'text-red-400' : 'text-blue-400'
                  }`}>
                    {status.status}
                  </span>
                </div>
              </div>

              {status.error_message && (
                <div className="text-xs bg-red-950/50 text-red-400 p-3 rounded-lg border border-red-900 font-mono">
                  Error: {status.error_message}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-gray-800/90 border-t border-gray-700 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 text-sm font-medium rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
