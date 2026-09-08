import { internalMutation, query } from "./_generated/server";
import type { MutationCtx } from "./_generated/server";
import type { Doc } from "./_generated/dataModel";
import { v } from "convex/values";
import { resortSeedData } from "./resortSeed";

const locationFields = v.object({
  continent: v.optional(v.string()),
  country: v.optional(v.string()),
  region: v.optional(v.string()),
});

const resortFieldNames = [
  "resortId",
  "name",
  "continent",
  "country",
  "region",
  "contact",
  "website",
  "address",
  "coordinates",
  "dayTicketPrice",
  "email",
  "googleMapsUrl",
  "hasAccommodations",
  "hasCrossCountry",
  "hasLessons",
  "hasSnowshoeing",
  "hasSpa",
  "hasTubing",
  "hasZipline",
  "image",
  "lessonsPrice",
  "phone",
  "rating",
  "skiRentalPrice",
  "snowBoardRentalPrice",
  "runs",
  "ticketUrl",
  "tollFree",
  "trackConditions",
  "trailMap",
  "tubbingPrice",
] as const;

type ResortDocument = Omit<Doc<"resorts">, "_id" | "_creationTime">;

function selectResortFields(
  input: Record<string, unknown>,
  resortId: string,
): ResortDocument {
  return {
    ...Object.fromEntries(
      resortFieldNames
        .filter((fieldName) => input[fieldName] !== undefined)
        .map((fieldName) => [fieldName, input[fieldName]]),
    ),
    resortId,
  } as ResortDocument;
}

export async function ensureResort(
  ctx: MutationCtx,
  identity: { resortId: string; website?: string },
) {
  const existing = await ctx.db
    .query("resorts")
    .withIndex("by_resort_id", (q) => q.eq("resortId", identity.resortId))
    .unique();

  if (existing) {
    if (!existing.website && identity.website) {
      await ctx.db.patch(existing._id, { website: identity.website });
    }
    return existing._id;
  }

  const seededResort = resortSeedData.find(
    (resort) => resort.resortId === identity.resortId,
  );
  if (seededResort) {
    return await ctx.db.insert("resorts", seededResort);
  }

  return await ctx.db.insert("resorts", {
    resortId: identity.resortId,
    ...(identity.website ? { website: identity.website } : {}),
  });
}

export const list = query({
  args: {
    continent: v.string(),
    country: v.string(),
    region: v.string(),
  },
  returns: v.array(v.any()),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resorts")
      .withIndex("by_location", (q) =>
        q
          .eq("continent", args.continent)
          .eq("country", args.country)
          .eq("region", args.region),
      )
      .collect();
  },
});

export const listLocations = query({
  args: {},
  returns: v.array(locationFields),
  handler: async (ctx) => {
    const resorts = await ctx.db.query("resorts").collect();
    return resorts.map(({ continent, country, region }) => ({
      continent,
      country,
      region,
    }));
  },
});

export const saveMany = internalMutation({
  args: {
    resorts: v.array(v.any()),
  },
  returns: v.array(v.id("resorts")),
  handler: async (ctx, args) => {
    const ids = [];

    for (const rawResort of args.resorts) {
      if (!rawResort || typeof rawResort !== "object" || Array.isArray(rawResort)) {
        throw new Error("Each resort must be an object");
      }

      const resort = rawResort as Record<string, unknown>;
      if (typeof resort.resortId !== "string" || !resort.resortId) {
        throw new Error("Each resort must include a resortId");
      }

      const document = selectResortFields(
        resort,
        resort.resortId as string,
      );
      const existing = await ctx.db
        .query("resorts")
        .withIndex("by_resort_id", (q) => q.eq("resortId", resort.resortId as string))
        .unique();

      if (existing) {
        await ctx.db.patch(existing._id, document);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resorts", document));
      }
    }

    return ids;
  },
});

export const getByResortId = query({
  args: { resortId: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resorts")
      .withIndex("by_resort_id", (q) => q.eq("resortId", args.resortId))
      .unique();
  },
});

export const seed = internalMutation({
  args: {},
  returns: v.array(v.id("resorts")),
  handler: async (ctx) => {
    const ids = [];

    for (const resort of resortSeedData) {
      const document = selectResortFields(
        resort as unknown as Record<string, unknown>,
        resort.resortId,
      );
      const existing = await ctx.db
        .query("resorts")
        .withIndex("by_resort_id", (q) => q.eq("resortId", resort.resortId))
        .unique();

      if (existing) {
        await ctx.db.patch(existing._id, document);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resorts", document));
      }
    }

    return ids;
  },
});
