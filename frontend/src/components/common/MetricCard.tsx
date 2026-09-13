import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    isNeutral?: boolean;
  };
  highlight?: boolean;
  help?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtitle,
  trend,
  highlight,
  help,
}) => {
  return (
    <div
      className={`relative p-3 sm:p-4 rounded-lg border bg-[#ffffff] dark:bg-[#131126] transition-all duration-150 flex flex-col justify-between shadow-sm ${
        highlight
          ? 'border-[#4200db]/40 dark:border-[#8575ff]/50 shadow-[0_0_15px_rgba(66,0,219,0.06)] dark:shadow-[0_0_15px_rgba(133,117,255,0.12)]'
          : 'border-[#e6e5f0] dark:border-[#262046] hover:border-[#cbd5e1] dark:hover:border-[#4a3f85]'
      }`}
      title={help}
    >
      <div className="flex items-start justify-between gap-1.5 mb-1 sm:mb-1.5">
        <span className="text-[11px] sm:text-xs font-medium text-[#5e6270] dark:text-[#a1a1aa] tracking-tight leading-tight line-clamp-1">{label}</span>
        {trend && (
          <span
            className={`text-[10px] sm:text-[11px] font-mono font-medium px-1.5 py-0.2 rounded shrink-0 whitespace-nowrap ${
              trend.isNeutral
                ? 'bg-[#f3f2f8] dark:bg-[#1f1a3a] text-[#5e6270] dark:text-[#a1a1aa] border border-[#e6e5f0] dark:border-[#262046]'
                : trend.isPositive
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>

      <div>
        <div className="text-lg sm:text-xl md:text-2xl font-bold font-mono tracking-tight text-[#131920] dark:text-[#f4f4f5] truncate">
          {value}
        </div>

        {subtitle && (
          <div className="text-[10px] sm:text-[11px] text-[#8e92a0] dark:text-[#71717a] mt-0.5 sm:mt-1 font-sans truncate">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
