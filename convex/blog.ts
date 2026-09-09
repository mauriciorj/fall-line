import { internalMutation, query } from "./_generated/server";
import type { QueryCtx } from "./_generated/server";
import type { Doc } from "./_generated/dataModel";
import { v } from "convex/values";

const articleInputFields = {
  slug: v.string(),
  title: v.string(),
  description: v.string(),
  body: v.array(v.any()),
  tags: v.array(v.string()),
  published: v.boolean(),
  heroImageId: v.id("_storage"),
};

async function withHeroImageUrl(ctx: QueryCtx, article: Doc<"articles">) {
  const { heroImageId, ...content } = article;
  return {
    ...content,
    heroImageUrl: heroImageId ? await ctx.storage.getUrl(heroImageId) : null,
  };
}

export const listPublished = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    const articles = await ctx.db
      .query("articles")
      .withIndex("by_published", (query) => query.eq("published", true))
      .order("desc")
      .collect();

    return Promise.all(articles.map((article) => withHeroImageUrl(ctx, article)));
  },
});

export const getPublishedBySlug = query({
  args: { slug: v.string() },
  returns: v.union(v.any(), v.null()),
  handler: async (ctx, args) => {
    const article = await ctx.db
      .query("articles")
      .withIndex("by_slug", (query) => query.eq("slug", args.slug))
      .unique();

    if (!article || !article.published) {
      return null;
    }

    return withHeroImageUrl(ctx, article);
  },
});

export const generateUploadUrl = internalMutation({
  args: {},
  returns: v.string(),
  handler: async (ctx) => ctx.storage.generateUploadUrl(),
});

export const create = internalMutation({
  args: {
    ...articleInputFields,
    publishedAt: v.optional(v.number()),
  },
  returns: v.id("articles"),
  handler: async (ctx, args) => {
    const now = Date.now();
    const { publishedAt, ...article } = args;
    return ctx.db.insert("articles", {
      ...article,
      publishedAt: publishedAt ?? now,
      createdAt: now,
      updatedAt: now,
    });
  },
});

export const update = internalMutation({
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
    const { id, ...patch } = args;
    await ctx.db.patch(id, { ...patch, updatedAt: Date.now() });
    return null;
  },
});

export const remove = internalMutation({
  args: { id: v.id("articles") },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id);
    return null;
  },
});