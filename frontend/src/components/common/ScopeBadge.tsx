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
    <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 py-1.5 px-2.5 sm:py-2 sm:px-3 mb-4 sm:mb-5 rounded-md bg-[#121024] border border-[#262046] text-[11px] sm:text-xs text-[#a1a1aa] leading-relaxed">
      <div className="flex items-center gap-1 sm:gap-1.5 font-mono text-[#8575ff]">
        <Database className="w-3 sm:w-3.5 h-3 sm:h-3.5 shrink-0" />
        <span className="font-semibold uppercase text-[10px] sm:text-[11px]">{tables.join(', ')}</span>
      </div>

      <span className="text-[#372e61] hidden xs:inline">•</span>

      <span className="text-[#d4d4d8] text-[11px] sm:text-xs">{scope}</span>

      {devSection && (
        <>
          <span className="text-[#372e61] hidden sm:inline">•</span>
          <div className="flex items-center gap-1 text-[#71717a] text-[10px] sm:text-xs w-full sm:w-auto mt-0.5 sm:mt-0">
            <BookOpen className="w-3 sm:w-3.5 h-3 sm:h-3.5 shrink-0" />
            <span className="truncate">{devSection}</span>
          </div>
        </>
      )}
    </div>
  );
};
