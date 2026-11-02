import React, { useState } from 'react';
import { Search, Sparkles, CornerDownLeft, XCircle, AlertCircle } from 'lucide-react';

const EXAMPLE_QUERIES = [
  "Show students with CGPA above 8.5",
  "Show top students ordered by CGPA",
  "Find courses with credits equal to 4",
  "List all students",
];

/**
 * QueryInput component with query suggestions, validation, and submission states.
 */
export default function QueryInput({ onExecuteQuery, isLoading }) {
  const [queryText, setQueryText] = useState("");
  const [localError, setLocalError] = useState("");

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    const trimmed = queryText.trim();
    if (!trimmed) {
      setLocalError("Query cannot be empty or contain only whitespace.");
      return;
    }
    if (trimmed.length > 500) {
      setLocalError(`Query is too long (${trimmed.length}/500 max characters).`);
      return;
    }
    setLocalError("");
    onExecuteQuery(trimmed);
  };

  const handleSelectExample = (example) => {
    setQueryText(example);
    setLocalError("");
    onExecuteQuery(example);
  };

  const handleClear = () => {
    setQueryText("");
    setLocalError("");
  };

  const handleKeyDown = (e) => {
    // Submit on Enter unless Shift is held
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <label
          htmlFor="query-input"
          className="text-sm font-semibold text-slate-800 flex items-center space-x-2"
        >
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Ask Your Database in Natural Language</span>
        </label>
        <span
          className={`text-xs font-mono ${
            queryText.length > 500 ? 'text-rose-600 font-bold' : 'text-slate-400'
          }`}
        >
          {queryText.length} / 500
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            id="query-input"
            rows={3}
            value={queryText}
            onChange={(e) => {
              setQueryText(e.target.value);
              if (localError) setLocalError("");
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask your database anything in natural language... (e.g. 'Show students with CGPA above 8.5')"
            disabled={isLoading}
            className={`w-full p-4 rounded-xl border text-sm text-slate-900 bg-slate-50/50 focus:bg-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all resize-none ${
              localError
                ? 'border-rose-300 focus:ring-rose-400 focus:border-rose-400'
                : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'
            }`}
          />

          {queryText && !isLoading && (
            <button
              type="button"
              onClick={handleClear}
              title="Clear input"
              className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 p-1"
            >
              <XCircle className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Validation Error Message */}
        {localError && (
          <div className="flex items-center space-x-2 text-xs text-rose-600 bg-rose-50 border border-rose-200 rounded-lg p-2.5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{localError}</span>
          </div>
        )}

        {/* Action Row */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
          {/* Example Suggestions */}
          <div className="flex items-center flex-wrap gap-1.5 text-xs">
            <span className="text-slate-400 font-medium mr-1 hidden sm:inline">Try:</span>
            {EXAMPLE_QUERIES.map((example, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectExample(example)}
                disabled={isLoading}
                className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600 border border-slate-200 hover:border-indigo-200 transition text-xs font-medium"
              >
                {example}
              </button>
            ))}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !queryText.trim()}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Execute Query</span>
                <CornerDownLeft className="w-3.5 h-3.5 opacity-60 ml-0.5 hidden sm:inline" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

