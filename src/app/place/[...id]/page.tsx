"use client";

import Image from "next/image";
import { useRouter, useParams } from "next/navigation";
import { resorts } from "@/data/resorts";
import { RunBreakdown } from "@/components/runBreakdown";
import {
  ArrowLeft,
  CircleDot,
  GraduationCap,
  MapPin,
  Mountain,
  Ticket,
  CableCar,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ResortInfoSection } from "@/place/component/resortInfoSection";
import { TracksSection } from "@/place/component/tracksSection";
import StatusBadge from "@/components/statusBadge";

import skiIcon from "@/icons/ski-svgrepo-com.svg";
import snowboardIcon from "@/icons/snowboard-1-svgrepo-com.svg";
import tubbingIcon from "@/icons/buoy-svgrepo-com.svg";

const ResortDetail = () => {
  const { id } = useParams();
  const router = useRouter();

  const resort = resorts.find((r) => r.id === id?.[0]);

  if (!resort) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-serif text-foreground">
            Resort not found
          </h1>
          <Button variant="ghost" onClick={() => router.push("/")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to all resorts
          </Button>
        </div>
      </div>
    );
  }

  const { green, blue, black, doubleBlack, freeStyle } = resort.runs;

  const totalRuns =
    green + blue + black + (doubleBlack || 0) + (freeStyle || 0);

  const greenTracks = resort.trackConditions
    ? resort.trackConditions.filter((item) => item.difficulty === "green")
        ?.length
    : 0;
  const greenTracksOpen = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) => item.difficulty === "green" && item.condition === "open"
      )?.length
    : 0;

  const blueTracks = resort.trackConditions
    ? resort.trackConditions.filter((item) => item.difficulty === "blue")
        ?.length
    : 0;
  const blueTracksOpen = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) => item.difficulty === "blue" && item.condition === "open"
      )?.length
    : 0;

  const blackTracks = resort.trackConditions
    ? resort.trackConditions.filter((item) => item.difficulty === "black")
        ?.length
    : 0;
  const blackTracksOpen = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) => item.difficulty === "black" && item.condition === "open"
      )?.length
    : 0;

  const doubleBlackTracks = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) => item.difficulty === "double-black"
      )?.length
    : 0;
  const doubleBlackTracksOpen = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) =>
          item.difficulty === "double-black" && item.condition === "open"
      )?.length
    : 0;

  const freeStyleTracks = resort.trackConditions
    ? resort.trackConditions.filter((item) => item.difficulty === "free-style")
        ?.length
    : 0;
  const freeStyleTracksOpen = resort.trackConditions
    ? resort.trackConditions.filter(
        (item) => item.difficulty === "free-style" && item.condition === "open"
      )?.length
    : 0;

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Image */}
      <div className="relative h-[40vh] md:h-[50vh] overflow-hidden">
        <Image
          src={resort.image}
          alt={resort.name}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/20 to-transparent" />
        <div className="absolute bottom-10 left-0 right-0 p-6 md:p-10">
          <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-medium text-foreground">
            {resort.name}
          </h1>
          {/* <div className="flex items-center gap-2 mt-3 text-muted-foreground">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{resort.distance} km from Toronto</span>
          </div> */}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-4xl mx-auto mb-20 px-6 py-10 space-y-10">
        {/* Buy Tickets CTA - Sticky on mobile */}
        {resort?.ticketUrl && (
          <div className="sticky top-16 z-30 bg-background/95 backdrop-blur-sm px-6 py-3">
            <a
              href={resort.ticketUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <Button
                className="w-full h-12 text-base font-semibold shadow-lg"
                size="lg"
              >
                <Ticket className="w-5 h-5 mr-2" />
                Buy Tickets — from ${resort.dayTicketPrice}
              </Button>
            </a>
          </div>
        )}
        {/* Quick Stats */}
        {/* <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex flex-col justify-between bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <CableCar className="w-3.5 h-3.5" />
              <span className="text-xs uppercase tracking-wide">Lift Pass</span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
          <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Image alt="ski-icons" src={skiIcon} width={16} height={16} />
              <span className="text-xs uppercase tracking-wide">
                Ski Rental
              </span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
          <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Image
                alt="ski-icons"
                src={snowboardIcon}
                width={14}
                height={14}
              />
              <span className="text-xs uppercase tracking-wide">
                Snowboard Rental
              </span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              ${resort.snowBoardRentalPrice}
            </p>
          </div>
          {Boolean(resort?.tubbingPrice && resort?.tubbingPrice > 0) && (
            <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
              <div className="flex items-center gap-2 text-muted-foreground mb-2">
                <Image
                  alt="ski-icons"
                  src={tubbingIcon}
                  width={14}
                  height={14}
                />
                <span className="text-xs uppercase tracking-wide">Tubbing</span>
              </div>
              <p className="text-2xl font-medium text-foreground">
                ${resort.tubbingPrice}
              </p>
            </div>
          )}
          <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Mountain className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wide">
                Total Runs
              </span>
            </div>
            <p className="text-2xl font-medium text-foreground">{totalRuns}</p>
          </div>
        </section> */}

        {/* Main Info */}
        <ResortInfoSection resort={resort} />

        {/* Tracks */}
        <TracksSection resort={resort} />

        {/* Terrain Breakdown */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Terrain Breakdown
          </h2>
          <div className="bg-card rounded-lg p-6 border border-border space-y-6">
            <RunBreakdown
              black={resort.runs.black}
              blue={resort.runs.blue}
              doubleBlack={resort.runs.doubleBlack}
              freeStyle={resort.runs.freeStyle}
              green={resort.runs.green}
              name={resort.name}
              trackConditions={resort.trackConditions}
              isToHideStatusBadge={true}
            />

            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-green" />
                  <span className="text-sm text-muted-foreground">Green</span>
                </div>
                <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
                  {resort.runs.green} runs
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
                  {Math.round((resort.runs.green / totalRuns) * 100)}% of
                  terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-blue" />
                  <span className="text-sm text-muted-foreground">Blue</span>
                </div>
                <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
                  {resort.runs.blue} runs
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
                  {Math.round((resort.runs.blue / totalRuns) * 100)}% of terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-black" />
                  <span className="text-sm text-muted-foreground">Black</span>
                </div>
                <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
                  {resort.runs.black} runs
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
                  {Math.round((resort.runs.black / totalRuns) * 100)}% of
                  terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-double-black" />
                  <span className="text-sm text-muted-foreground">
                    Double Black
                  </span>
                </div>
                <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
                  {resort.runs.doubleBlack} runs
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
                  {Math.round((resort.runs.doubleBlack / totalRuns) * 100)}% of
                  terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-free-style" />
                  <span className="text-sm text-muted-foreground">
                    Free Style
                  </span>
                </div>
                <p className="flex flex-row items-center justify-center text-xl font-medium text-foreground">
                  {resort.runs.freeStyle} runs
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
                  {resort.runs.freeStyle
                    ? Math.round((resort.runs.freeStyle / totalRuns) * 100)
                    : 0}
                  % of terrain
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Details */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Pricing
          </h2>
          <div className="bg-card rounded-lg border border-border divide-y divide-border">
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-medium text-foreground">Lift Pass</p>
                {/* <p className="text-sm text-muted-foreground">
                  Lift access
                </p> */}
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.dayTicketPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-medium text-foreground">Ski Rental</p>
                {/* <p className="text-sm text-muted-foreground">Skis with boots</p> */}
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.skiRentalPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-medium text-foreground">Snowboard Rental</p>
                {/* <p className="text-sm text-muted-foreground">
                  Snowboard with boots
                </p> */}
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.snowBoardRentalPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5">
              <div className="flex items-center gap-2">
                <GraduationCap className="w-4 h-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Lessons</p>
                  {/* <p className="text-sm text-muted-foreground">
                    Group lesson (2 hours)
                  </p> */}
                </div>
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.lessonsPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5">
              <div className="flex items-center gap-2">
                <CircleDot className="w-4 h-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Tubing</p>
                  {/* <p className="text-sm text-muted-foreground">
                    Full day snow tubing pass
                  </p> */}
                </div>
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort?.tubbingPrice}
              </p>
            </div>
          </div>
        </section>

        {/* Location */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Location
          </h2>
          <div className="bg-card rounded-lg p-6 border border-border">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-full bg-primary/10">
                <MapPin className="w-5 h-5 text-primary" />
              </div>
              <div className="space-y-1">
                {/* <p className="font-medium text-foreground">
                  {resort.distance} km from Toronto
                </p> */}
                <p className="font-medium text-foreground">
                  Address: {resort.address}
                </p>
                <a
                  href={resort.googleMapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-2"
                >
                  Get directions
                  <ArrowLeft className="w-3 h-3 rotate-[135deg]" />
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Bottom CTA */}
        {/* <section className="pb-6">
          <a
            href={resort.ticketUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block"
          >
            <Button
              className="w-full h-14 text-lg font-semibold shadow-lg"
              size="lg"
            >
              <Ticket className="w-5 h-5 mr-2" />
              Buy Tickets
            </Button>
          </a>
        </section> */}
      </main>
    </div>
  );
};

export default ResortDetail;
