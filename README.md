# Fall Line

pnpm workspace: Next.js web app in `apps/web`, Expo app in `apps/mobile`,
shared logic in `packages/shared`, and Convex functions in `convex`.

## Development

Run `pnpm install` from the repository root, then:

```sh
pnpm start:web      # Next.js only (http://localhost:3000)
pnpm start:mobile   # Expo development server only
pnpm start:all      # Both servers; Ctrl+C stops both
```

The equivalent commands are `pnpm dev:web`, `pnpm dev:mobile`, and
`pnpm dev:all`. `pnpm dev` starts web only. `pnpm build` builds web;
`pnpm start` starts the built web app.

Web loads environment variables from `apps/web/.env*` first. Root `.env*`
files remain fallbacks, so existing Convex CLI configuration stays in
place. Mobile has separate configuration and requires a custom development
build for Google Maps on iOS; see `apps/mobile/README.md`.

Resort assets live in `apps/web/public/assets/resorts`. The web dev/build scripts
generate the shared manifest at `packages/shared/src/data/resortAssets.json`.

## Vercel

Set the project root directory to `apps/web` and permit access to files outside
that directory: the web app needs root `convex`, `scripts`, and
`packages/shared`, as well as the pnpm workspace lockfile. Keep existing Vercel
environment variables. Changing the Vercel project configuration and deploying
are separate actions.
