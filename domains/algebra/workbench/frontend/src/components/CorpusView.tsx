import React, { useState } from 'react';
import { ChapterHierarchy, SectionSummary, AssessmentItem } from '../types';
import { StatusBadge } from './StatusBadge';
import { Folder, ChevronRight, BookOpen, Layers, CheckCircle2, Clock, AlertTriangle, FileText } from 'lucide-react';

interface CorpusViewProps {
  chapters: ChapterHierarchy[];
  selectedSectionId?: string;
  onSelectSection: (sectionId: string) => void;
  sectionItems: AssessmentItem[];
  onSelectItem: (item: AssessmentItem) => void;
  isLoading: boolean;
}

export const CorpusView: React.FC<CorpusViewProps> = ({
  chapters,
  selectedSectionId,
  onSelectSection,
  sectionItems,
  onSelectItem,
  isLoading
}) => {
  const [openChapters, setOpenChapters] = useState<Record<string, boolean>>({
    'chap-1': true,
    'chap-2': true,
  });

  const toggleChapter = (chapterId: string) => {
    setOpenChapters((prev) => ({ ...prev, [chapterId]: !prev[chapterId] }));
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-80px)] p-6">
      {/* Chapter & Section Tree Sidebar */}
      <div className="col-span-4 bg-gray-800 border border-gray-700 rounded-xl p-4 flex flex-col overflow-hidden shadow-lg">
        <div className="flex items-center space-x-2 border-b border-gray-700 pb-3 mb-3">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-gray-200">Textbook Hierarchy</h2>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {chapters.map((ch) => {
            const isOpen = openChapters[ch.id] ?? true;
            return (
              <div key={ch.id} className="bg-gray-900/60 border border-gray-700/80 rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleChapter(ch.id)}
                  className="w-full flex items-center justify-between px-3 py-2.5 bg-gray-800/90 hover:bg-gray-750 transition-colors text-left"
                >
                  <div className="flex items-center space-x-2 font-semibold text-xs text-gray-100">
                    <ChevronRight className={`w-4 h-4 text-blue-400 transition-transform ${isOpen ? 'rotate-90' : ''}`} />
                    <span>Chapter {ch.chapter_number}: {ch.title}</span>
                  </div>
                </button>

                {isOpen && (
                  <div className="p-2 space-y-1">
                    {ch.sections.map((sec) => {
                      const isSelected = sec.id === selectedSectionId;
                      return (
                        <button
                          key={sec.id}
                          onClick={() => onSelectSection(sec.id)}
                          className={`w-full text-left p-2.5 rounded-md text-xs transition-all border ${
                            isSelected
                              ? 'bg-blue-950/80 border-blue-600 text-white shadow'
                              : 'bg-gray-800/40 border-gray-700/50 text-gray-300 hover:bg-gray-800 hover:text-white'
                          }`}
                        >
                          <div className="font-semibold mb-1 flex items-center justify-between">
                            <span>Sec {sec.section_number}: {sec.title}</span>
                          </div>

                          <div className="flex items-center space-x-2 text-[10px] text-gray-400 mt-1">
                            {sec.verified_count > 0 && (
                              <span className="flex items-center space-x-0.5 text-emerald-400">
                                <CheckCircle2 className="w-3 h-3" />
                                <span>{sec.verified_count}</span>
                              </span>
                            )}
                            {sec.candidate_count > 0 && (
                              <span className="flex items-center space-x-0.5 text-amber-400">
                                <Clock className="w-3 h-3" />
                                <span>{sec.candidate_count}</span>
                              </span>
                            )}
                            {sec.needs_resolution_count > 0 && (
                              <span className="flex items-center space-x-0.5 text-purple-400">
                                <AlertTriangle className="w-3 h-3" />
                                <span>{sec.needs_resolution_count}</span>
                              </span>
                            )}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Section Content & Assessment Items Panel */}
      <div className="col-span-8 bg-gray-800 border border-gray-700 rounded-xl p-4 flex flex-col overflow-hidden shadow-lg">
        <div className="flex items-center justify-between border-b border-gray-700 pb-3 mb-4">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-blue-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-200">
              Assessment Items & Extracted Spans
            </h2>
          </div>
          <span className="text-xs text-gray-400">
            {sectionItems.length} item{sectionItems.length !== 1 ? 's' : ''} in section
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {isLoading ? (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              Loading section items...
            </div>
          ) : sectionItems.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              Select a section from the hierarchy tree to inspect assessment items.
            </div>
          ) : (
            sectionItems.map((item) => (
              <div
                key={item.id}
                onClick={() => onSelectItem(item)}
                className="bg-gray-900/80 border border-gray-700 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:shadow-md transition-all space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-sm text-blue-300 bg-blue-950 px-2 py-0.5 rounded border border-blue-800">
                      {item.item_label}
                    </span>
                    <span className="text-xs font-semibold uppercase text-gray-400 bg-gray-800 px-2 py-0.5 rounded">
                      {item.item_type}
                    </span>
                  </div>

                  {item.links.length > 0 && (
                    <StatusBadge status={item.links[0].current_status} />
                  )}
                </div>

                <div className="text-sm text-gray-100 font-medium">
                  {item.content_text}
                </div>

                {/* Multipart sub-questions */}
                {item.parts && item.parts.length > 0 && (
                  <div className="pl-4 border-l-2 border-blue-600/60 space-y-2 my-2">
                    <div className="text-xs font-semibold text-gray-400">Exercise Parts:</div>
                    {item.parts.map((p) => (
                      <div key={p.id} className="flex items-center justify-between text-xs bg-gray-800/80 p-2 rounded">
                        <span className="text-gray-200">
                          <strong className="text-blue-400">({p.part_label})</strong> {p.content_text}
                        </span>
                        {p.links.length > 0 && (
                          <StatusBadge status={p.links[0].current_status} />
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-800">
                  <span className="flex items-center space-x-1">
                    <FileText className="w-3.5 h-3.5 text-gray-500" />
                    <span>Source Span ID: {item.source_span_id || 'N/A'}</span>
                  </span>
                  <span className="text-blue-400 font-semibold text-xs hover:underline">
                    Inspect Provenance & Review &rarr;
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
