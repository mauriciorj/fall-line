// Starts Expo Go through a tunnel and builds the first Android and iOS bundles
// locally, so the phone's first request does not hit the tunnel's ~30s gateway
// timeout while Metro is still bundling.
import { spawn } from "node:child_process";

const port = process.env.EXPO_PORT ?? "8081";
const local = `http://127.0.0.1:${port}`;
const expo = spawn(`expo start --go --tunnel --port ${port}`, { shell: true, stdio: "inherit" });
expo.on("exit", (code) => process.exit(code ?? 0));
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => expo.kill(signal));

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForMetro() {
  for (;;) {
    try {
      if ((await (await fetch(`${local}/status`)).text()).includes("running")) return;
    } catch {}
    await sleep(1000);
  }
}

async function warm(platform) {
  const headers = { "expo-platform": platform, accept: "application/expo+json,application/json" };
  const manifest = await (await fetch(`${local}/`, { headers })).json();
  const started = Date.now();
  // In tunnel mode the manifest points at the tunnel; build through Metro directly.
  const bundle = new URL(manifest.launchAsset.url);
  const response = await fetch(new URL(bundle.pathname + bundle.search, local));
  await response.arrayBuffer();
  if (!response.ok) throw new Error(`${platform} bundle failed with HTTP ${response.status}`);
  return `${platform} ${Math.round((Date.now() - started) / 1000)}s`;
}

await waitForMetro();
console.log("\nPreparing Android and iOS bundles before opening Expo Go...");
const results = await Promise.allSettled([warm("android"), warm("ios")]);
for (const result of results) {
  console.log(result.status === "fulfilled" ? `Bundle ready: ${result.value}` : `Bundle warm-up failed: ${result.reason.message}`);
}
console.log("Ready: scan the QR code above with Expo Go.\n");
