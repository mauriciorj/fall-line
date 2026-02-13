import { cn } from "@/utils/utils";

interface RunBreakdownProps {
  black: number;
  blue: number;
  className?: string;
  doubleBlack?: number;
  freeStyle?: number;
  green: number;
  name: string;
  trackConditions?: {
    name: string;
    condition: string;
    difficulty: "black" | "blue" | "double-black" | "free-style" | "green";
  }[];
}

export function RunBreakdown({
  black,
  blue,
  className,
  doubleBlack,
  freeStyle,
  green,
  name,
  trackConditions,
}: RunBreakdownProps) {
  const total = green + blue + black + (doubleBlack || 0) + (freeStyle || 0);
  const greenPercent = (green / total) * 100;
  const bluePercent = (blue / total) * 100;
  const blackPercent = (black / total) * 100;
  const doubleBlackPercent = ((doubleBlack || 0) / total) * 100;
  const freeStylePercent = ((freeStyle || 0) / total) * 100;

  // const greenTracks = trackConditions
  //   ? trackConditions.filter((item) => item.difficulty === "green")?.length
  //   : 0;
  // const blueTracks = trackConditions
  //   ? trackConditions.filter((item) => item.difficulty === "blue")?.length
  //   : 0;
  // const blackTracks = trackConditions
  //   ? trackConditions.filter((item) => item.difficulty === "black")?.length
  //   : 0;
  // const doubleBlackTracks = trackConditions
  //   ? trackConditions.filter((item) => item.difficulty === "double-black")
  //       ?.length
  //   : 0;
  // const freeStyleTracks = trackConditions
  //   ? trackConditions.map((item) => item.difficulty === "free-style")?.length
  //   : 0;

  // console.log("");
  // console.log(name);
  // console.log(
  //   `{ black: ${blackTracks}, blue: ${blueTracks}, doubleBlack: ${doubleBlackTracks}, freeStyle: ${freeStyleTracks}, green: ${greenTracks} }`
  // );

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
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-run-double-black" />
            <span className="w-3 h-3 rounded-full bg-run-double-black" />
            {doubleBlack}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-run-free-style" />
            {freeStyle}
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
        <div
          className="h-full bg-run-double-black transition-all duration-300"
          style={{ width: `${doubleBlackPercent}%` }}
        />
        <div
          className="h-full bg-run-free-style transition-all duration-300"
          style={{ width: `${freeStylePercent}%` }}
        />
      </div>
    </div>
  );
}
