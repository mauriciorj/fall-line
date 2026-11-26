// Creates a web-optimized .webp next to every raster image (jpg, jpeg, png,
// avif, gif, tif, tiff) under apps/web/public/assets that has no .webp of the
// same name yet. Originals are kept; og.jpg is skipped because social previews
// must stay JPEG.
//
// Quality: photos start at q80, trail maps (names with trail/map) and PNG graphics at
// q88. Quality steps down only while the file is over its size budget, never
// below the floor, so detail is preserved first and size second. Images wider
// than the max width are downscaled; smaller ones are never enlarged. EXIF
// (including GPS) is stripped, orientation is applied, alpha is kept.
//
//   node scripts/convertImagesToWebp.mjs             convert missing .webp files
//   node scripts/convertImagesToWebp.mjs --dry-run   list what would be converted
//   node scripts/convertImagesToWebp.mjs --force     re-encode existing .webp from originals
//   node scripts/convertImagesToWebp.mjs --dir <path>  use another root folder
import { readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const force = args.includes("--force");
const dirIndex = args.indexOf("--dir");
const root = dirIndex >= 0
  ? resolve(args[dirIndex + 1])
  : join(dirname(fileURLToPath(import.meta.url)), "..", "apps", "web", "public", "assets");

const PHOTO = { maxWidth: 1920, quality: 80, floor: 62, budget: 400 * 1024 };
const DETAIL = { maxWidth: 2400, quality: 88, floor: 72, budget: 600 * 1024 };
const RASTER = /\.(jpe?g|png|avif|gif|tiff?)$/i;
const LOSSLESS = /\.(png|gif|tiff?)$/i;

const kb = (bytes) => `${Math.round(bytes / 1024)} KB`;

// Several originals can share a base name (trail.png + trail.jpg): use the one
// with the most pixels, preferring lossless formats on a tie.
async function pickSource(dir, files) {
  const ranked = await Promise.all(files.map(async (file) => {
    const { width = 0, height = 0 } = await sharp(readFileSync(join(dir, file))).metadata();
    return { file, pixels: width * height, lossless: LOSSLESS.test(file) ? 1 : 0 };
  }));
  ranked.sort((a, b) => b.pixels - a.pixels || b.lossless - a.lossless);
  return ranked[0].file;
}

async function encode(input, settings, animated) {
  const { maxWidth, floor, budget } = settings;
  for (let quality = settings.quality; ; quality -= 4) {
    const buffer = await sharp(input, { animated })
      .rotate()
      .resize({ width: maxWidth, withoutEnlargement: true })
      .webp({ quality: Math.max(quality, floor), effort: 6, smartSubsample: true })
      .toBuffer();
    if (buffer.length <= budget || quality <= floor) return { buffer, quality: Math.max(quality, floor) };
  }
}

const stats = { created: 0, skipped: 0, notSmaller: 0, failed: 0, before: 0, after: 0 };

async function processDir(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files = entries.filter((entry) => entry.isFile()).map((entry) => entry.name);
  const groups = new Map();
  for (const file of files) {
    if (!RASTER.test(file) || file.toLowerCase() === "og.jpg") continue;
    const base = file.slice(0, -extname(file).length);
    groups.set(base, [...(groups.get(base) ?? []), file]);
  }

  for (const [base, candidates] of groups) {
    const target = `${base}.webp`;
    const label = relative(root, join(dir, target)).replaceAll("\\", "/");
    const exists = files.some((file) => file.toLowerCase() === target.toLowerCase());
    if (exists && !force) {
      stats.skipped++;
      continue;
    }
    try {
      const source = await pickSource(dir, candidates);
      const input = readFileSync(join(dir, source)); // in memory: libvips holds file handles on Windows
      const original = input.length;
      if (dryRun) {
        console.log(`would convert ${label} from ${source} (${kb(original)})`);
        stats.created++;
        continue;
      }
      const settings = /trail|map/i.test(base) || LOSSLESS.test(source) ? DETAIL : PHOTO;
      const { buffer, quality } = await encode(input, settings, /\.gif$/i.test(source));
      if (buffer.length >= original) {
        console.log(`skip ${label}: webp ${kb(buffer.length)} not smaller than ${source} ${kb(original)}`);
        stats.notSmaller++;
        continue;
      }
      writeFileSync(join(dir, target), buffer);
      stats.created++;
      stats.before += original;
      stats.after += buffer.length;
      const over = buffer.length > settings.budget ? ", over budget at quality floor" : "";
      console.log(`${label}: ${source} ${kb(original)} -> ${kb(buffer.length)} (q${quality}${over})`);
    } catch (error) {
      stats.failed++;
      console.error(`failed ${label}: ${error.message}`);
    }
  }

  for (const entry of entries) {
    if (entry.isDirectory()) await processDir(join(dir, entry.name));
  }
}

if (!statSync(root, { throwIfNoEntry: false })?.isDirectory()) {
  console.error(`Folder not found: ${root}`);
  process.exit(1);
}
await processDir(root);

const saved = stats.before ? ` | ${kb(stats.before)} -> ${kb(stats.after)}` : "";
console.log(`\n${dryRun ? "to convert" : "created"}: ${stats.created}, already webp: ${stats.skipped}, not smaller: ${stats.notSmaller}, failed: ${stats.failed}${saved}`);
if (!dryRun && stats.created) console.log("Run `node scripts/generateResortAssets.mjs` (or pnpm dev/build) so the apps use the new files.");
if (stats.failed) process.exitCode = 1;
