"use client";

import { cn } from "@/utils/utils";
import { useLanguage } from "@/src/i18n";

interface TrackStatus {
  className?: string;
  open: number;
  total: number;
  type: "green" | "blue" | "black" | "double-black" | "free-style";
}

const StatusBadge = ({ open, total, type, className }: TrackStatus) => {
  const { t } = useLanguage();

  return (
    <span
      className={cn(
        "text-[11px] font-medium px-1.5 pb-0.5 pt-1 rounded-full",
        className,
        type === "green" && "border border-run-green text-run-green",
        type === "blue" && "border border-run-blue text-run-blue",
        type === "black" && "border border-run-black text-run-black",
        type === "double-black" &&
          "border border-run-double-black text-run-double-black",
        type === "free-style" &&
          "border border-run-free-style text-run-free-style"
      )}
    >
      {open}/{total} {t("open")}
    </span>
  );
};

export default StatusBadge;
