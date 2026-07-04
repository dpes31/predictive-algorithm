import { chromium } from "playwright";
import fs from "node:fs";

const baseUrl = process.env.PREVIEW_URL?.replace(/\/$/, "");
if (!baseUrl) throw new Error("PREVIEW_URL is required");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const result = {
  status: "STARTED",
  preview_url: baseUrl,
  checks: {},
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
const page = await context.newPage();
const externalApiCalls = [];
const previewOrigin = new URL(baseUrl).origin;

page.on("request", (request) => {
  if (!["fetch", "xhr"].includes(request.resourceType())) return;
  const url = new URL(request.url());
  if (url.origin !== previewOrigin) externalApiCalls.push(request.url());
});

try {
  await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
  await page.locator("#predict-button").waitFor({ state: "visible" });
  await page.waitForFunction(() => !document.querySelector("#predict-button")?.disabled);
  assert((await page.locator("#latest-draw").textContent())?.trim() === "1230회", "initial latest draw must be 1230");
  assert((await page.locator("#target-draw").textContent())?.trim() === "1231회", "initial target draw must be 1231");
  assert(await page.locator("#result-panel").evaluate((element) => element.classList.contains("hidden")), "results must be hidden before click");
  result.checks.home_initial_state = "PASS";

  await page.locator("#predict-button").click();
  await page.locator("#result-panel:not(.hidden)").waitFor();
  const initialRows = page.locator("#result-sets .result-row");
  assert((await initialRows.count()) === 5, "initial prediction must contain five sets");
  for (let index = 0; index < 5; index += 1) {
    assert((await initialRows.nth(index).locator(".lotto-ball").count()) === 6, `set ${index + 1} must contain six numbers`);
  }
  const initialSeed = (await page.locator("#result-seed").textContent())?.trim() || "";
  const initialHash = (await page.locator("#result-hash").textContent())?.trim() || "";
  assert(/^[0-9a-f]{64}$/.test(initialSeed), "initial seed must be a SHA-256 hex string");
  assert(/^[0-9a-f]{64}$/.test(initialHash), "initial prediction hash must be a SHA-256 hex string");
  await page.screenshot({ path: "preview-artifacts/home-1231-result.png", fullPage: true });
  result.checks.click_to_predict_1231 = "PASS";

  await page.goto(`${baseUrl}/archive.html`, { waitUntil: "networkidle" });
  await page.locator("#data-status.ready").waitFor();
  assert((await page.locator("#summary-count").textContent())?.includes("1,230"), "archive must show 1,230 canonical draws");
  assert((await page.locator("#frequency-grid .frequency-item").count()) === 45, "frequency statistics must contain 45 numbers");
  await page.locator("#draw-search").fill("1230");
  await page.waitForFunction(() => document.querySelectorAll("#draw-list .draw-card").length === 1);
  assert((await page.locator("#draw-list .draw-number").textContent())?.trim() === "1230회", "archive search must find draw 1230");
  await page.screenshot({ path: "preview-artifacts/archive-search.png", fullPage: true });
  result.checks.archive_search_filter_statistics = "PASS";

  await page.goto(`${baseUrl}/update.html`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#draw-no")?.value === "1231");
  const minimumDate = await page.locator("#draw-date").getAttribute("min");
  assert(Boolean(minimumDate), "update form must provide the next valid date");
  await page.locator("#draw-date").fill(minimumDate);
  const numbers = [1, 7, 18, 24, 33, 41];
  const numberInputs = page.locator("[data-winning-number]");
  for (let index = 0; index < numbers.length; index += 1) {
    await numberInputs.nth(index).fill(String(numbers[index]));
  }
  await page.locator("#bonus-number").fill("12");
  await page.locator("#draw-form button[type=submit]").click();
  await page.waitForFunction(() => document.querySelector("#overlay-count")?.textContent?.trim() === "1건");
  assert((await page.locator("#latest-effective").textContent())?.trim() === "1231회", "effective latest draw must become 1231");
  assert((await page.locator("#next-target").textContent())?.trim() === "1232회", "next target must become 1232");
  await page.screenshot({ path: "preview-artifacts/manual-update-1231.png", fullPage: true });
  result.checks.manual_update_overlay = "PASS";

  await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#latest-draw")?.textContent?.trim() === "1231회");
  assert((await page.locator("#target-draw").textContent())?.trim() === "1232회", "home target must advance to 1232");
  await page.locator("#predict-button").click();
  await page.locator("#result-panel:not(.hidden)").waitFor();
  const overlayRows = page.locator("#result-sets .result-row");
  assert((await overlayRows.count()) === 5, "overlay prediction must contain five sets");
  for (let index = 0; index < 5; index += 1) {
    assert((await overlayRows.nth(index).locator(".lotto-ball").count()) === 6, `overlay set ${index + 1} must contain six numbers`);
  }
  const overlaySeed = (await page.locator("#result-seed").textContent())?.trim() || "";
  const overlayHash = (await page.locator("#result-hash").textContent())?.trim() || "";
  assert(/^[0-9a-f]{64}$/.test(overlaySeed), "overlay seed must be a SHA-256 hex string");
  assert(/^[0-9a-f]{64}$/.test(overlayHash), "overlay prediction hash must be a SHA-256 hex string");
  assert(overlaySeed !== initialSeed, "overlay seed must differ from the canonical-only seed");
  assert(overlayHash !== initialHash, "overlay prediction hash must differ from the canonical-only hash");
  await page.screenshot({ path: "preview-artifacts/home-1232-result.png", fullPage: true });
  result.checks.latest_plus_one_and_dynamic_hash = "PASS";

  assert(externalApiCalls.length === 0, `external API calls detected: ${externalApiCalls.join(", ")}`);
  result.checks.external_api_calls = "PASS";
  result.initial_prediction_hash = initialHash;
  result.overlay_prediction_hash = overlayHash;
  result.status = "FULL_PRODUCT_UI_PREVIEW_PASS";
} catch (error) {
  result.status = "FULL_PRODUCT_UI_PREVIEW_FAIL";
  result.error = error instanceof Error ? error.message : String(error);
  await page.screenshot({ path: "preview-artifacts/failure.png", fullPage: true }).catch(() => {});
  throw error;
} finally {
  fs.mkdirSync("preview-artifacts", { recursive: true });
  fs.writeFileSync("preview-artifacts/preview-result.json", `${JSON.stringify(result, null, 2)}\n`);
  await browser.close();
}
