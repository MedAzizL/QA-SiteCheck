type Props = {
  value: number; // 0-100
  size?: number;
  stroke?: number;
  ringColor?: string; // hex
};

export function CircleScore({
  value,
  size = 140,
  stroke = 12,
  ringColor = "#3b82f6",
}: Props) {
  const clamped = Math.max(0, Math.min(100, value));
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = (clamped / 100) * c;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke="#e5e7eb"
          strokeWidth={stroke}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={ringColor}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c - dash}`}
          fill="transparent"
        />
      </svg>

      <div className="absolute inset-0 grid place-items-center">
        <div className="text-center">
          <div className="text-3xl font-bold tabular-nums text-gray-900">{clamped}</div>
          <div className="text-xs text-gray-500 -mt-0.5">/100</div>
        </div>
      </div>
    </div>
  );
}