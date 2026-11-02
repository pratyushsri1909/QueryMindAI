import React from 'react';
import { Table as TableIcon, Layers, Inbox } from 'lucide-react';

/**
 * ResultsTable component displaying dynamic query result rows and headers.
 */
export default function ResultsTable({ execution }) {
  const columns = execution?.columns || [];
  const rows = execution?.rows || [];
  const rowCount = execution?.row_count ?? rows.length;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      {/* Header bar */}
      <div className="flex items-center justify-between px-5 py-3.5 bg-slate-50/70 border-b border-slate-200">
        <div className="flex items-center space-x-2 text-slate-800">
          <TableIcon className="w-4 h-4 text-indigo-600" />
          <h2 className="text-sm font-semibold tracking-wide">Execution Results</h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center space-x-1 text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            <Layers className="w-3 h-3 text-slate-500" />
            <span>{rowCount} {rowCount === 1 ? 'row' : 'rows'} returned</span>
          </span>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto">
        {rows.length === 0 ? (
          <div className="py-12 px-4 text-center">
            <Inbox className="w-8 h-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-slate-600">No records found</p>
            <p className="text-xs text-slate-400 mt-1">The query returned zero matching rows.</p>
          </div>
        ) : (
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-slate-100/70 text-slate-600 text-xs uppercase tracking-wider font-semibold border-b border-slate-200">
                <th className="py-3 px-4 w-12 text-center text-slate-400 font-mono">#</th>
                {columns.map((col, idx) => (
                  <th key={idx} className="py-3 px-4 font-mono">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-indigo-50/40 transition-colors duration-100"
                >
                  <td className="py-3 px-4 text-center text-xs font-mono text-slate-400">
                    {rowIdx + 1}
                  </td>
                  {row.map((cell, colIdx) => (
                    <td
                      key={colIdx}
                      className="py-3 px-4 font-normal text-slate-800 text-sm whitespace-nowrap"
                    >
                      {cell !== null && cell !== undefined ? (
                        typeof cell === 'number' ? (
                          <span className="font-mono text-indigo-700 font-medium">
                            {cell}
                          </span>
                        ) : (
                          String(cell)
                        )
                      ) : (
                        <span className="italic text-slate-400 text-xs">null</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

