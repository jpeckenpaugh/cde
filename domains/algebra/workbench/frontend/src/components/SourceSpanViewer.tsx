import React from 'react';
import { SourceSpan } from '../types';
import { FileText, MapPin, Layers, Hash, BookOpen } from 'lucide-react';

interface SourceSpanViewerProps {
  span?: SourceSpan;
  title?: string;
  onOpenPdfPage?: (page: number) => void;
}

export const SourceSpanViewer: React.FC<SourceSpanViewerProps> = ({ span, title = 'Source Span Evidence', onOpenPdfPage }) => {
  if (!span) {
    return (
      <div className="bg-gray-800/60 border border-gray-700/60 rounded-lg p-3 text-xs text-gray-400 italic">
        No source span attached.
      </div>
    );
  }

  let bbox: any = null;
  if (span.bbox_json) {
    try {
      bbox = JSON.parse(span.bbox_json);
    } catch (e) {
      bbox = null;
    }
  }

  let metadata: any = null;
  if (span.extraction_metadata_json) {
    try {
      metadata = JSON.parse(span.extraction_metadata_json);
    } catch (e) {
      metadata = null;
    }
  }

  return (
    <div className="bg-gray-800/80 border border-gray-700 rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between border-b border-gray-700/80 pb-1.5">
        <span className="text-xs font-semibold text-gray-300 flex items-center space-x-1.5">
          <FileText className="w-3.5 h-3.5 text-blue-400" />
          <span>{title}</span>
        </span>
        <span className="text-xs bg-gray-900 border border-gray-700 text-gray-300 px-2 py-0.5 rounded font-mono flex items-center space-x-1">
          <Hash className="w-3 h-3 text-gray-400" />
          <span>Span ID: {span.id}</span>
        </span>
      </div>

      <div className="bg-gray-950 p-2.5 rounded border border-gray-800 font-mono text-xs text-emerald-300 whitespace-pre-wrap">
        "{span.text_content}"
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
        <div className="flex items-center justify-between bg-gray-900/80 border border-gray-700/60 px-2 py-1 rounded">
          <span className="flex items-center space-x-1.5">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span>Page: {span.page_number ?? 'N/A'}</span>
          </span>
          {span.page_number != null && onOpenPdfPage && (
            <button
              onClick={() => onOpenPdfPage(span.page_number!)}
              className="text-[11px] bg-blue-900/60 hover:bg-blue-800 text-blue-300 border border-blue-700/80 px-1.5 py-0.5 rounded flex items-center space-x-1 transition"
              title={`View Page ${span.page_number} in PDF`}
            >

              <BookOpen className="w-3 h-3" />
              <span>Citation Pointer</span>
            </button>
          )}
        </div>
        <div className="flex items-center space-x-1.5 bg-gray-900/60 px-2 py-1 rounded">
          <Layers className="w-3.5 h-3.5 text-purple-400" />
          <span>Reading Order: {span.reading_order}</span>
        </div>
      </div>


      {bbox && (
        <div className="text-[11px] text-gray-400 bg-gray-900/40 p-1.5 rounded font-mono">
          <span className="text-gray-500 font-sans font-semibold">BBox (x0, y0, x1, y1): </span>
          ({bbox.x0}, {bbox.y0}, {bbox.x1}, {bbox.y1})
        </div>
      )}

      {metadata && (
        <div className="text-[11px] text-gray-400 bg-gray-900/40 p-1.5 rounded font-mono">
          <span className="text-gray-500 font-sans font-semibold">Parser Metadata: </span>
          {JSON.stringify(metadata)}
        </div>
      )}
    </div>
  );
};
