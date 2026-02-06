import { cn } from "@/utils/utils";

interface RunBreakdownProps {
  green: number;
  blue: number;
  black: number;
  className?: string;
}

export function RunBreakdown({
  green,
  blue,
  black,
  className,
}: RunBreakdownProps) {
  const total = green + blue + black;
  const greenPercent = (green / total) * 100;
  const bluePercent = (blue / total) * 100;
  const blackPercent = (black / total) * 100;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center gap-3">
        <div>
          <p className="text-xs text-muted-foreground">Tracks</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-run-green" />
            {green}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-run-blue" />
            {blue}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-run-black" />
            {black}
          </span>
        </div>
      </div>
      <div className="h-2.5 w-full flex rounded-full overflow-hidden bg-muted">
        <div
          className="h-full bg-run-green transition-all duration-300"
          style={{ width: `${greenPercent}%` }}
        />
        <div
          className="h-full bg-run-blue transition-all duration-300"
          style={{ width: `${bluePercent}%` }}
        />
        <div
          className="h-full bg-run-black transition-all duration-300"
          style={{ width: `${blackPercent}%` }}
        />
      </div>
    </div>
  );
}
