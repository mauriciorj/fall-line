"use client";

import { useMemo, useState } from "react";
import { SignInButton, useClerk, useUser } from "@clerk/nextjs";
import { Authenticated, AuthLoading, Unauthenticated, useMutation, useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import type { Id } from "@/convex/_generated/dataModel";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

type Block = { type: "paragraph" | "heading" | "list"; text: string; level?: number; items?: string[] };

type ResortRecord = {
  _id: Id<"resorts">;
  resortId: string;
  name?: string;
  address?: string;
  website?: string;
  email?: string;
  phone?: string;
  ticketUrl?: string;
  tollFree?: string;
  dayTicketPrice?: number;
  lessonsPrice?: number;
  skiRentalPrice?: number;
  snowBoardRentalPrice?: number;
  tubbingPrice?: number;
  rating?: number;
  published?: boolean;
};

type LocationRecord = { _id: string; country: string; region: string };
type AdminRecord = { _id: Id<"adminEmails">; email: string; enabled: boolean };
type ArticleRecord = { _id: Id<"articles">; slug: string; title: string; description: string; tags: string[]; published: boolean; heroImageId: string; body: unknown[] };

type Draft = {
  slug: string;
  title: string;
  description: string;
  tags: string;
  published: boolean;
  heroImageId?: string;
  blocks: Block[];
};

const emptyDraft: Draft = {
  slug: "",
  title: "",
  description: "",
  tags: "",
  published: false,
  blocks: [{ type: "paragraph", text: "" }],
};

function AdminDashboard() {
  const { user } = useUser();
  console.log("")
  console.log("")
  console.log("user => ", user)
  const { signOut } = useClerk();
  const status = useQuery(api.admin.isAdmin);
  const isAdmin = status?.isAdmin === true;
  const locations = useQuery(api.admin.listLocations, isAdmin ? {} : "skip") as LocationRecord[] | undefined;
  const resorts = useQuery(api.admin.listResorts, isAdmin ? {} : "skip") as ResortRecord[] | undefined;
  const admins = useQuery(api.admin.listAdmins, isAdmin ? {} : "skip") as AdminRecord[] | undefined;
  const articles = useQuery(api.admin.listArticles, isAdmin ? {} : "skip") as ArticleRecord[] | undefined;
  const syncLocations = useMutation(api.admin.syncLocations);
  const updateResort = useMutation(api.admin.updateResort);
  const addAdmin = useMutation(api.admin.addAdmin);
  const setAdminEnabled = useMutation(api.admin.setAdminEnabled);
  const createArticle = useMutation(api.admin.createArticle);
  const updateArticle = useMutation(api.admin.updateArticle);
  const deleteArticle = useMutation(api.admin.deleteArticle);
  const generateUploadUrl = useMutation(api.admin.generateArticleUploadUrl);

  const [selectedResortId, setSelectedResortId] = useState<Id<"resorts"> | null>(null);
  const selectedResort = useMemo(
    () => resorts?.find((resort) => resort._id === selectedResortId),
    [resorts, selectedResortId],
  );
  const [resortForm, setResortForm] = useState<Record<string, string | number | boolean | undefined>>({});
  const [adminEmail, setAdminEmail] = useState("");
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [editingArticleId, setEditingArticleId] = useState<Id<"articles"> | null>(null);
  const [busy, setBusy] = useState(false);

  const startResortEdit = (resort: ResortRecord) => {
    setSelectedResortId(resort._id);
    setResortForm({
      name: resort.name ?? "",
      address: resort.address ?? "",
      website: resort.website ?? "",
      email: resort.email ?? "",
      phone: resort.phone ?? "",
      ticketUrl: resort.ticketUrl ?? "",
      tollFree: resort.tollFree ?? "",
      dayTicketPrice: resort.dayTicketPrice ?? "",
      lessonsPrice: resort.lessonsPrice ?? "",
      skiRentalPrice: resort.skiRentalPrice ?? "",
      snowBoardRentalPrice: resort.snowBoardRentalPrice ?? "",
      tubbingPrice: resort.tubbingPrice ?? "",
      rating: resort.rating ?? "",
      published: resort.published !== false,
    });
  };

  const saveResort = async () => {
    if (!selectedResortId) return;
    setBusy(true);
    try {
      const fields = { ...resortForm };
      for (const field of ["dayTicketPrice", "lessonsPrice", "skiRentalPrice", "snowBoardRentalPrice", "tubbingPrice", "rating"]) {
        const value = fields[field];
        fields[field] = value === "" ? undefined : Number(value);
      }
      await updateResort({ id: selectedResortId, fields });
    } finally {
      setBusy(false);
    }
  };

  const startArticleEdit = (article: ArticleRecord) => {
    setEditingArticleId(article._id);
    setDraft({
      slug: article.slug,
      title: article.title,
      description: article.description,
      tags: article.tags.join(", "),
      published: article.published,
      heroImageId: article.heroImageId,
      blocks: article.body as Block[],
    });
  };

  const uploadHero = async (file: File) => {
    const uploadUrl = await generateUploadUrl({});
    const response = await fetch(uploadUrl, {
      method: "POST",
      headers: { "Content-Type": file.type },
      body: file,
    });
    const { storageId } = await response.json() as { storageId: string };
    setDraft((current) => ({ ...current, heroImageId: storageId }));
  };

  const saveArticle = async () => {
    if (!draft.heroImageId || !draft.slug || !draft.title) return;
    setBusy(true);
    try {
      const payload = {
        slug: draft.slug,
        title: draft.title,
        description: draft.description,
        body: draft.blocks,
        tags: draft.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
        published: draft.published,
        heroImageId: draft.heroImageId as never,
      };
      if (editingArticleId) {
        await updateArticle({ id: editingArticleId, ...payload });
      } else {
        await createArticle(payload as never);
      }
      setDraft(emptyDraft);
      setEditingArticleId(null);
    } finally {
      setBusy(false);
    }
  };

  if (!isAdmin) {
    return (
      <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-2xl flex-col items-center justify-center gap-4 px-6 text-center">
        <h1 className="font-serif text-3xl font-semibold">Access denied</h1>
        <p className="text-muted-foreground">Clerk: {user?.primaryEmailAddress?.emailAddress ?? "unknown"}</p>
        <p className="text-muted-foreground">Convex: {status?.email ?? "not authenticated"}</p>
        <p className="text-muted-foreground">This email is not enabled in adminEmails.</p>
        <Button variant="outline" onClick={() => signOut({ redirectUrl: "/" })}>Sign out</Button>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl space-y-10 px-6 py-10">
      <header>
        <p className="text-sm uppercase tracking-[0.2em] text-primary">Admin</p>
        <h1 className="font-serif text-4xl font-semibold">Dashboard</h1>
      </header>

      <section className="space-y-4 rounded-xl border border-border bg-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div><h2 className="text-2xl font-semibold">Locations</h2><p className="text-sm text-muted-foreground">{locations?.length ?? 0} locations registered</p></div>
          <Button onClick={() => syncLocations({})}>Update locations</Button>
        </div>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          {locations?.map((location) => <span key={location._id} className="rounded-full bg-muted px-3 py-1">{location.country} / {location.region}</span>)}
        </div>
      </section>

      <section className="space-y-4 rounded-xl border border-border bg-card p-6">
        <div><h2 className="text-2xl font-semibold">Resorts</h2><p className="text-sm text-muted-foreground">{resorts?.length ?? 0} resorts registered</p></div>
        <div className="grid gap-3 md:grid-cols-2">
          {resorts?.map((resort) => (
            <button key={resort._id} onClick={() => startResortEdit(resort)} className="flex items-center justify-between rounded-lg border border-border p-4 text-left hover:bg-muted/40">
              <span>{resort.name ?? resort.resortId}</span>
              <span className={resort.published === false ? "text-destructive" : "text-green-600"}>{resort.published === false ? "Hidden" : "Published"}</span>
            </button>
          ))}
        </div>
        {selectedResort && (
          <div className="grid gap-3 border-t border-border pt-5 md:grid-cols-2">
            {["name", "address", "website", "email", "phone", "ticketUrl", "tollFree"].map((field) => (
              <Input key={field} value={String(resortForm[field] ?? "")} placeholder={field} onChange={(event) => setResortForm({ ...resortForm, [field]: event.target.value })} />
            ))}
            {["dayTicketPrice", "lessonsPrice", "skiRentalPrice", "snowBoardRentalPrice", "tubbingPrice", "rating"].map((field) => (
              <Input key={field} type="number" step="any" value={String(resortForm[field] ?? "")} placeholder={field} onChange={(event) => setResortForm({ ...resortForm, [field]: event.target.value })} />
            ))}
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={Boolean(resortForm.published)} onChange={(event) => setResortForm({ ...resortForm, published: event.target.checked })} /> Published</label>
            <Button disabled={busy} onClick={saveResort}>Save resort</Button>
          </div>
        )}
      </section>

      <section className="space-y-4 rounded-xl border border-border bg-card p-6">
        <h2 className="text-2xl font-semibold">Admin emails</h2>
        <div className="flex gap-2"><Input value={adminEmail} placeholder="admin@example.com" onChange={(event) => setAdminEmail(event.target.value)} /><Button onClick={async () => { await addAdmin({ email: adminEmail }); setAdminEmail(""); }}>Add</Button></div>
        <div className="space-y-2">{admins?.map((admin) => <div key={admin._id} className="flex items-center justify-between text-sm"><span>{admin.email}</span><Button variant="outline" size="sm" onClick={() => setAdminEnabled({ id: admin._id, enabled: !admin.enabled })}>{admin.enabled ? "Disable" : "Enable"}</Button></div>)}</div>
      </section>

      <section className="space-y-5 rounded-xl border border-border bg-card p-6">
        <div className="flex items-center justify-between"><h2 className="text-2xl font-semibold">Blog</h2><Button variant="outline" onClick={() => { setDraft(emptyDraft); setEditingArticleId(null); }}>New article</Button></div>
        <div className="grid gap-2">{articles?.map((article) => <div key={article._id} className="flex items-center justify-between gap-3 rounded-lg border border-border p-3"><span>{article.title}</span><div className="flex gap-2"><Button size="sm" variant="outline" onClick={() => startArticleEdit(article)}>Edit</Button><Button size="sm" variant="destructive" onClick={() => deleteArticle({ id: article._id })}>Delete</Button></div></div>)}</div>
        <div className="space-y-3 border-t border-border pt-5">
          <Input placeholder="Slug" value={draft.slug} onChange={(event) => setDraft({ ...draft, slug: event.target.value })} />
          <Input placeholder="Title" value={draft.title} onChange={(event) => setDraft({ ...draft, title: event.target.value })} />
          <Input placeholder="Description" value={draft.description} onChange={(event) => setDraft({ ...draft, description: event.target.value })} />
          <Input placeholder="Tags, comma separated" value={draft.tags} onChange={(event) => setDraft({ ...draft, tags: event.target.value })} />
          <label className="block text-sm">Hero image<input className="mt-1 block w-full text-sm" type="file" accept="image/*" onChange={(event) => event.target.files?.[0] && uploadHero(event.target.files[0])} /></label>
          <div className="space-y-2"><p className="text-sm font-medium">Body blocks</p>{draft.blocks.map((block, index) => <div key={index} className="grid gap-2 rounded-lg border border-border p-3"><select className="rounded-md border border-input bg-background px-3 py-2 text-sm" value={block.type} onChange={(event) => { const blocks = [...draft.blocks]; blocks[index] = { ...block, type: event.target.value as Block["type"] }; setDraft({ ...draft, blocks }); }}><option value="paragraph">Paragraph</option><option value="heading">Heading</option><option value="list">List</option></select><Textarea value={block.type === "list" ? (block.items ?? []).join("\n") : block.text} placeholder="Content" onChange={(event) => { const blocks = [...draft.blocks]; blocks[index] = block.type === "list" ? { ...block, items: event.target.value.split("\n") } : { ...block, text: event.target.value }; setDraft({ ...draft, blocks }); }} /></div>)}<Button variant="outline" onClick={() => setDraft({ ...draft, blocks: [...draft.blocks, { type: "paragraph", text: "" }] })}>Add block</Button></div>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={draft.published} onChange={(event) => setDraft({ ...draft, published: event.target.checked })} /> Published</label>
          <Button disabled={busy || !draft.heroImageId} onClick={saveArticle}>Save article</Button>
        </div>
      </section>
    </main>
  );
}

export default function AdminPage() {
  return (
    <>
      <AuthLoading>
        <main className="flex min-h-[calc(100vh-73px)] items-center justify-center text-muted-foreground">Authenticating...</main>
      </AuthLoading>
      <Unauthenticated>
        <main className="mx-auto flex min-h-[calc(100vh-73px)] max-w-2xl flex-col items-center justify-center gap-4 px-6 text-center">
          <h1 className="font-serif text-3xl font-semibold">Admin dashboard</h1>
          <p className="text-muted-foreground">Sign in with an authorized admin account.</p>
          <SignInButton mode="modal"><Button>Sign in</Button></SignInButton>
        </main>
      </Unauthenticated>
      <Authenticated>
        <AdminDashboard />
      </Authenticated>
    </>
  );
}
