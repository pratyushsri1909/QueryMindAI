import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import QueryInput from './components/QueryInput';
import SqlPanel from './components/SqlPanel';
import ResultsTable from './components/ResultsTable';
import ExecutionInfo from './components/ExecutionInfo';
import { checkBackendHealth, executeQuery, getDatabaseStudents } from './services/queryService';
import { AlertTriangle, Database, ArrowRight, ShieldCheck, Cpu, Server, CheckCircle2, X } from 'lucide-react';

export default function App() {
  const [backendStatus, setBackendStatus] = useState({ healthy: false, status: 'checking', database: 'disconnected' });
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [queryResult, setQueryResult] = useState(null);

  // PostgreSQL direct inspection state
  const [showLiveDb, setShowLiveDb] = useState(false);
  const [liveDbStudents, setLiveDbStudents] = useState(null);
  const [liveDbLoading, setLiveDbLoading] = useState(false);
  const [liveDbError, setLiveDbError] = useState('');

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

  // Handle query execution (Day 2 prototype flow)
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

  // Fetch live PostgreSQL students
  const handleFetchLiveStudents = async () => {
    if (showLiveDb && liveDbStudents) {
      setShowLiveDb(false);
      return;
    }
    setShowLiveDb(true);
    setLiveDbLoading(true);
    setLiveDbError('');

    try {
      const res = await getDatabaseStudents();
      setLiveDbStudents(res);
    } catch (err) {
      setLiveDbError(err.message || 'Failed to fetch PostgreSQL records.');
    } finally {
      setLiveDbLoading(false);
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

        {/* PostgreSQL Direct Verification Action Bar */}
        <div className="flex items-center justify-between bg-white px-5 py-3 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center space-x-2 text-xs text-slate-600">
            <Server className={`w-4 h-4 ${backendStatus.database === 'connected' ? 'text-emerald-600' : 'text-slate-400'}`} />
            <span className="font-medium">PostgreSQL 18 Foundation:</span>
            <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${
              backendStatus.database === 'connected' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
            }`}>
              {backendStatus.database === 'connected' ? 'querymind_db (Connected)' : 'Disconnected'}
            </span>
          </div>

          <button
            type="button"
            onClick={handleFetchLiveStudents}
            disabled={liveDbLoading}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-200 text-xs font-semibold text-slate-700 transition"
          >
            <Database className="w-3.5 h-3.5 text-indigo-600" />
            <span>{showLiveDb ? 'Hide PostgreSQL Data' : 'Inspect Live PostgreSQL Students'}</span>
          </button>
        </div>

        {/* Live PostgreSQL Data Inspector Panel */}
        {showLiveDb && (
          <div className="bg-white rounded-2xl border border-emerald-200 p-6 shadow-sm space-y-4 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Live PostgreSQL Records &bull; <code className="text-xs font-mono text-indigo-600">GET /api/v1/database/students</code>
                </h3>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  REAL POSTGRESQL DATA
                </span>
              </div>
              <button
                type="button"
                onClick={() => setShowLiveDb(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {liveDbLoading && (
              <div className="py-6 text-center text-xs text-slate-500 font-medium">
                Querying PostgreSQL database...
              </div>
            )}

            {liveDbError && (
              <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-3 rounded-lg">
                {liveDbError}
              </div>
            )}

            {liveDbStudents && !liveDbLoading && (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 uppercase font-semibold border-b border-slate-200">
                      <th className="py-2.5 px-3">Student ID</th>
                      <th className="py-2.5 px-3">Name</th>
                      <th className="py-2.5 px-3">Batch</th>
                      <th className="py-2.5 px-3">CGPA</th>
                      <th className="py-2.5 px-3">Department</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {liveDbStudents.data.map((st) => (
                      <tr key={st.student_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono font-medium text-slate-500">{st.student_id}</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-800">{st.name}</td>
                        <td className="py-2.5 px-3 text-slate-600 font-mono">{st.batch}</td>
                        <td className="py-2.5 px-3 font-mono font-bold text-indigo-600">{st.cgpa}</td>
                        <td className="py-2.5 px-3 text-slate-700">{st.department}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="text-[11px] text-slate-400 mt-2">
                  Retrieved {liveDbStudents.count} verified records directly from PostgreSQL <code className="text-slate-600">querymind_db.students</code> via SQLAlchemy ORM.
                </p>
              </div>
            )}
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
          <span>QueryMind AI &bull; Academic NLP-to-SQL Architecture &bull; Day 3 Database Foundation</span>
          <span className="text-slate-400">Member 3: Backend, Frontend &amp; Integration</span>
        </div>
      </footer>
    </div>
  );
}
