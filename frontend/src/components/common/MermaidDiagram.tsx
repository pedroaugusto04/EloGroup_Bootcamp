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
    mainBkg: '#18181b',
    primaryColor: '#0284c7',
    primaryTextColor: '#ffffff',
    primaryBorderColor: '#38bdf8',
    lineColor: '#38bdf8',
    secondaryColor: '#1e293b',
    secondaryTextColor: '#ffffff',
    secondaryBorderColor: '#60a5fa',
    tertiaryColor: '#2e1065',
    tertiaryTextColor: '#ffffff',
    tertiaryBorderColor: '#a78bfa',
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: '13px',
    textColor: '#f4f4f5',
    nodeBorder: '#38bdf8',
    nodeTextColor: '#ffffff',
    clusterBkg: '#121215',
    clusterBorder: '#27272a',
    titleColor: '#38bdf8',
    edgeLabelBackground: '#18181b',

    // Timeline / Multi-section Color Scales (avoids dark unreadable center cards)
    cScale0: '#0284c7', // Cyan/Blue
    cScaleLabel0: '#ffffff',
    cScaleInv0: '#ffffff',
    cScale1: '#0d9488', // Teal (clear & luminous, replaces dark muddiness)
    cScaleLabel1: '#ffffff',
    cScaleInv1: '#ffffff',
    cScale2: '#6366f1', // Indigo/Periwinkle
    cScaleLabel2: '#ffffff',
    cScaleInv2: '#ffffff',
    cScale3: '#8b5cf6', // Violet
    cScaleLabel3: '#ffffff',
    cScaleInv3: '#ffffff',
    cScale4: '#d97706', // Amber
    cScaleLabel4: '#ffffff',
    cScaleInv4: '#ffffff',
    cScale5: '#e11d48', // Rose
    cScaleLabel5: '#ffffff',
    cScaleInv5: '#ffffff',
    cScale6: '#059669', // Emerald
    cScaleLabel6: '#ffffff',
    cScaleInv6: '#ffffff',
    cScale7: '#2563eb', // Royal Blue
    cScaleLabel7: '#ffffff',
    cScaleInv7: '#ffffff',
    cScale8: '#0284c7',
    cScaleLabel8: '#ffffff',
    cScaleInv8: '#ffffff',
    cScale9: '#0d9488',
    cScaleLabel9: '#ffffff',
    cScaleInv9: '#ffffff',
    cScale10: '#6366f1',
    cScaleLabel10: '#ffffff',
    cScaleInv10: '#ffffff',
    cScale11: '#8b5cf6',
    cScaleLabel11: '#ffffff',
    cScaleInv11: '#ffffff',

    // Gantt / Task Colors
    sectionBkgColor: '#18181b',
    altSectionBkgColor: '#121215',
    sectionBkgColor2: '#1e293b',
    taskTextColor: '#ffffff',
    taskTextLightColor: '#ffffff',
    taskTextDarkColor: '#ffffff',
    taskTextOutsideColor: '#f4f4f5',
    taskTextClickableColor: '#38bdf8',
    activeTaskBkgColor: '#0284c7',
    activeTaskBorderColor: '#38bdf8',
    doneTaskBkgColor: '#059669',
    doneTaskBorderColor: '#34d399',
    critBkgColor: '#e11d48',
    critBorderColor: '#fb7185',
    todayLineColor: '#f43f5e',
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
