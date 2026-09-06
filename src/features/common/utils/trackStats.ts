import { Resort } from "@/types/resort";

const TrackStats = ({ resort }: { resort: Resort }) => {
  const {
    trackConditions,
    runs: { black, blue, doubleBlack, freeStyle, green },
  } = resort;

  const totalTracks =
    green + blue + black + (doubleBlack || 0) + (freeStyle || 0);

  const percentage = (count: number) =>
    totalTracks > 0 ? (count / totalTracks) * 100 : 0;
  const greenTracksPercent = percentage(green);
  const blueTracksPercent = percentage(blue);
  const blackTracksPercent = percentage(black);
  const doubleBlackTracksPercent = percentage(doubleBlack || 0);
  const freeStyleTracksPercent = percentage(freeStyle || 0);

  const greenTracks = trackConditions
    ? trackConditions.filter((item) => item.difficulty === "green")?.length
    : 0;
  const greenTracksOpen = trackConditions
    ? trackConditions.filter(
        (item) => item.difficulty === "green" && item.condition === "open"
      )?.length
    : 0;

  const blueTracks = trackConditions
    ? trackConditions.filter((item) => item.difficulty === "blue")?.length
    : 0;
  const blueTracksOpen = trackConditions
    ? trackConditions.filter(
        (item) => item.difficulty === "blue" && item.condition === "open"
      )?.length
    : 0;

  const blackTracks = trackConditions
    ? trackConditions.filter((item) => item.difficulty === "black")?.length
    : 0;
  const blackTracksOpen = trackConditions
    ? trackConditions.filter(
        (item) => item.difficulty === "black" && item.condition === "open"
      )?.length
    : 0;

  const doubleBlackTracks = trackConditions
    ? trackConditions.filter((item) => item.difficulty === "double-black")
        ?.length
    : 0;
  const doubleBlackTracksOpen = trackConditions
    ? trackConditions.filter(
        (item) =>
          item.difficulty === "double-black" && item.condition === "open"
      )?.length
    : 0;

  const freeStyleTracks = trackConditions
    ? trackConditions.filter((item) => item.difficulty === "free-style")?.length
    : 0;
  const freeStyleTracksOpen = trackConditions
    ? trackConditions.filter(
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
