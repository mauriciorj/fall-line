import { internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { ensureResort } from "./resorts";
import { resortRentalsFields } from "./schema";

export const save = internalMutation({
  args: {
    ...resortRentalsFields,
    updatedAt: v.optional(v.number()),
  },
  returns: v.id("resortRentals"),
  handler: async (ctx, args) => {
    const { updatedAt: updatedAtArg, ...docFields } = args;
    const updatedAt = updatedAtArg ?? Date.now();
    await ensureResort(ctx, {
      resortId: args.resortId,
      website: args.sourceUrl,
    });
    const doc = { ...docFields, updatedAt };

    const existing = await ctx.db
      .query("resortRentals")
      .withIndex("by_resort", (q) => q.eq("resortId", args.resortId))
      .unique();

    if (existing) {
      await ctx.db.replace(existing._id, doc);
      return existing._id;
    }

    return await ctx.db.insert("resortRentals", doc);
  },
});
