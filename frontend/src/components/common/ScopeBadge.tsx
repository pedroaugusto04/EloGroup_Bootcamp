import React from 'react';
import { Database, BookOpen } from 'lucide-react';

interface ScopeBadgeProps {
  tables: string[];
  scope: string;
  devSection?: string;
}

export const ScopeBadge: React.FC<ScopeBadgeProps> = ({
  tables,
  scope,
  devSection,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-2 py-2 px-3 mb-5 rounded-md bg-[#121215] border border-[#27272a] text-xs text-[#a1a1aa]">
      <div className="flex items-center gap-1.5 font-mono text-[#38bdf8]">
        <Database className="w-3.5 h-3.5" />
        <span className="font-semibold uppercase text-[11px]">{tables.join(', ')}</span>
      </div>

      <span className="text-[#3f3f46]">•</span>

      <span className="text-[#d4d4d8]">{scope}</span>

      {devSection && (
        <>
          <span className="text-[#3f3f46]">•</span>
          <div className="flex items-center gap-1 text-[#71717a]">
            <BookOpen className="w-3.5 h-3.5" />
            <span>{devSection}</span>
          </div>
        </>
      )}
    </div>
  );
};
