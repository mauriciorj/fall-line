import { notFound, permanentRedirect } from "next/navigation";
import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { getResortLocationPath } from "@/utils/convexResort";
import { listPublishedResorts } from "@/utils/publishedResorts";

// Legacy URLs (/place/<resortId>): cached 308 to the canonical location path.
export const dynamic = "force-static";
export const revalidate = 3600;

export async function generateStaticParams(): Promise<{ id: string[] }[]> {
  const resorts = await listPublishedResorts();
  return resorts.map((resort) => ({ id: [resort.resortId] }));
}

export default async function LegacyPlaceRedirect({
  params,
}: {
  params: Promise<{ id: string[] }>;
}) {
  const { id } = await params;
  const resortId = id.at(-1);
  const resort = resortId
    ? await fetchQuery(api.resorts.getByResortId, { resortId })
    : null;

  if (!resort) {
    notFound();
  }

  permanentRedirect(
    getResortLocationPath(resort.resortId, resort.country, resort.region),
  );
}
