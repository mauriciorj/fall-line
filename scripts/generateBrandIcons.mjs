// Generates the brand icon set from one SVG (lucide "mountain" glyph on the
// primary colour): favicon.ico (16/32/48, PNG-in-ICO), app/icon0.svg,
// app/icon1.png (192, a multiple of 48 as Google's favicon guidelines want),
// app/apple-icon.png (180) and the manifest icons in public/icons. Manual
// step; commit the outputs.
//
//   node scripts/generateBrandIcons.mjs
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const PRIMARY = "#4A6FA5";
const GLYPH = "m8 3 4 8 5-5 5 15H2L8 3z"; // lucide-react <Mountain />, 24x24 viewBox

// `inset`: fraction of the canvas kept clear around the glyph. Maskable icons
// need the glyph inside the central 80% (safe zone), regular ones can breathe.
const svg = ({ rounded, inset }) => {
  const size = 64;
  const glyph = size * (1 - 2 * inset);
  const scale = glyph / 24;
  const offset = size * inset;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${rounded ? 14 : 0}" fill="${PRIMARY}"/>
  <g transform="translate(${offset} ${offset}) scale(${scale})" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="${GLYPH}"/>
  </g>
</svg>
`;
};

const png = (markup, size) =>
  sharp(Buffer.from(markup), { density: 72 * (size / 64) * 4 })
    .resize(size, size)
    .png({ compressionLevel: 9 })
    .toBuffer();

// ICO container with PNG-encoded entries (supported by every current browser).
function ico(entries) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(entries.length, 4);
  let offset = header.length + 16 * entries.length;
  const directory = entries.map(({ size, buffer }) => {
    const entry = Buffer.alloc(16);
    entry.writeUInt8(size === 256 ? 0 : size, 0);
    entry.writeUInt8(size === 256 ? 0 : size, 1);
    entry.writeUInt16LE(1, 4); // colour planes
    entry.writeUInt16LE(32, 6); // bits per pixel
    entry.writeUInt32LE(buffer.length, 8);
    entry.writeUInt32LE(offset, 12);
    offset += buffer.length;
    return entry;
  });
  return Buffer.concat([header, ...directory, ...entries.map((e) => e.buffer)]);
}

const app = join(process.cwd(), "src", "app");
const icons = join(process.cwd(), "public", "icons");
mkdirSync(icons, { recursive: true });

const standard = svg({ rounded: true, inset: 0.19 });
const maskable = svg({ rounded: false, inset: 0.26 });

writeFileSync(join(app, "icon0.svg"), standard);
writeFileSync(join(app, "icon1.png"), await png(standard, 192));
writeFileSync(join(app, "apple-icon.png"), await png(svg({ rounded: false, inset: 0.2 }), 180));
writeFileSync(join(icons, "icon-192.png"), await png(standard, 192));
writeFileSync(join(icons, "icon-512.png"), await png(standard, 512));
writeFileSync(join(icons, "icon-512-maskable.png"), await png(maskable, 512));
writeFileSync(
  join(app, "favicon.ico"),
  ico(
    await Promise.all(
      [16, 32, 48].map(async (size) => ({ size, buffer: await png(standard, size) })),
    ),
  ),
);
console.log("brand icons written: favicon.ico, icon0.svg, icon1.png, apple-icon.png, public/icons/*");
