import React, { useState } from 'react';
import { VerifiedSampleExport } from '../types';
import { Download, CheckCircle2, FileCode, Copy, Check } from 'lucide-react';

interface ExportViewProps {
  samples: VerifiedSampleExport[];
  isLoading: boolean;
}

export const ExportView: React.FC<ExportViewProps> = ({ samples, isLoading }) => {
  const [copied, setCopied] = useState(false);

  const downloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(samples, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "ekc_verified_samples.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const downloadJsonl = () => {
    const jsonlLines = samples.map((s) => JSON.stringify(s)).join('\n');
    const dataStr = "data:text/plain;charset=utf-8," + encodeURIComponent(jsonlLines);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "ekc_verified_samples.jsonl");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(samples, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-[calc(100vh-80px)] p-6 flex flex-col space-y-4">
      {/* Header & Export Actions */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3">
          <div className="bg-emerald-600/20 text-emerald-400 p-2 rounded-lg border border-emerald-600/30">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Certified EKC Compilation Export</h2>
            <p className="text-xs text-gray-400">
              Only verified (X, Y) sample units crossing the compilation threshold
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-1.5 bg-gray-700 hover:bg-gray-600 text-white font-semibold text-xs py-2 px-3 rounded transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied JSON' : 'Copy JSON'}</span>
          </button>

          <button
            onClick={downloadJson}
            className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs py-2 px-3 rounded transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download JSON</span>
          </button>

          <button
            onClick={downloadJsonl}
            className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs py-2 px-3 rounded transition-colors"
          >
            <FileCode className="w-4 h-4" />
            <span>Download JSONL</span>
          </button>
        </div>
      </div>

      {/* Export Samples Preview */}
      <div className="flex-1 bg-gray-800 border border-gray-700 rounded-xl p-4 flex flex-col overflow-hidden shadow-lg">
        <div className="border-b border-gray-700 pb-3 mb-3 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-gray-300">
            Certified (X, Y) Compilation Units ({samples.length})
          </span>
          <span className="text-xs text-emerald-400 font-semibold bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded">
            Excludes all candidate & unresolved links
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {isLoading ? (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              Loading verified export samples...
            </div>
          ) : samples.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              No certified samples found. Review and accept candidates in the Review Queue to populate exports.
            </div>
          ) : (
            samples.map((sample) => (
              <div key={sample.sample_id} className="bg-gray-900 border border-gray-700 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-xs font-mono text-emerald-300 bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded">
                      {sample.sample_id}
                    </span>
                    <span className="text-xs text-gray-300 font-medium">
                      Chapter: {sample.chapter_title} (Sec {sample.section_number})
                    </span>
                  </div>
                  <span className="text-xs uppercase bg-gray-800 text-gray-300 px-2 py-0.5 rounded border border-gray-700 font-semibold">
                    {sample.item_type}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                  <div className="bg-gray-950 p-3 rounded border border-gray-800 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-blue-400 font-sans block">X: Input Prompt</span>
                    <p className="text-gray-100">{sample.prompt_text}</p>
                  </div>
                  <div className="bg-gray-950 p-3 rounded border border-gray-800 space-y-1">
                    <span className="text-[10px] uppercase font-bold text-emerald-400 font-sans block">Y: Certified Target Answer</span>
                    <p className="text-emerald-300">{sample.answer_text}</p>
                  </div>
                </div>

                <details className="text-[11px] text-gray-400 bg-gray-950 p-2.5 rounded border border-gray-800 font-mono">
                  <summary className="cursor-pointer text-gray-400 font-sans font-semibold hover:text-white">
                    View Provenance Metadata JSON
                  </summary>
                  <pre className="mt-2 text-emerald-400 whitespace-pre-wrap overflow-x-auto">
                    {JSON.stringify(sample.provenance, null, 2)}
                  </pre>
                </details>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
