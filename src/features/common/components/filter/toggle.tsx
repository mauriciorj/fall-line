"use client";

import { cn } from "@/utils/utils";

interface DifficultyToggleProps {
  label: string;
  color: "green" | "blue" | "black";
  isActive: boolean;
  onClick: () => void;
}

function Toggle({ label, color, isActive, onClick }: DifficultyToggleProps) {
  const colorClasses = {
    green: {
      dot: "bg-run-green",
      active: "ring-run-green/30 bg-run-green/10",
    },
    blue: {
      dot: "bg-run-blue",
      active: "ring-run-blue/30 bg-run-blue/10",
    },
    black: {
      dot: "bg-run-black",
      active: "ring-run-black/20 bg-run-black/5",
    },
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm",
        isActive
          ? `${colorClasses[color].active} ring-1 text-foreground`
          : "bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/50"
      )}
    >
      {/* <span className={cn("w-2 h-2 rounded-full", colorClasses[color].dot)} /> */}
      {label}
    </button>
  );
}

export default Toggle;
