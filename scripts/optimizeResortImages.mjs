// Brings resort images in public/assets/resorts within a size budget and
// derives a 1200x630 social crop (og.jpg) per resort. Manual step: run after
// adding or replacing images, then commit.
//
// Rules: a file is only touched when it is missing or over budget, and a result
// is only written when it is smaller than what exists. Encoding always starts
// from the best available source (original jpg/png/avif, else the webp itself),
// read into memory first because libvips keeps file handles open until GC,
// which blocks overwriting the same path on Windows.
//
//   node scripts/optimizeResortImages.mjs
import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const root = join(process.cwd(), "public", "assets", "resorts");
const HERO = { maxWidth: 1920, quality: 75, budget: 400 * 1024 };
const TRAIL = { maxWidth: 2400, quality: 85, budget: 400 * 1024 };
const OG = { width: 1200, height: 630, quality: 80 };

const kb = (bytes) => `${Math.round(bytes / 1024)} KB`;
const isRaster = (file) => /\.(jpe?g|png|avif)$/i.test(file);
const sizeOf = (path) => statSync(path).size;

const encodeWebp = (source, { maxWidth, quality }) =>
  sharp(readFileSync(source))
    .rotate()
    .resize({ width: maxWidth, withoutEnlargement: true })
    .webp({ quality, effort: 5 })
    .toBuffer();

// Ensures `<dir>/<base>.webp` exists and is within budget, encoding from the
// raster original when available.
async function ensureWebp(dir, base, candidates, settings, label) {
  const target = join(dir, `${base}.webp`);
  const existing = candidates.includes(`${base}.webp`) ? sizeOf(target) : null;
  if (existing !== null && existing <= settings.budget) return;

  const original = candidates.find(isRaster);
  const source = original ? join(dir, original) : existing !== null ? target : null;
  if (!source) return;

  const buffer = await encodeWebp(source, settings);
  if (existing !== null && buffer.length >= existing) {
    console.log(`${label}: ${base}.webp kept at ${kb(existing)} (re-encode not smaller)`);
    return;
  }
  writeFileSync(target, buffer);
  const over = buffer.length > settings.budget ? " (still over budget)" : "";
  console.log(`${label}: ${base}.webp ${existing === null ? "new" : kb(existing)} -> ${kb(buffer.length)}${over}`);
}

for (const country of readdirSync(root)) {
  for (const region of readdirSync(join(root, country))) {
    for (const resort of readdirSync(join(root, country, region))) {
      const dir = join(root, country, region, resort);
      if (!statSync(dir).isDirectory()) continue;
      const files = readdirSync(dir);
      const label = `${country}/${region}/${resort}`;

      const heroFiles = files.filter((file) => /^hero\.(webp|jpe?g|png|avif)$/i.test(file));
      await ensureWebp(dir, "hero", heroFiles, HERO, label);

      // Social image: regenerated every run from the best source (deterministic bytes).
      const heroSource = heroFiles.find(isRaster) ?? heroFiles.find((file) => file.endsWith(".webp"));
      if (heroSource) {
        const og = await sharp(readFileSync(join(dir, heroSource)))
          .rotate()
          .resize({ width: OG.width, height: OG.height, fit: "cover", position: "attention" })
          .jpeg({ quality: OG.quality, progressive: true, mozjpeg: true })
          .toBuffer();
        writeFileSync(join(dir, "og.jpg"), og);
      }

      // Trail maps, grouped per index (trail, trail-1, trail-2, ...).
      const groups = new Map();
      for (const file of files) {
        const match = file.match(/^(trail(?:-\d+)?)\.(webp|jpe?g|png|avif)$/i);
        if (match) groups.set(match[1], [...(groups.get(match[1]) ?? []), file]);
      }
      for (const [base, candidates] of groups) {
        await ensureWebp(dir, base, candidates, TRAIL, label);
      }
    }
  }
}
