import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";
import { ensureResort } from "./resorts";
import { resortHoursFields } from "./schema";

export const save = internalMutation({
  args: {
    ...resortHoursFields,
    updatedAt: v.optional(v.number()),
  },
  returns: v.id("resortHours"),
  handler: async (ctx, args) => {
    const { updatedAt: updatedAtArg, ...docFields } = args;
    const updatedAt = updatedAtArg ?? Date.now();
    await ensureResort(ctx, {
      resortId: args.resortId,
      website: args.sourceUrl,
    });
    const doc = { ...docFields, updatedAt };

    const existing = await ctx.db
      .query("resortHours")
      .withIndex("by_resort", (q) => q.eq("resortId", args.resortId))
      .unique();

    if (existing) {
      await ctx.db.replace(existing._id, doc);
      return existing._id;
    }

    return await ctx.db.insert("resortHours", doc);
  },
});

export const getByResort = query({
  args: { resortId: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resortHours")
      .withIndex("by_resort", (q) => q.eq("resortId", args.resortId))
      .unique();
  },
});
