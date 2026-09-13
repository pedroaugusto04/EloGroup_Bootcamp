import React, { useState, useMemo } from 'react';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  searchPlaceholder?: string;
  searchKey?: keyof T | ((row: T) => string);
  pageSize?: number;
  emptyMessage?: string;
}

export function DataTable<T extends Record<string, any>>({
  columns,
  data,
  searchPlaceholder = 'Buscar registros...',
  searchKey,
  pageSize = 10,
  emptyMessage = 'Nenhum dado encontrado para o filtro selecionado.',
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) return data;
    const term = searchTerm.toLowerCase();

    return data.filter(row => {
      if (typeof searchKey === 'function') {
        return searchKey(row).toLowerCase().includes(term);
      }
      if (searchKey && row[searchKey]) {
        return String(row[searchKey]).toLowerCase().includes(term);
      }
      return Object.values(row).some(val =>
        String(val).toLowerCase().includes(term)
      );
    });
  }, [data, searchTerm, searchKey]);

  const totalPages = Math.max(1, Math.ceil(filteredData.length / pageSize));
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, currentPage, pageSize]);

  return (
    <div className="w-full rounded-lg border border-[#e6e5f0] dark:border-[#262046] bg-[#ffffff] dark:bg-[#131126] overflow-hidden shadow-sm">
      {/* Search Header */}
      <div className="p-2.5 sm:p-3 border-b border-[#e6e5f0] dark:border-[#262046] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 sm:gap-4 bg-[#f8f7fc] dark:bg-[#121024]">
        <div className="relative flex-1 w-full sm:max-w-sm">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#8e92a0] dark:text-[#71717a]" />
          <input
            type="text"
            value={searchTerm}
            onChange={e => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            placeholder={searchPlaceholder}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] rounded-md text-[#131920] dark:text-[#f4f4f5] placeholder-[#8e92a0] dark:placeholder-[#71717a] focus:outline-none focus:border-[#4200db] dark:focus:border-[#8575ff]/60 transition-colors shadow-inner"
          />
        </div>

        <div className="text-[11px] font-mono text-[#5e6270] dark:text-[#71717a] text-right sm:text-left self-end sm:self-center">
          {filteredData.length} registros
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto touch-pan-x">
        <table className="w-full text-xs text-left min-w-[500px] sm:min-w-full">
          <thead className="bg-[#f3f2f8] dark:bg-[#181530] text-[#5e6270] dark:text-[#a1a1aa] font-medium border-b border-[#e6e5f0] dark:border-[#262046]">
            <tr>
              {columns.map(col => (
                <th
                  key={col.key}
                  className={`py-2 px-2.5 sm:py-2.5 sm:px-3.5 tracking-tight whitespace-nowrap ${
                    col.align === 'right'
                      ? 'text-right'
                      : col.align === 'center'
                      ? 'text-center'
                      : 'text-left'
                  } ${col.className || ''}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#e6e5f0] dark:divide-[#262046]/60 font-sans">
            {paginatedData.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="py-8 text-center text-[#8e92a0] dark:text-[#71717a] font-mono text-xs"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-[#f8f7fc] dark:hover:bg-[#181530]/50 transition-colors duration-100"
                >
                  {columns.map(col => (
                    <td
                      key={col.key}
                      className={`py-2 px-2.5 sm:py-2.5 sm:px-3.5 ${
                        col.align === 'right'
                          ? 'text-right font-mono'
                          : col.align === 'center'
                          ? 'text-center'
                          : 'text-left'
                      } ${col.className || ''}`}
                    >
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="p-2.5 sm:p-3 border-t border-[#e6e5f0] dark:border-[#262046] bg-[#f8f7fc] dark:bg-[#121024] flex items-center justify-between text-xs text-[#5e6270] dark:text-[#a1a1aa]">
          <div>
            Pág. <span className="font-mono text-[#131920] dark:text-[#f4f4f5]">{currentPage}</span> de{' '}
            <span className="font-mono text-[#131920] dark:text-[#f4f4f5]">{totalPages}</span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5] disabled:opacity-40 disabled:cursor-not-allowed transition-colors active:scale-95"
              aria-label="Página anterior"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded bg-[#ffffff] dark:bg-[#181530] border border-[#e6e5f0] dark:border-[#262046] text-[#5e6270] dark:text-[#a1a1aa] hover:text-[#131920] dark:hover:text-[#f4f4f5] disabled:opacity-40 disabled:cursor-not-allowed transition-colors active:scale-95"
              aria-label="Próxima página"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
