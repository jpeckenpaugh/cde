import React from 'react';
import { NavLink } from 'react-router-dom';
import { BookOpen, ListChecks, CheckCircle, Download, FileText } from 'lucide-react';

interface NavbarProps {
  reviewQueueCount: number;
  verifiedCount: number;
  onOpenPdf?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  reviewQueueCount,
  verifiedCount,
  onOpenPdf,
}) => {
  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center space-x-3">
        <div className="bg-blue-600 p-2 rounded-lg text-white font-bold text-xl flex items-center justify-center">
          <BookOpen className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">Algebra EKC Workbench</h1>
          <p className="text-xs text-gray-400">Human Review & Empirical Knowledge Certification Surface</p>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <NavLink
          to="/corpus"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`
          }
        >
          <BookOpen className="w-4 h-4" />
          <span>Corpus Tree</span>
        </NavLink>

        <NavLink
          to="/queue"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`
          }
        >
          <ListChecks className="w-4 h-4" />
          <span>Review Queue</span>
          {reviewQueueCount > 0 && (
            <span className="bg-amber-500 text-gray-950 font-bold text-xs px-2 py-0.5 rounded-full">
              {reviewQueueCount}
            </span>
          )}
        </NavLink>

        <NavLink
          to="/export"
          className={({ isActive }) =>
            `flex items-center space-x-2 px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              isActive
                ? 'bg-blue-600 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white'
            }`
          }
        >
          <Download className="w-4 h-4" />
          <span>EKC Export</span>
          {verifiedCount > 0 && (
            <span className="bg-emerald-500 text-gray-950 font-bold text-xs px-2 py-0.5 rounded-full">
              {verifiedCount}
            </span>
          )}
        </NavLink>

        {onOpenPdf && (
          <button
            onClick={onOpenPdf}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-md font-medium text-sm text-gray-300 hover:text-white hover:bg-gray-700 transition border border-gray-700 ml-2"
            title="Open OpenStax Elementary Algebra PDF Document"
          >
            <FileText className="w-4 h-4 text-amber-400" />
            <span>Open PDF</span>
          </button>
        )}
      </div>
    </nav>
  );
};


