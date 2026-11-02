import React, { useState } from 'react';
import { Terminal, Copy, Check, Code } from 'lucide-react';

/**
 * SqlPanel component displaying the synthesized SQL query with one-click clipboard copy.
 */
export default function SqlPanel({ sqlQuery }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!sqlQuery) return;
    try {
      await navigator.clipboard.writeText(sqlQuery);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback if clipboard API is restricted
      const textarea = document.createElement('textarea');
      textarea.value = sqlQuery;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      {/* Panel Header */}
      <div className="flex items-center justify-between px-5 py-3.5 bg-slate-50/70 border-b border-slate-200">
        <div className="flex items-center space-x-2 text-slate-800">
          <Terminal className="w-4 h-4 text-indigo-600" />
          <h2 className="text-sm font-semibold tracking-wide">Generated SQL</h2>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
            PostgreSQL / ANSI
          </span>
        </div>

        <button
          onClick={handleCopy}
          type="button"
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 transition shadow-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-slate-500" />
              <span>Copy SQL</span>
            </>
          )}
        </button>
      </div>

      {/* Code Display Area */}
      <div className="p-5 bg-slate-900 text-slate-100 overflow-x-auto">
        <pre className="font-mono text-sm leading-relaxed whitespace-pre-wrap select-all">
          <code className="text-emerald-400">
            {sqlQuery || "-- No SQL generated"}
          </code>
        </pre>
      </div>

      {/* Footer Info */}
      <div className="px-5 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span className="flex items-center space-x-1">
          <Code className="w-3 h-3 text-slate-400" />
          <span>Synthesized from Intermediate Representation (IR) via Mock SQL Engine</span>
        </span>
        <span className="font-medium text-slate-400">Read-Only Safe Target</span>
      </div>
    </div>
  );
}
