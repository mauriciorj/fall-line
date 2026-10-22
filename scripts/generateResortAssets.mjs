// Scans public/assets/resorts and writes src/data/resortAssets.json so the app
// knows which hero/trail-map files exist without probing the filesystem at
// request time (ISR revalidation on serverless hosts has no `public/` on disk).
import { mkdirSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

const root = join(process.cwd(), "public", "assets", "resorts");
const output = join(process.cwd(), "src", "data", "resortAssets.json");
const formatRank = ["webp", "avif", "jpg", "jpeg", "png"];

const bestFormat = (candidates) =>
  candidates
    .map((file) => ({ file, rank: formatRank.indexOf(file.split(".").pop().toLowerCase()) }))
    .filter(({ rank }) => rank !== -1)
    .sort((a, b) => a.rank - b.rank)[0]?.file ?? null;

const manifest = {};
for (const country of readdirSync(root)) {
  for (const region of readdirSync(join(root, country))) {
    for (const resort of readdirSync(join(root, country, region))) {
      const dir = join(root, country, region, resort);
      if (!statSync(dir).isDirectory()) continue;
      const files = readdirSync(dir);

      const hero = bestFormat(files.filter((file) => /^hero\.\w+$/i.test(file)));

      // trail-1.webp, trail-2.jpg, ...; a bare trail.* counts as index 1.
      const byIndex = new Map();
      for (const file of files) {
        const match = file.match(/^trail(?:-(\d+))?\.(\w+)$/i);
        if (!match) continue;
        const index = Number(match[1] ?? 1);
        byIndex.set(index, [...(byIndex.get(index) ?? []), file]);
      }
      const trailMaps = [...byIndex.entries()]
        .sort(([a], [b]) => a - b)
        .map(([, candidates]) => bestFormat(candidates))
        .filter(Boolean);

      // 1200x630 social crop produced by scripts/optimizeResortImages.mjs.
      const og = files.includes("og.jpg") ? "og.jpg" : null;

      manifest[`${country}/${region}/${resort}`] = { hero, og, trailMaps };
    }
  }
}

mkdirSync(dirname(output), { recursive: true });
writeFileSync(output, `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`resortAssets.json: ${Object.keys(manifest).length} resorts`);
