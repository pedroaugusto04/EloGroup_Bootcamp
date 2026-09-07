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
      className={`relative p-3 sm:p-4 rounded-lg border bg-[#11131a] transition-all duration-150 flex flex-col justify-between ${
        highlight
          ? 'border-[#38bdf8]/40 shadow-[0_0_15px_rgba(56,189,248,0.06)]'
          : 'border-[#27272a] hover:border-[#3f3f46]'
      }`}
      title={help}
    >
      <div className="flex items-start justify-between gap-1.5 mb-1 sm:mb-1.5">
        <span className="text-[11px] sm:text-xs font-medium text-[#a1a1aa] tracking-tight leading-tight line-clamp-1">{label}</span>
        {trend && (
          <span
            className={`text-[10px] sm:text-[11px] font-mono font-medium px-1.5 py-0.2 rounded shrink-0 whitespace-nowrap ${
              trend.isNeutral
                ? 'bg-[#27272a] text-[#a1a1aa]'
                : trend.isPositive
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}
          >
            {trend.value}
          </span>
        )}
      </div>

      <div>
        <div className="text-lg sm:text-xl md:text-2xl font-bold font-mono tracking-tight text-[#f4f4f5] truncate">
          {value}
        </div>

        {subtitle && (
          <div className="text-[10px] sm:text-[11px] text-[#71717a] mt-0.5 sm:mt-1 font-sans truncate">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
