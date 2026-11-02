import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import QueryInput from './components/QueryInput';
import SqlPanel from './components/SqlPanel';
import ResultsTable from './components/ResultsTable';
import ExecutionInfo from './components/ExecutionInfo';
import { checkBackendHealth, executeQuery } from './services/queryService';
import { AlertTriangle, Database, ArrowRight, ShieldCheck, Cpu } from 'lucide-react';

export default function App() {
  const [backendStatus, setBackendStatus] = useState({ healthy: false, status: 'checking' });
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [queryResult, setQueryResult] = useState(null);

  // Probe backend status on mount
  const checkStatus = useCallback(async () => {
    setIsCheckingStatus(true);
    const status = await checkBackendHealth();
    setBackendStatus(status);
    setIsCheckingStatus(false);
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  // Handle query execution
  const handleExecuteQuery = async (queryText) => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const response = await executeQuery(queryText);
      setQueryResult(response);
    } catch (err) {
      setQueryResult(null);
      setErrorMessage(err.message || 'An unexpected error occurred while executing the query.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Sticky Top Header */}
      <Header
        backendStatus={backendStatus}
        onRefreshStatus={checkStatus}
        isCheckingStatus={isCheckingStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Backend Offline Warning Banner */}
        {!backendStatus.healthy && backendStatus.status !== 'checking' && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start space-x-3 text-rose-900 shadow-xs">
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <span className="font-bold">Backend Service Unavailable:</span> Cannot reach the FastAPI server at{' '}
              <code className="px-1.5 py-0.5 rounded bg-rose-100 font-mono text-xs">
                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
              </code>
              . Please start the backend service using{' '}
              <code className="px-1.5 py-0.5 rounded bg-rose-100 font-mono text-xs">
                uvicorn app.main:app --reload
              </code>{' '}
              in the <code className="font-mono text-xs">backend/</code> directory.
            </div>
          </div>
        )}

        {/* Natural Language Query Input */}
        <section aria-label="Natural Language Query Input">
          <QueryInput
            onExecuteQuery={handleExecuteQuery}
            isLoading={isLoading}
          />
        </section>

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start space-x-3 text-rose-900 shadow-sm animate-fadeIn">
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm flex-1">
              <span className="font-bold">Query Error: </span>
              <span>{errorMessage}</span>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center shadow-sm">
            <div className="inline-flex items-center justify-center p-3 rounded-full bg-indigo-50 text-indigo-600 mb-3 animate-pulse">
              <Database className="w-6 h-6 animate-bounce" />
            </div>
            <p className="text-sm font-semibold text-slate-800">
              Processing Natural Language Query...
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Validating syntax &bull; Extracting intent &bull; Generating ANSI SQL &bull; Simulating execution
            </p>
          </div>
        )}

        {/* Results Section */}
        {queryResult && !isLoading && (
          <section aria-label="Query Execution Results" className="space-y-6">
            {/* Summary & Execution Metrics */}
            <ExecutionInfo result={queryResult} />

            {/* Generated SQL Panel */}
            <SqlPanel sqlQuery={queryResult.generated_sql} />

            {/* Dynamic Results Table */}
            <ResultsTable execution={queryResult.execution} />
          </section>
        )}

        {/* Initial Empty State (When no query has run yet) */}
        {!queryResult && !isLoading && !errorMessage && (
          <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center shadow-sm">
            <div className="max-w-md mx-auto space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto shadow-inner">
                <Database className="w-6 h-6" />
              </div>
              <h2 className="text-base font-semibold text-slate-900">
                Ready for Natural Language Querying
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                Type a natural language query in the prompt above or click one of the suggested example buttons (such as{' '}
                <span className="font-semibold text-slate-700">"Show students with CGPA above 8.5"</span>) to test the end-to-end integration pipeline.
              </p>

              {/* Architectural Pipeline Badge Checklist */}
              <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-600">
                <span className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-100 font-medium">
                  <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Pydantic Input Validation</span>
                </span>
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <span className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-100 font-medium">
                  <Cpu className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Mock NLP &rarr; IR</span>
                </span>
                <ArrowRight className="w-3 h-3 text-slate-400" />
                <span className="flex items-center space-x-1 px-2.5 py-1 rounded bg-slate-100 font-medium">
                  <Database className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Mock SQL Engine</span>
                </span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>QueryMind AI &bull; Academic NLP-to-SQL Architecture &bull; Day 2 Implementation</span>
          <span className="text-slate-400">Member 3: Backend, Frontend &amp; Integration</span>
        </div>
      </footer>
    </div>
  );
}

