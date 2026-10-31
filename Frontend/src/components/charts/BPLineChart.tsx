import { Activity } from 'lucide-react';
import React, { useState } from 'react';

interface DataPoint {
  label: string;
  systolic: number;
  diastolic: number;
  isManual?: boolean;
  tooltipText?: string;
  isHighlighted?: boolean;
}

interface BPLineChartProps {
  data?: DataPoint[];
  showTargetZone?: boolean;
  targetMin?: number;
  targetMax?: number;
  height?: number;
  showLegend?: boolean;
  variant?: 'doctor' | 'patient';
}

export const BPLineChart: React.FC<BPLineChartProps> = ({
  data = [],
  showTargetZone = false,
  targetMin = 115,
  targetMax = 130,
  height = 200,
  showLegend = true,
  variant = 'doctor'
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(
    data && data.length > 0 ? (data.findIndex(d => d.isHighlighted) !== -1 ? data.findIndex(d => d.isHighlighted) : null) : null
  );

  if (!data || data.length === 0) {
    return (
      <div className="w-full h-44 flex flex-col items-center justify-center text-slate-400 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
        <Activity className="w-6 h-6 mb-2 text-slate-300" />
        <p className="text-xs font-medium">No blood pressure readings recorded yet for this period.</p>
      </div>
    );
  }

  const minY = 60;
  const maxY = 180;
  const yRange = maxY - minY;

  // Chart coordinates calculation
  const paddingX = 45;
  const paddingY = 25;
  const width = 650;
  const graphWidth = width - paddingX * 2;
  const graphHeight = height - paddingY * 2;

  const getY = (val: number) => {
    return paddingY + graphHeight - ((val - minY) / yRange) * graphHeight;
  };

  const getX = (index: number) => {
    if (data.length <= 1) return paddingX + graphWidth / 2;
    return paddingX + (index / (data.length - 1)) * graphWidth;
  };

  // Generate SVG path strings
  const systolicPoints = data.map((d, i) => `${getX(i)},${getY(d.systolic)}`).join(' ');
  const diastolicPoints = data.map((d, i) => `${getX(i)},${getY(d.diastolic)}`).join(' ');

  // Target zone coordinates
  const targetTopY = getY(targetMax);
  const targetBottomY = getY(targetMin);

  return (
    <div className="w-full relative select-none">
      {/* Legend */}
      {showLegend && (
        <div className="flex items-center justify-end gap-6 text-xs text-slate-500 mb-3">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-0.5 bg-[#0d6269] rounded-full inline-block"></span>
            <span className="font-medium text-slate-700">Systolic</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-0.5 bg-[#5b9a9d] rounded-full inline-block"></span>
            <span className="font-medium text-slate-700">Diastolic</span>
          </div>
        </div>
      )}

      <div className="relative w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto overflow-visible"
        >
          {/* Target Zone Shading if enabled */}
          {showTargetZone && (
            <rect
              x={paddingX}
              y={targetTopY}
              width={graphWidth}
              height={targetBottomY - targetTopY}
              fill="#e6f5f3"
              rx={4}
            />
          )}

          {/* Target Zone Label */}
          {showTargetZone && (
            <text
              x={paddingX + graphWidth - 8}
              y={targetTopY + (targetBottomY - targetTopY) / 2 + 4}
              textAnchor="end"
              className="text-[10px] fill-[#0d6269] font-medium"
            >
              Target range: {targetMin}–{targetMax} mmHg
            </text>
          )}

          {/* Horizontal Grid lines */}
          {[180, 140, 100, 60].map((val) => {
            const y = getY(val);
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - paddingX}
                  y2={y}
                  stroke="#e2e8f0"
                  strokeWidth="1"
                  strokeDasharray={val === 140 || val === 100 ? '2 2' : 'none'}
                />
                <text
                  x={paddingX - 12}
                  y={y + 4}
                  textAnchor="end"
                  className="text-[11px] fill-slate-400 font-sans"
                >
                  {val}
                </text>
              </g>
            );
          })}

          {/* Diastolic Line */}
          <polyline
            fill="none"
            stroke="#659d9f"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={diastolicPoints}
            strokeDasharray={variant === 'patient' ? '4 3' : 'none'}
          />

          {/* Systolic Line */}
          <polyline
            fill="none"
            stroke="#0d6269"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={systolicPoints}
          />

          {/* Data Points */}
          {data.map((d, i) => {
            const sysX = getX(i);
            const sysY = getY(d.systolic);
            const diaX = getX(i);
            const diaY = getY(d.diastolic);
            const isHovered = hoveredIndex === i;

            return (
              <g key={i} className="cursor-pointer" onMouseEnter={() => setHoveredIndex(i)}>
                {/* Systolic Point */}
                <circle
                  cx={sysX}
                  cy={sysY}
                  r={isHovered ? 6 : 4}
                  fill={d.isManual ? '#ffffff' : '#0d6269'}
                  stroke="#0d6269"
                  strokeWidth={d.isManual ? 2.5 : 1}
                  className="transition-all duration-150"
                />

                {/* Diastolic Point */}
                <circle
                  cx={diaX}
                  cy={diaY}
                  r={isHovered ? 5 : 3.5}
                  fill={d.isManual ? '#ffffff' : '#659d9f'}
                  stroke="#659d9f"
                  strokeWidth={d.isManual ? 2 : 1}
                  className="transition-all duration-150"
                />

                {/* Vertical hover guide */}
                {isHovered && (
                  <line
                    x1={sysX}
                    y1={paddingY}
                    x2={sysX}
                    y2={height - paddingY}
                    stroke="#94a3b8"
                    strokeWidth="1"
                    strokeDasharray="2 2"
                  />
                )}
              </g>
            );
          })}

          {/* X Axis Labels */}
          {data.map((d, i) => {
            const x = getX(i);
            return (
              <text
                key={i}
                x={x}
                y={height - 5}
                textAnchor="middle"
                className="text-[11px] fill-slate-500 font-sans"
              >
                {d.label}
              </text>
            );
          })}

          {/* Hover Tooltip / Badge */}
          {hoveredIndex !== null && data[hoveredIndex] && (
            <g
              transform={`translate(${getX(hoveredIndex)}, ${Math.max(
                16,
                getY(data[hoveredIndex].systolic) - 22
              )})`}
              className="pointer-events-none transition-all duration-150"
            >
              <rect
                x="-46"
                y="-14"
                width="92"
                height="22"
                rx="6"
                fill="#fee2e2"
                stroke="#fca5a5"
                strokeWidth="1"
              />
              <text
                x="0"
                y="1"
                textAnchor="middle"
                className="text-[10px] font-bold fill-[#991b1b]"
              >
                {data[hoveredIndex].tooltipText ||
                  `${data[hoveredIndex].systolic}/${data[hoveredIndex].diastolic}`}
              </text>
            </g>
          )}
        </svg>
      </div>
    </div>
  );
};
