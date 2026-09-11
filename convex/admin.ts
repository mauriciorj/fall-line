import { internalMutation, mutation, query } from "./_generated/server";
import type { QueryCtx } from "./_generated/server";
import { v } from "convex/values";

const articleInput = {
  slug: v.string(),
  title: v.string(),
  description: v.string(),
  body: v.array(v.any()),
  tags: v.array(v.string()),
  published: v.boolean(),
  publishedAt: v.optional(v.number()),
  heroImageId: v.id("_storage"),
};

function identityEmail(identity: Awaited<ReturnType<QueryCtx["auth"]["getUserIdentity"]>>) {
  if (!identity) return undefined;
  const claims = identity as unknown as Record<string, unknown>;
  const value = identity.email ?? claims.email_address ?? claims.emailAddress;
  return typeof value === "string" ? value.trim().toLowerCase() : undefined;
}

async function requireAdmin(ctx: QueryCtx) {
  const email = identityEmail(await ctx.auth.getUserIdentity());
  if (!email) throw new Error("Authentication required");
  const admins = await ctx.db.query("adminEmails").collect();
  const admin = admins.find((record) => record.email.trim().toLowerCase() === email);
  if (!admin?.enabled) throw new Error("Admin access required");
  return email;
}

export const isAdmin = query({
  args: {},
  returns: v.object({ email: v.optional(v.string()), isAdmin: v.boolean() }),
  handler: async (ctx) => {
    const email = identityEmail(await ctx.auth.getUserIdentity());
    if (!email) return { email: undefined, isAdmin: false };
    const admins = await ctx.db.query("adminEmails").collect();
    const admin = admins.find((record) => record.email.trim().toLowerCase() === email);
    return { email, isAdmin: Boolean(admin?.enabled) };
  },
});

export const listAdmins = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    return ctx.db.query("adminEmails").order("asc").collect();
  },
});

export const addAdmin = mutation({
  args: { email: v.string() },
  returns: v.id("adminEmails"),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    const email = args.email.trim().toLowerCase();
    if (!email.includes("@")) throw new Error("A valid email is required");
    const existing = await ctx.db
      .query("adminEmails")
      .withIndex("by_email", (query) => query.eq("email", email))
      .unique();
    if (existing) {
      await ctx.db.patch(existing._id, { enabled: true });
      return existing._id;
    }
    return ctx.db.insert("adminEmails", { email, enabled: true, createdAt: Date.now() });
  },
});

export const setAdminEnabled = mutation({
  args: { id: v.id("adminEmails"), enabled: v.boolean() },
  returns: v.null(),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    await ctx.db.patch(args.id, { enabled: args.enabled });
    return null;
  },
});

export const listLocations = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    return ctx.db.query("locations").order("asc").collect();
  },
});

export const syncLocations = mutation({
  args: {},
  returns: v.number(),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    const resorts = await ctx.db.query("resorts").collect();
    const unique = new Map<string, { continent: string; country: string; region: string }>();
    for (const resort of resorts) {
      if (resort.published === false || !resort.continent || !resort.country) continue;
      const region = resort.region ?? "Unknown";
      const key = `${resort.continent.toLowerCase()}|${resort.country.toLowerCase()}|${region.toLowerCase()}`;
      unique.set(key, { continent: resort.continent, country: resort.country, region });
    }
    const existing = await ctx.db.query("locations").collect();
    for (const location of existing) await ctx.db.delete(location._id);
    for (const location of unique.values()) await ctx.db.insert("locations", location);
    return unique.size;
  },
});

export const listResorts = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    return ctx.db.query("resorts").order("asc").collect();
  },
});

export const updateResort = mutation({
  args: { id: v.id("resorts"), fields: v.any() },
  returns: v.null(),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    const allowed = new Set([
      "published", "name", "address", "website", "email", "phone", "tollFree",
      "dayTicketPrice", "lessonsPrice", "skiRentalPrice", "snowBoardRentalPrice",
      "tubbingPrice", "rating", "ticketUrl",
    ]);
    const input = args.fields as Record<string, unknown>;
    const fields = Object.fromEntries(Object.entries(input).filter(([key]) => allowed.has(key)));
    await ctx.db.patch(args.id, fields);
    return null;
  },
});

export const listArticles = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    return ctx.db.query("articles").order("desc").collect();
  },
});

export const generateArticleUploadUrl = mutation({
  args: {},
  returns: v.string(),
  handler: async (ctx) => {
    await requireAdmin(ctx);
    return ctx.storage.generateUploadUrl();
  },
});

export const createArticle = mutation({
  args: articleInput,
  returns: v.id("articles"),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    const now = Date.now();
    return ctx.db.insert("articles", {
      ...args,
      publishedAt: args.publishedAt ?? now,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const updateArticle = mutation({
  args: {
    id: v.id("articles"),
    slug: v.optional(v.string()),
    title: v.optional(v.string()),
    description: v.optional(v.string()),
    body: v.optional(v.array(v.any())),
    tags: v.optional(v.array(v.string())),
    published: v.optional(v.boolean()),
    publishedAt: v.optional(v.number()),
    heroImageId: v.optional(v.id("_storage")),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    const { id, ...patch } = args;
    await ctx.db.patch(id, { ...patch, updatedAt: Date.now() });
    return null;
  },
});

export const deleteArticle = mutation({
  args: { id: v.id("articles") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await requireAdmin(ctx);
    await ctx.db.delete(args.id);
    return null;
  },
});

export const seedAdmin = internalMutation({
  args: { email: v.string() },
  returns: v.id("adminEmails"),
  handler: async (ctx, args) => {
    const email = args.email.trim().toLowerCase();
    const existing = await ctx.db
      .query("adminEmails")
      .withIndex("by_email", (query) => query.eq("email", email))
      .unique();
    if (existing) return existing._id;
    return ctx.db.insert("adminEmails", { email, enabled: true, createdAt: Date.now() });
  },
});