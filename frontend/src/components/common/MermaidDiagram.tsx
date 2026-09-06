import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
}

mermaid.initialize({
  startOnLoad: false,
  suppressErrorRendering: true,
  securityLevel: 'loose',
  theme: 'dark',
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
  const [error, setError] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      const cleanChart = chart.trim();
      if (!cleanChart) return;

      try {
        // Step 1: Validate syntax with mermaid.parse
        const isValid = await mermaid.parse(cleanChart, { suppressErrors: true }).catch(() => false);
        if (!isValid) {
          if (isMounted) setError(true);
          return;
        }

        // Step 2: Render SVG
        const uniqueId = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
        const { svg } = await mermaid.render(uniqueId, cleanChart);

        if (isMounted) {
          if (svg.includes('Syntax error in text') || svg.includes('mermaid version')) {
            setError(true);
          } else {
            setSvgContent(svg);
            setError(false);
          }
        }
      } catch (err) {
        if (isMounted) {
          setError(true);
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
      <div className="my-4 p-4 rounded-xl border border-[#27272a] bg-[#11131a]">
        <div className="text-xs font-mono text-[#a1a1aa] mb-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#38bdf8]" />
          <span>Estrutura / Fluxo do Diagrama</span>
        </div>
        <pre className="font-mono text-xs text-[#38bdf8] overflow-x-auto p-3.5 rounded-lg bg-[#09090b] border border-[#27272a]/60 leading-relaxed whitespace-pre-wrap">
          {chart}
        </pre>
      </div>
    );
  }

  if (!svgContent) {
    return (
      <div className="my-4 p-5 rounded-xl border border-[#27272a] bg-[#11131a] flex items-center justify-center text-xs text-[#71717a]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#38bdf8] animate-ping" />
          <span>Renderizando diagrama...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="my-4 p-4 rounded-xl border border-[#27272a] bg-[#11131a] overflow-x-auto shadow-md">
      <div
        ref={containerRef}
        className="mermaid-wrapper flex justify-center text-xs min-w-full [&_svg]:max-w-full [&_svg]:h-auto [&_svg]:min-w-[300px]"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
};
