import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    darkMode: true,
    background: '#11131a',
    primaryColor: '#0284c7',
    primaryTextColor: '#f4f4f5',
    primaryBorderColor: '#38bdf8',
    lineColor: '#38bdf8',
    secondaryColor: '#18181b',
    tertiaryColor: '#27272a',
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: '13px',
    textColor: '#f4f4f5',
    mainBkg: '#18181b',
    nodeBorder: '#38bdf8',
    clusterBkg: '#121215',
    titleColor: '#38bdf8',
    edgeLabelBackground: '#18181b',
  },
});

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ chart }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      const cleanChart = chart.trim();
      if (!cleanChart) return;
      try {
        const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(uniqueId, cleanChart);
        if (isMounted) {
          setSvgContent(svg);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          console.warn('Mermaid render error:', err);
          setError(err?.message || 'Erro ao renderizar diagrama Mermaid');
        }
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chart]);

  if (error) {
    return (
      <div className="my-4 p-4 rounded-xl border border-[#27272a] bg-[#121215] text-xs">
        <div className="text-[#a1a1aa] font-semibold mb-2 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-400" />
          <span>Diagrama Estratégico (Visualização em Texto)</span>
        </div>
        <pre className="font-mono text-[12px] text-[#38bdf8] overflow-x-auto p-3 rounded-lg bg-[#09090b] border border-[#27272a]/60 leading-relaxed whitespace-pre-wrap">
          {chart}
        </pre>
      </div>
    );
  }

  if (!svgContent) {
    return (
      <div className="my-4 p-6 rounded-xl border border-[#27272a] bg-[#11131a] flex items-center justify-center text-xs text-[#71717a]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping" />
          <span>Gerando diagrama visual...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="my-4 p-4 rounded-xl border border-[#27272a] bg-[#11131a] overflow-x-auto shadow-md">
      <div
        ref={containerRef}
        className="mermaid-wrapper flex justify-center text-xs min-w-full [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:min-w-[320px]"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
};
