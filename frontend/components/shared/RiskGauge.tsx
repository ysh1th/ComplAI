"use client";

import { motion } from "framer-motion";
import { getRiskColor } from "@/lib/utils";
import type { RiskBand } from "@/lib/types";

interface RiskGaugeProps {
  score: number;
  band: RiskBand;
  size?: number;
}

export function RiskGauge({ score, band, size = 180 }: RiskGaugeProps) {
  const color = getRiskColor(band);
  const radius = (size - 20) / 2;
  const circumference = Math.PI * radius;
  const progress = (score / 100) * circumference;
  const cx = size / 2;
  const cy = size / 2 + 10;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size / 2 + 30} viewBox={`0 0 ${size} ${size / 2 + 30}`}>
        {/* Background arc */}
        <path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke="#2A2A2A"
          strokeWidth="8"
          strokeLinecap="round"
        />
        {/* Progress arc */}
        <motion.path
          d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: circumference - progress }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
        {/* Score text */}
        <text
          x={cx}
          y={cy - radius / 3}
          textAnchor="middle"
          fill={color}
          fontSize={size / 4}
          fontWeight="800"
          fontFamily="Inter, sans-serif"
        >
          {score}
        </text>
        <text
          x={cx}
          y={cy - radius / 3 + 18}
          textAnchor="middle"
          fill="#6B7280"
          fontSize="13"
          fontFamily="Inter, sans-serif"
        >
          / 100
        </text>
      </svg>
      <span
        className="text-sm font-bold mt-[-4px]"
        style={{ color }}
      >
        {band} RISK
      </span>
    </div>
  );
}
