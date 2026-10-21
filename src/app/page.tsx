import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import HomeView from "@/src/features/home/components/homeView";
import { findDefaultLocation } from "@/types/location";
import { Resort } from "@/types/resort";
import { toResort } from "@/utils/convexResort";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

export default async function HomePage() {
  const locations = await fetchQuery(api.locations.list);
  const defaultLocation = findDefaultLocation(locations);
  const dbResorts = defaultLocation
    ? await fetchQuery(api.resorts.list, defaultLocation)
    : [];
  const initialResorts = dbResorts
    .map((resort) => toResort(resort))
    .filter((resort): resort is Resort => resort !== null);

  return <HomeView initialResorts={initialResorts} />;
}
