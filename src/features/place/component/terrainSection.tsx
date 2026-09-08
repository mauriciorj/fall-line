"use client";

import StatusBadge from "@/components/statusBadge";
import { useLanguage } from "@/src/i18n";
import TracksBreakdown from "@/components/tracksBreakdown";
import TrackStats from "@/utils/trackStats";
import { Resort } from "@/types/resort";

const TerrainSection = ({ resort }: { resort: Resort }) => {
  const { t } = useLanguage();
  const {
    totalTracks,
    greenTracks,
    greenTracksOpen,
    blueTracks,
    blueTracksOpen,
    blackTracks,
    blackTracksOpen,
    doubleBlackTracks,
    doubleBlackTracksOpen,
    freeStyleTracks,
    freeStyleTracksOpen,
  } = TrackStats({ resort });
  const trackPercentage = (count: number) =>
    totalTracks > 0 ? Math.round((count / totalTracks) * 100) : 0;

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("terrainBreakdown")}
      </h2>
      <div className="bg-card rounded-lg p-6 border border-border space-y-6">
        <TracksBreakdown resort={resort} isToHideStatusBadge={true} />

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 pt-4 border-t border-border">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-run-green" />
              <span className="text-sm text-muted-foreground">{t("green")}</span>
            </div>
            <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
              {resort.runs.green} {t("runs")}
              {Boolean(greenTracks > 0) && (
                <StatusBadge
                  className="ml-2"
                  open={greenTracksOpen}
                  total={greenTracks}
                  type="green"
                />
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {trackPercentage(resort.runs.green)}% {t("percentTerrain")}
            </p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-run-blue" />
              <span className="text-sm text-muted-foreground">{t("blue")}</span>
            </div>
            <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
              {resort.runs.blue} {t("runs")}
              {Boolean(blueTracks > 0) && (
                <StatusBadge
                  className="ml-2"
                  open={blueTracksOpen}
                  total={blueTracks}
                  type="blue"
                />
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {trackPercentage(resort.runs.blue)}% {t("percentTerrain")}
            </p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-run-black" />
              <span className="text-sm text-muted-foreground">{t("black")}</span>
            </div>
            <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
              {resort.runs.black} {t("runs")}
              {Boolean(blackTracks > 0) && (
                <StatusBadge
                  className="ml-2"
                  open={blackTracksOpen}
                  total={blackTracks}
                  type="black"
                />
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {trackPercentage(resort.runs.black)}% {t("percentTerrain")}
            </p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-run-double-black" />
              <span className="text-sm text-muted-foreground">
                {t("doubleBlack")}
              </span>
            </div>
            <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
              {resort.runs.doubleBlack} {t("runs")}
              {Boolean(doubleBlackTracks > 0) && (
                <StatusBadge
                  className="ml-2"
                  open={doubleBlackTracksOpen}
                  total={doubleBlackTracks}
                  type="double-black"
                />
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {trackPercentage(resort.runs.doubleBlack)}% {t("percentTerrain")}
            </p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-run-free-style" />
              <span className="text-sm text-muted-foreground">{t("freeStyle")}</span>
            </div>
            <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
              {resort.runs.freeStyle} {t("runs")}
              {Boolean(freeStyleTracks > 0) && (
                <StatusBadge
                  className="ml-2"
                  open={freeStyleTracksOpen}
                  total={freeStyleTracks}
                  type="free-style"
                />
              )}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              {trackPercentage(resort.runs.freeStyle || 0)}% {t("percentTerrain")}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TerrainSection;
