type Point = {
  label: string;
  value: number | null;
};

type Props = {
  title: string;
  points: Point[];
  colorClassName: "line-primary" | "line-secondary";
  valueFormatter?: (value: number) => string;
};

export function SimpleLineChart({ title, points, colorClassName, valueFormatter }: Props) {
  const validPoints = points
    .map((point, index) => ({ ...point, index }))
    .filter((point) => point.value !== null) as Array<Point & { value: number; index: number }>;

  const min = validPoints.length > 0 ? Math.min(...validPoints.map((point) => point.value)) : 0;
  const max = validPoints.length > 0 ? Math.max(...validPoints.map((point) => point.value)) : 1;
  const spread = max - min || 1;

  const width = 480;
  const height = 200;
  const chartPath = validPoints
    .map((point, idx) => {
      const x = validPoints.length > 1 ? (point.index / (points.length - 1)) * width : width / 2;
      const y = height - ((point.value - min) / spread) * height;
      return `${idx === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");

  return (
    <section className="chart-card">
      <h3>{title}</h3>
      {validPoints.length === 0 ? (
        <p className="muted">No sufficient data points for chart rendering.</p>
      ) : (
        <>
          <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
            <path d={chartPath} className={colorClassName} />
          </svg>
          <div className="chart-footnote">
            <span>{points[0]?.label}</span>
            <span>
              Latest: {valueFormatter ? valueFormatter(validPoints[validPoints.length - 1].value) : validPoints[validPoints.length - 1].value.toFixed(2)}
            </span>
            <span>{points[points.length - 1]?.label}</span>
          </div>
        </>
      )}
    </section>
  );
}
