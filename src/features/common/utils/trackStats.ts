import { Resort } from "@/types/resort";

const TrackStats = ({ resort }: { resort: Resort }) => {
  const {
    trackConditions,
    runs: { black, blue, doubleBlack, freeStyle, green },
  } = resort;
  const conditions = trackConditions ?? [];
  const hasTrackConditions = conditions.length > 0;

  const totalTracks =
    green + blue + black + (doubleBlack || 0) + (freeStyle || 0);

  const percentage = (count: number) =>
    totalTracks > 0 ? (count / totalTracks) * 100 : 0;
  const greenTracksPercent = percentage(green);
  const blueTracksPercent = percentage(blue);
  const blackTracksPercent = percentage(black);
  const doubleBlackTracksPercent = percentage(doubleBlack || 0);
  const freeStyleTracksPercent = percentage(freeStyle || 0);

  const greenTracks = hasTrackConditions
    ? conditions.filter((item) => item.difficulty === "green")?.length
    : green;
  const greenTracksOpen = hasTrackConditions
    ? conditions.filter(
        (item) => item.difficulty === "green" && item.condition === "open"
      )?.length
    : 0;

  const blueTracks = hasTrackConditions
    ? conditions.filter((item) => item.difficulty === "blue")?.length
    : blue;
  const blueTracksOpen = hasTrackConditions
    ? conditions.filter(
        (item) => item.difficulty === "blue" && item.condition === "open"
      )?.length
    : 0;

  const blackTracks = hasTrackConditions
    ? conditions.filter((item) => item.difficulty === "black")?.length
    : black;
  const blackTracksOpen = hasTrackConditions
    ? conditions.filter(
        (item) => item.difficulty === "black" && item.condition === "open"
      )?.length
    : 0;

  const doubleBlackTracks = hasTrackConditions
    ? conditions.filter((item) => item.difficulty === "double-black")
        ?.length
    : doubleBlack || 0;
  const doubleBlackTracksOpen = hasTrackConditions
    ? conditions.filter(
        (item) =>
          item.difficulty === "double-black" && item.condition === "open"
      )?.length
    : 0;

  const freeStyleTracks = hasTrackConditions
    ? conditions.filter((item) => item.difficulty === "free-style")?.length
    : freeStyle || 0;
  const freeStyleTracksOpen = hasTrackConditions
    ? conditions.filter(
        (item) => item.difficulty === "free-style" && item.condition === "open"
      )?.length
    : 0;

  return {
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
  };
};

export default TrackStats;
