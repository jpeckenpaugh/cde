import React, { useState, useEffect } from 'react';
import { X, ExternalLink, BookOpen, ChevronLeft, ChevronRight, Hash, FileText } from 'lucide-react';
import { fetchDocumentInfo } from '../api/client';
import { DocumentInfo } from '../types';

interface PdfViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialPage?: number;
  documentId?: string | number;
  documentTitle?: string;
}

export const PdfViewerModal: React.FC<PdfViewerModalProps> = ({
  isOpen,
  onClose,
  initialPage = 1,
  documentId = 'active',
  documentTitle = 'OpenStax Elementary Algebra 2e'
}) => {
  const [docInfo, setDocInfo] = useState<DocumentInfo | null>(null);
  const [page, setPage] = useState<number>(initialPage);
  const [inputPage, setInputPage] = useState<string>(initialPage.toString());

  useEffect(() => {
    if (isOpen) {
      fetchDocumentInfo(String(documentId))
        .then((info) => {
          setDocInfo(info);
          const maxP = info.ingested_pages_count || 1;
          const targetP = Math.min(Math.max(1, initialPage), maxP);
          setPage(targetP);
          setInputPage(targetP.toString());
        })
        .catch(() => {
          setPage(initialPage);
          setInputPage(initialPage.toString());
        });
    }
  }, [isOpen, initialPage, documentId]);

  if (!isOpen) return null;

  const maxPage = docInfo?.ingested_pages_count || 50;
  const singlePagePdfUrl = `/api/documents/${docInfo?.id || documentId}/pages/${page}/pdf`;

  const handlePageSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const p = parseInt(inputPage, 10);
    if (!isNaN(p) && p >= 1 && p <= maxPage) {
      setPage(p);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="bg-gray-950 px-4 py-3 border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-blue-400">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <h3 className="font-semibold text-sm text-gray-200 truncate">
              {docInfo?.title || documentTitle}
            </h3>
            <span className="bg-blue-950 text-blue-300 text-xs px-2 py-0.5 rounded border border-blue-800 font-mono flex items-center space-x-1">
              <FileText className="w-3 h-3 text-amber-400" />
              <span>Parsed Stage 1 Artifacts ({maxPage} Ingested Pages)</span>
            </span>
          </div>

          <div className="flex items-center space-x-3">
            {/* Page Jump Form */}
            <form onSubmit={handlePageSubmit} className="flex items-center space-x-1 bg-gray-900 border border-gray-700 rounded px-2 py-1">
              <span className="text-xs text-gray-400 font-mono flex items-center">
                <Hash className="w-3 h-3 mr-0.5 text-amber-400" /> Page:
              </span>
              <input
                type="number"
                min={1}
                max={maxPage}
                value={inputPage}
                onChange={(e) => setInputPage(e.target.value)}
                className="w-16 bg-gray-950 border border-gray-700 text-gray-100 text-xs rounded px-1.5 py-0.5 font-mono text-center focus:outline-none focus:border-blue-500"
              />
              <span className="text-xs text-gray-500 font-mono">/ {maxPage}</span>
              <button
                type="submit"
                className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-2 py-0.5 rounded transition ml-1"
              >
                Jump
              </button>
            </form>

            <div className="flex items-center space-x-1 border-l border-gray-800 pl-3">
              <button
                onClick={() => {
                  const p = Math.max(1, page - 1);
                  setPage(p);
                  setInputPage(p.toString());
                }}
                disabled={page <= 1}
                className="p-1 text-gray-400 hover:text-white disabled:opacity-30 rounded hover:bg-gray-800"
                title="Previous Page"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  const p = Math.min(maxPage, page + 1);
                  setPage(p);
                  setInputPage(p.toString());
                }}
                disabled={page >= maxPage}
                className="p-1 text-gray-400 hover:text-white disabled:opacity-30 rounded hover:bg-gray-800"
                title="Next Page"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <a
              href={singlePagePdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-xs text-gray-400 hover:text-blue-400 bg-gray-800/80 px-2.5 py-1 rounded border border-gray-700 transition"
              title="Open single-page PDF artifact in new browser tab"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Tab</span>
            </a>

            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white p-1 rounded hover:bg-gray-800 transition"
              title="Close PDF Viewer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body / PDF Frame */}
        <div className="flex-1 bg-gray-950 p-2 relative overflow-hidden">
          <iframe
            key={`pdf-page-${page}`}
            src={singlePagePdfUrl}
            className="w-full h-full rounded border border-gray-800 bg-white"
            title={`Parsed PDF Artifact Page ${page}`}
          />
        </div>
      </div>
    </div>
  );
};
