import { cn } from "@/utils/utils";
import StatusBadge from "@/components/statusBadge";
import { Resort } from "@/types/resort";
import TrackStats from "@/utils/trackStats";

const TracksBreakdown = ({
  className,
  isToHideStatusBadge = false,
  resort,
}: {
  className?: string;
  isToHideStatusBadge?: boolean;
  resort: Resort;
}) => {
  const {
    totalTracks,
    greenTracks,
    greenTracksOpen,
    greenTracksPercent,
    blueTracks,
    blueTracksOpen,
    blueTracksPercent,
    blackTracks,
    blackTracksOpen,
    blackTracksPercent,
    doubleBlackTracks,
    doubleBlackTracksOpen,
    doubleBlackTracksPercent,
    freeStyleTracks,
    freeStyleTracksOpen,
    freeStyleTracksPercent,
  } = TrackStats({ resort });

  // console.log("");
  // console.log(name);
  // console.log(
  //   `{ black: ${blackTracks}, blue: ${blueTracks}, doubleBlack: ${doubleBlackTracks}, freeStyle: ${freeStyleTracks}, green: ${greenTracks} }`
  // );

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center gap-3">
        <div>
          <p className="text-xs text-muted-foreground">Tracks:</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          {Boolean(greenTracks > 0) && (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-run-green" />
              {greenTracks}
            </span>
          )}
          {Boolean(blueTracks > 0) && (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-run-blue" />
              {blueTracks}
            </span>
          )}
          {Boolean(blackTracks > 0) && (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-run-black" />
              {blackTracks}
            </span>
          )}
          {Boolean(doubleBlackTracks && doubleBlackTracks > 0) && (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-run-double-black" />
              <span className="w-3 h-3 rounded-full bg-run-double-black" />
              {doubleBlackTracks}
            </span>
          )}
          {Boolean(freeStyleTracks && freeStyleTracks > 0) && (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-run-free-style" />
              {freeStyleTracks}
            </span>
          )}
        </div>
      </div>
      <div className="h-2.5 w-full flex rounded-full overflow-hidden bg-muted">
        {Boolean(greenTracks > 0) && (
          <div
            className="h-full bg-run-green transition-all duration-300"
            style={{ width: `${greenTracksPercent}%` }}
          />
        )}
        {Boolean(blueTracksPercent > 0) && (
          <div
            className="h-full bg-run-blue transition-all duration-300"
            style={{ width: `${blueTracksPercent}%` }}
          />
        )}
        {Boolean(blackTracksPercent > 0) && (
          <div
            className="h-full bg-run-black transition-all duration-300"
            style={{ width: `${blackTracksPercent}%` }}
          />
        )}
        {Boolean(doubleBlackTracksPercent > 0) && (
          <div
            className="h-full bg-run-double-black transition-all duration-300"
            style={{ width: `${doubleBlackTracksPercent}%` }}
          />
        )}
        {Boolean(freeStyleTracksPercent > 0) && (
          <div
            className="h-full bg-run-free-style transition-all duration-300"
            style={{ width: `${freeStyleTracksPercent}%` }}
          />
        )}
      </div>
      {!isToHideStatusBadge && (
        <div className="flex items-center text-xs text-muted-foreground">
          {Boolean(greenTracks > 0) && (
            <StatusBadge
              className="mr-2"
              open={greenTracksOpen}
              total={greenTracks}
              type="green"
            />
          )}
          {Boolean(blueTracks > 0) && (
            <StatusBadge
              className="mr-2"
              open={blueTracksOpen}
              total={blueTracks}
              type="blue"
            />
          )}
          {Boolean(blackTracks > 0) && (
            <StatusBadge
              className="mr-2"
              open={blackTracksOpen}
              total={blackTracks}
              type="black"
            />
          )}
          {Boolean(doubleBlackTracks > 0) && (
            <StatusBadge
              className="mr-2"
              open={doubleBlackTracksOpen}
              total={doubleBlackTracks}
              type="double-black"
            />
          )}
          {Boolean(freeStyleTracks > 0) && (
            <StatusBadge
              open={freeStyleTracksOpen}
              total={freeStyleTracks}
              type="free-style"
            />
          )}
        </div>
      )}
    </div>
  );
};
export default TracksBreakdown;
