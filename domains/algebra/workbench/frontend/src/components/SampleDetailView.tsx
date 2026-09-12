import React, { useState } from 'react';
import { AssessmentItem, ItemAnswerLink, ReviewSubmission } from '../types';
import { StatusBadge } from './StatusBadge';
import { SourceSpanViewer } from './SourceSpanViewer';
import { X, CheckCircle2, XCircle, AlertTriangle, RefreshCw, Clock, User, MessageSquare } from 'lucide-react';

interface SampleDetailViewProps {
  item: AssessmentItem;
  onClose: () => void;
  onReviewSubmit: (linkId: string, submission: ReviewSubmission) => Promise<void>;
  onOpenPdfPage?: (page: number) => void;
}

export const SampleDetailView: React.FC<SampleDetailViewProps> = ({
  item,
  onClose,
  onReviewSubmit,
  onOpenPdfPage
}) => {
  const [actorName, setActorName] = useState('reviewer1');
  const [rationale, setRationale] = useState('');
  const [replacementAnswer, setReplacementAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState<'details' | 'audit'>('details');

  // Collect all links associated with this item or its parts
  const itemLinks: { link: ItemAnswerLink; partLabel?: string }[] = [];
  item.links.forEach((l) => itemLinks.push({ link: l }));
  item.parts.forEach((p) => {
    p.links.forEach((l) => itemLinks.push({ link: l, partLabel: p.part_label }));
  });

  const handleAction = async (linkId: string, action: 'accept' | 'reject' | 'correct' | 'mark_needs_resolution') => {
    if (!actorName.trim()) {
      alert('Please enter your reviewer actor name.');
      return;
    }
    setIsSubmitting(true);
    try {
      await onReviewSubmit(linkId, {
        action,
        actor: actorName,
        rationale: rationale.trim() || undefined,
        replacement_answer_id: action === 'correct' ? replacementAnswer.trim() || undefined : undefined
      });
      setRationale('');
      setReplacementAnswer('');
    } catch (e) {
      alert(`Error submitting review decision: ${e}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-6 backdrop-blur-sm">
      <div className="bg-gray-800 border border-gray-700 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-700 px-6 py-4 bg-gray-850">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-lg font-bold text-white">{item.item_label}</h2>
              <span className="text-xs uppercase bg-blue-950 text-blue-300 border border-blue-800 px-2 py-0.5 rounded font-semibold">
                {item.item_type}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">Assessment Item Sample Detail & Certification Surface</p>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Item Prompt Section */}
          <div className="bg-gray-900 border border-gray-700/80 rounded-lg p-4 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Item Prompt</h3>
            <div className="text-base text-white font-medium bg-gray-950 p-3 rounded border border-gray-800">
              {item.content_text}
            </div>
            <SourceSpanViewer span={item.source_span} title="Prompt Source Span" onOpenPdfPage={onOpenPdfPage} />
          </div>


          {/* Parts & Links */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400">Candidate Answers & Review Actions</h3>

            {itemLinks.length === 0 ? (
              <div className="text-sm text-gray-400 italic bg-gray-900 p-4 rounded border border-gray-800">
                No answer links currently attached to this item.
              </div>
            ) : (
              itemLinks.map(({ link, partLabel }) => (
                <div key={link.id} className="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                    <div className="flex items-center space-x-2">
                      {partLabel && (
                        <span className="bg-purple-950 text-purple-300 border border-purple-800 px-2 py-0.5 rounded text-xs font-bold">
                          Part ({partLabel})
                        </span>
                      )}
                      <span className="text-xs text-gray-400">Link ID: {link.id}</span>
                      <span className="text-xs text-gray-400">Method: {link.method}</span>
                      <span className="text-xs text-gray-400">Confidence: {(link.confidence * 100).toFixed(0)}%</span>
                    </div>

                    <StatusBadge status={link.current_status} />
                  </div>

                  {/* Proposed / Linked Answer Entry */}
                  <div className="space-y-2">
                    <span className="text-xs font-semibold text-gray-300">Target Answer Entry:</span>
                    <div className="bg-gray-950 p-3 rounded border border-gray-800 text-sm font-mono text-emerald-300">
                      {link.answer?.content_text || 'No answer text'}
                    </div>
                    {link.answer?.source_span && (
                      <SourceSpanViewer span={link.answer.source_span} title="Answer Source Span Evidence" onOpenPdfPage={onOpenPdfPage} />
                    )}

                  </div>

                  {/* Review Action Controls */}
                  <div className="bg-gray-800/80 p-3 rounded-lg border border-gray-700/80 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-semibold text-gray-300 mb-1 flex items-center space-x-1">
                          <User className="w-3.5 h-3.5 text-blue-400" />
                          <span>Reviewer Actor Name</span>
                        </label>
                        <input
                          type="text"
                          value={actorName}
                          onChange={(e) => setActorName(e.target.value)}
                          className="w-full bg-gray-950 border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-300 mb-1 flex items-center space-x-1">
                          <MessageSquare className="w-3.5 h-3.5 text-purple-400" />
                          <span>Review Rationale</span>
                        </label>
                        <input
                          type="text"
                          placeholder="Reason for certification or rejection..."
                          value={rationale}
                          onChange={(e) => setRationale(e.target.value)}
                          className="w-full bg-gray-950 border border-gray-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                        />
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 pt-2 border-t border-gray-700/80">
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleAction(link.id, 'accept')}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-2 px-3 rounded flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
                      >
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Accept & Verify</span>
                      </button>

                      <button
                        disabled={isSubmitting}
                        onClick={() => handleAction(link.id, 'reject')}
                        className="flex-1 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs py-2 px-3 rounded flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Reject</span>
                      </button>

                      <button
                        disabled={isSubmitting}
                        onClick={() => handleAction(link.id, 'mark_needs_resolution')}
                        className="flex-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs py-2 px-3 rounded flex items-center justify-center space-x-1.5 transition-colors disabled:opacity-50"
                      >
                        <AlertTriangle className="w-4 h-4" />
                        <span>Flag Ambiguous</span>
                      </button>
                    </div>
                  </div>

                  {/* Audit Event History */}
                  {link.review_events && link.review_events.length > 0 && (
                    <div className="border-t border-gray-800 pt-3 space-y-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center space-x-1">
                        <Clock className="w-3.5 h-3.5 text-blue-400" />
                        <span>Append-Only Review History Audit Log</span>
                      </h4>
                      <div className="space-y-1.5">
                        {link.review_events.map((evt) => (
                          <div key={evt.id} className="bg-gray-950 p-2.5 rounded text-xs border border-gray-800 flex items-start justify-between">
                            <div>
                              <span className="font-semibold text-blue-300">{evt.actor}</span> performed{' '}
                              <span className="font-bold text-amber-300 uppercase">{evt.action}</span>
                              {evt.rationale && <p className="text-gray-300 text-[11px] mt-0.5">"{evt.rationale}"</p>}
                            </div>
                            <span className="text-[10px] text-gray-500 font-mono">
                              {new Date(evt.timestamp).toLocaleString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
