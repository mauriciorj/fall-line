import { internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { resortRatesFields } from "./schema";

export const save = internalMutation({
  args: {
    ...resortRatesFields,
    fetchedAt: v.optional(v.number()),
  },
  returns: v.id("resortRates"),
  handler: async (ctx, args) => {
    const { fetchedAt: fetchedAtArg, ...docFields } = args;
    const fetchedAt = fetchedAtArg ?? Date.now();
    const doc = { ...docFields, fetchedAt };

    const existing = await ctx.db
      .query("resortRates")
      .withIndex("by_resort", (q) => q.eq("resortName", args.resortName))
      .unique();

    if (existing) {
      await ctx.db.replace(existing._id, doc);
      return existing._id;
    }

    return await ctx.db.insert("resortRates", doc);
  },
});
