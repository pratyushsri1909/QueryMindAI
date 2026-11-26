import React from 'react';
import { Database, RefreshCw, Cpu, Server } from 'lucide-react';

/**
 * Header component displaying branding, backend health status, database connection, and active mode indicator.
 */
export default function Header({ backendStatus, onRefreshStatus, isCheckingStatus }) {
  const isDbConnected = backendStatus?.database === 'connected';
  const isChecking = backendStatus?.status === 'checking' || isCheckingStatus;
  const isHealthy = Boolean(backendStatus?.healthy);
  const mode = backendStatus?.mode || 'mock';
  const isDatabaseMode = mode === 'database';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          {/* Brand & Subtitle */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900">
                  QueryMind <span className="text-indigo-600">AI</span>
                </h1>
                <span className="text-xs px-2 py-0.5 font-medium rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  v1.0.0
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                Natural Language to SQL Query Assistant &bull; Academic Analytics Dashboard
              </p>
            </div>
          </div>

          {/* Right Status Badges */}
          <div className="flex items-center flex-wrap gap-2.5">
            {/* Pipeline Mode Indicator */}
            <div
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md border text-xs font-semibold ${
                isDatabaseMode
                  ? 'bg-indigo-50 text-indigo-800 border-indigo-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              }`}
            >
              <Cpu className={`w-3.5 h-3.5 ${isDatabaseMode ? 'text-indigo-600' : 'text-amber-600'}`} />
              <span>{isDatabaseMode ? 'DATABASE PIPELINE' : 'MOCK PIPELINE'}</span>
            </div>

            {/* PostgreSQL DB Status */}
            <div
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs font-medium border ${
                isDbConnected
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-slate-100 text-slate-600 border-slate-200'
              }`}
              title={isDbConnected ? "PostgreSQL database is connected" : "PostgreSQL database is currently disconnected"}
            >
              <Server className={`w-3.5 h-3.5 ${isDbConnected ? 'text-emerald-600' : 'text-slate-400'}`} />
              <span>DB: {isDbConnected ? 'Connected' : 'Offline'}</span>
            </div>

            {/* Backend Connectivity Status */}
            <div
              className={`flex items-center space-x-2 px-3 py-1 rounded-md text-xs font-medium border ${
                isHealthy
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : isChecking
                    ? 'bg-slate-100 text-slate-700 border-slate-200'
                    : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isHealthy
                    ? 'bg-emerald-500 animate-pulse'
                    : isChecking
                      ? 'bg-indigo-500 animate-pulse'
                      : 'bg-rose-500'
                }`}
              />
              <span>
                {isHealthy
                  ? 'Backend Connected'
                  : isChecking
                    ? 'Checking Backend...'
                    : 'Backend Disconnected'}
              </span>
              <button
                onClick={onRefreshStatus}
                disabled={isCheckingStatus}
                title="Refresh status"
                className="ml-1 p-0.5 text-slate-400 hover:text-slate-700 rounded transition"
              >
                <RefreshCw
                  className={`w-3 h-3 ${isCheckingStatus ? 'animate-spin text-indigo-600' : ''}`}
                />
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
