export default function ProgressRing({ value = 0, size = 80, strokeWidth = 7, color = '#7c5af2', label }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="rotate-[-90deg]">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="#f1f3f9" strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="progress-ring__circle"
        />
      </svg>
      <div className="text-center -mt-1">
        <p className="text-xl font-extrabold text-gray-900" style={{ marginTop: -(size / 2 + 12) }}>
          {/* layered on top of SVG via absolute – handled in parent */}
        </p>
      </div>
      {label && <p className="text-xs text-gray-500">{label}</p>}
    </div>
  )
}

export function ProgressRingWithValue({ value = 0, size = 100, strokeWidth = 8, color = '#7c5af2', label }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="relative inline-flex flex-col items-center">
      <svg width={size} height={size}>
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="#f1f3f9" strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="progress-ring__circle"
          style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
        />
        <text
          x="50%" y="50%"
          dominantBaseline="middle"
          textAnchor="middle"
          className="font-extrabold"
          fontSize={size * 0.22}
          fill="#111827"
          fontFamily="Inter, sans-serif"
          fontWeight="800"
        >
          {Math.round(value)}%
        </text>
      </svg>
      {label && <p className="text-xs text-gray-500 mt-1 text-center">{label}</p>}
    </div>
  )
}
