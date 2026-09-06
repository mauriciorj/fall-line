import { internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { resortRentalsFields } from "./schema";

export const save = internalMutation({
  args: {
    ...resortRentalsFields,
    fetchedAt: v.optional(v.number()),
  },
  returns: v.id("resortRentals"),
  handler: async (ctx, args) => {
    const { fetchedAt: fetchedAtArg, ...docFields } = args;
    const fetchedAt = fetchedAtArg ?? Date.now();
    const doc = { ...docFields, fetchedAt };

    const existing = await ctx.db
      .query("resortRentals")
      .withIndex("by_resort", (q) => q.eq("resortName", args.resortName))
      .unique();

    if (existing) {
      await ctx.db.replace(existing._id, doc);
      return existing._id;
    }

    return await ctx.db.insert("resortRentals", doc);
  },
});
