import React, { useState } from 'react';
import { Clock, ShieldCheck, Tag, Info, ChevronDown, ChevronRight, FileJson } from 'lucide-react';

/**
 * ExecutionInfo component showing query summary, execution metadata, and mock disclaimers.
 */
export default function ExecutionInfo({ result }) {
  const [showIR, setShowIR] = useState(false);

  if (!result) return null;

  const {
    original_query,
    intent,
    execution,
    ir,
  } = result;

  return (
    <div className="space-y-4">
      {/* Summary Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Original Query */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
            <Info className="w-3.5 h-3.5 text-indigo-500" />
            <span>Parsed Query</span>
          </span>
          <p className="mt-2 text-sm font-medium text-slate-900 line-clamp-2" title={original_query}>
            "{original_query}"
          </p>
        </div>

        {/* Card 2: Intent */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
            <Tag className="w-3.5 h-3.5 text-indigo-500" />
            <span>Detected Intent</span>
          </span>
          <div className="mt-2 flex items-center">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
              {intent || 'UNKNOWN'}
            </span>
          </div>
        </div>

        {/* Card 3: Execution Status */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Execution Status</span>
          </span>
          <div className="mt-2 flex items-center space-x-2">
            <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              <span>{execution?.status || 'mock_success'}</span>
            </span>
            <span className="text-[11px] font-bold text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
              MOCK
            </span>
          </div>
        </div>

        {/* Card 4: Execution Latency */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center space-x-1.5">
            <Clock className="w-3.5 h-3.5 text-indigo-500" />
            <span>Mock Latency</span>
          </span>
          <p className="mt-2 text-sm font-mono font-semibold text-slate-800">
            {execution?.execution_time_ms ?? 12} ms
          </p>
        </div>
      </div>

      {/* Prominent Mock Notice Banner */}
      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-3.5 text-xs text-amber-900 flex items-start space-x-2.5">
        <Info className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Integration Prototype Mode:</span> Results and generated SQL above are produced by deterministic mock NLP and mock SQL engine components for Day 2 pipeline verification. No physical PostgreSQL queries or machine learning inference were performed.
        </div>
      </div>

      {/* Expandable Intermediate Representation (IR) Inspector */}
      {ir && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <button
            type="button"
            onClick={() => setShowIR(!showIR)}
            className="w-full px-4 py-2.5 bg-slate-50 hover:bg-slate-100/70 text-left flex items-center justify-between transition text-xs font-semibold text-slate-700"
          >
            <span className="flex items-center space-x-2">
              <FileJson className="w-3.5 h-3.5 text-indigo-600" />
              <span>Intermediate Representation (IR) Contract</span>
            </span>
            <span className="flex items-center space-x-1 text-slate-500 font-normal">
              <span>{showIR ? 'Hide IR Payload' : 'Inspect IR Payload'}</span>
              {showIR ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </span>
          </button>

          {showIR && (
            <div className="p-4 bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto border-t border-slate-200">
              <pre>{JSON.stringify(ir, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

