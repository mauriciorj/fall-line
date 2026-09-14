import { internalMutation } from "./_generated/server";
import type { Doc } from "./_generated/dataModel";
import { v } from "convex/values";

const fieldNames = [
  "resortId",
  "name",
  "continent",
  "country",
  "region",
  "address",
  "website",
  "image",
  "rating",
] as const;

type SkiresortinfoDocument = Omit<Doc<"skiresortinfo">, "_id" | "_creationTime">;

function selectFields(
  input: Record<string, unknown>,
  resortId: string,
): SkiresortinfoDocument {
  return {
    ...Object.fromEntries(
      fieldNames
        .filter((fieldName) => input[fieldName] !== undefined)
        .map((fieldName) => [fieldName, input[fieldName]]),
    ),
    resortId,
  } as SkiresortinfoDocument;
}

export const saveMany = internalMutation({
  args: {
    resorts: v.array(v.any()),
  },
  returns: v.array(v.id("skiresortinfo")),
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
      if (typeof resort.name !== "string" || !resort.name) {
        throw new Error("Each resort must include a name");
      }

      const document = selectFields(resort, resort.resortId);
      const existing = await ctx.db
        .query("skiresortinfo")
        .withIndex("by_resort_id", (q) => q.eq("resortId", resort.resortId as string))
        .unique();

      if (existing) {
        await ctx.db.patch(existing._id, document);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("skiresortinfo", document));
      }
    }

    return ids;
  },
});
