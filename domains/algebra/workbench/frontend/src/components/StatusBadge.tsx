import React from 'react';
import { CheckCircle2, Clock, XCircle, AlertTriangle, Eye } from 'lucide-react';

interface StatusBadgeProps {
  status: 'candidate' | 'reviewed' | 'verified' | 'rejected' | 'needs_resolution' | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  switch (status) {
    case 'verified':
      return (
        <span className="inline-flex items-center space-x-1 bg-emerald-950 text-emerald-300 border border-emerald-700 text-xs px-2.5 py-1 rounded-full font-medium">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Verified</span>
        </span>
      );
    case 'candidate':
      return (
        <span className="inline-flex items-center space-x-1 bg-amber-950 text-amber-300 border border-amber-700 text-xs px-2.5 py-1 rounded-full font-medium">
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          <span>Candidate</span>
        </span>
      );
    case 'reviewed':
      return (
        <span className="inline-flex items-center space-x-1 bg-blue-950 text-blue-300 border border-blue-700 text-xs px-2.5 py-1 rounded-full font-medium">
          <Eye className="w-3.5 h-3.5 text-blue-400" />
          <span>Reviewed</span>
        </span>
      );
    case 'rejected':
      return (
        <span className="inline-flex items-center space-x-1 bg-rose-950 text-rose-300 border border-rose-700 text-xs px-2.5 py-1 rounded-full font-medium">
          <XCircle className="w-3.5 h-3.5 text-rose-400" />
          <span>Rejected</span>
        </span>
      );
    case 'needs_resolution':
      return (
        <span className="inline-flex items-center space-x-1 bg-purple-950 text-purple-300 border border-purple-700 text-xs px-2.5 py-1 rounded-full font-medium">
          <AlertTriangle className="w-3.5 h-3.5 text-purple-400" />
          <span>Needs Resolution</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center space-x-1 bg-gray-800 text-gray-300 border border-gray-700 text-xs px-2 py-0.5 rounded-full font-medium">
          <span>{status}</span>
        </span>
      );
  }
};
