import React, { useState } from 'react';
import { ItemAnswerLink, ReviewSubmission } from '../types';
import { StatusBadge } from './StatusBadge';
import { SourceSpanViewer } from './SourceSpanViewer';
import { ListChecks, CheckCircle2, XCircle, AlertTriangle, User, MessageSquare, Filter } from 'lucide-react';

interface ReviewQueueViewProps {
  queue: ItemAnswerLink[];
  selectedStatus: string;
  onStatusFilterChange: (status: string) => void;
  onReviewSubmit: (linkId: string, submission: ReviewSubmission) => Promise<void>;
  isLoading: boolean;
}

export const ReviewQueueView: React.FC<ReviewQueueViewProps> = ({
  queue,
  selectedStatus,
  onStatusFilterChange,
  onReviewSubmit,
  isLoading
}) => {
  const [actorName, setActorName] = useState('reviewer1');
  const [rationales, setRationales] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<Record<string, boolean>>({});

  const handleRationaleChange = (linkId: string, val: string) => {
    setRationales((prev) => ({ ...prev, [linkId]: val }));
  };

  const handleAction = async (linkId: string, action: 'accept' | 'reject' | 'correct' | 'mark_needs_resolution') => {
    if (!actorName.trim()) {
      alert('Please specify a reviewer actor name.');
      return;
    }
    setIsSubmitting((prev) => ({ ...prev, [linkId]: true }));
    try {
      await onReviewSubmit(linkId, {
        action,
        actor: actorName,
        rationale: rationales[linkId]?.trim() || undefined
      });
      setRationales((prev) => ({ ...prev, [linkId]: '' }));
    } catch (e) {
      alert(`Review error: ${e}`);
    } finally {
      setIsSubmitting((prev) => ({ ...prev, [linkId]: false }));
    }
  };

  return (
    <div className="h-[calc(100vh-80px)] p-6 flex flex-col space-y-4">
      {/* Header & Filter Controls */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3">
          <div className="bg-amber-600/20 text-amber-400 p-2 rounded-lg border border-amber-600/30">
            <ListChecks className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">EKC Sample Review Queue</h2>
            <p className="text-xs text-gray-400">Inspect parser candidate predictions and certify question-answer links</p>
          </div>
        </div>

        {/* Status Filter Buttons */}
        <div className="flex items-center space-x-2 bg-gray-900 p-1.5 rounded-lg border border-gray-700">
          <Filter className="w-4 h-4 text-gray-400 ml-1.5 mr-0.5" />
          <button
            onClick={() => onStatusFilterChange('')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              selectedStatus === '' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Pending Queue
          </button>
          <button
            onClick={() => onStatusFilterChange('candidate')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              selectedStatus === 'candidate' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Candidates
          </button>
          <button
            onClick={() => onStatusFilterChange('needs_resolution')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              selectedStatus === 'needs_resolution' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Unresolved
          </button>
          <button
            onClick={() => onStatusFilterChange('rejected')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              selectedStatus === 'rejected' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Rejected
          </button>
          <button
            onClick={() => onStatusFilterChange('verified')}
            className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
              selectedStatus === 'verified' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            }`}
          >
            Verified
          </button>
        </div>
      </div>

      {/* Queue Items List */}
      <div className="flex-1 bg-gray-800 border border-gray-700 rounded-xl p-4 overflow-y-auto space-y-4 shadow-lg">
        {isLoading ? (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
            Loading review queue...
          </div>
        ) : queue.length === 0 ? (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
            No items in queue matching the selected filter.
          </div>
        ) : (
          queue.map((link) => (
            <div key={link.id} className="bg-gray-900 border border-gray-700 rounded-lg p-5 space-y-4 shadow">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center space-x-3">
                  <span className="bg-gray-800 text-blue-300 font-mono text-xs px-2.5 py-1 rounded border border-gray-700 font-semibold">
                    Link ID: {link.id}
                  </span>
                  <span className="text-xs text-gray-400">Method: {link.method}</span>
                  <span className="text-xs text-gray-400">Confidence: {(link.confidence * 100).toFixed(0)}%</span>
                </div>
                <StatusBadge status={link.current_status} />
              </div>

              {/* Item Prompt and Answer Grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Item / Part Prompt */}
                <div className="bg-gray-950 p-3.5 rounded-lg border border-gray-800 space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-400 block">
                    Question Prompt {link.part ? `(Part ${link.part.part_label})` : ''}
                  </span>
                  <p className="text-sm text-gray-100 font-medium">
                    {link.part ? link.part.content_text : (link.item ? link.item.content_text : 'N/A')}
                  </p>
                  {(link.part?.source_span || link.item?.source_span) && (
                    <SourceSpanViewer span={link.part?.source_span || link.item?.source_span} title="Prompt Evidence" />
                  )}
                </div>

                {/* Proposed Answer */}
                <div className="bg-gray-950 p-3.5 rounded-lg border border-gray-800 space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 block">
                    Candidate Answer Entry
                  </span>
                  <p className="text-sm font-mono text-emerald-300">
                    {link.answer ? link.answer.content_text : 'N/A'}
                  </p>
                  {link.answer?.source_span && (
                    <SourceSpanViewer span={link.answer.source_span} title="Answer Evidence" />
                  )}
                </div>
              </div>

              {/* Action Bar */}
              <div className="bg-gray-800 p-3 rounded-lg border border-gray-700/80 flex items-center space-x-3">
                <div className="w-1/4">
                  <input
                    type="text"
                    placeholder="Reviewer Actor Name"
                    value={actorName}
                    onChange={(e) => setActorName(e.target.value)}
                    className="w-full bg-gray-950 border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Rationale / review note..."
                    value={rationales[link.id] || ''}
                    onChange={(e) => handleRationaleChange(link.id, e.target.value)}
                    className="w-full bg-gray-950 border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    disabled={isSubmitting[link.id]}
                    onClick={() => handleAction(link.id, 'accept')}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-1.5 px-3 rounded flex items-center space-x-1 transition-colors disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Accept</span>
                  </button>
                  <button
                    disabled={isSubmitting[link.id]}
                    onClick={() => handleAction(link.id, 'reject')}
                    className="bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs py-1.5 px-3 rounded flex items-center space-x-1 transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                  <button
                    disabled={isSubmitting[link.id]}
                    onClick={() => handleAction(link.id, 'mark_needs_resolution')}
                    className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs py-1.5 px-3 rounded flex items-center space-x-1 transition-colors disabled:opacity-50"
                  >
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Flag Ambiguous</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
