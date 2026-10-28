#!/usr/bin/env node
/**
 * Gera os slides da apresentação final a partir de Slides_Apresentacao.md.
 *
 * Estratégia:
 *  - cada bloco separado por <!-- SLIDE --> já contém o markup de um slide;
 *  - o HTML final serve para tela e para impressão;
 *  - o Chrome headless imprime em 16:9 (13,333 × 7,5 in), sem margens.
 *
 * Dependência instalada em /tmp/opencode/docgen:
 *   puppeteer-core.
 */

import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);

function loadModule(name) {
  for (const candidate of [name, `/tmp/opencode/docgen/node_modules/${name}`]) {
    try {
      return require(candidate);
    } catch (error) {
      if (error.code !== "MODULE_NOT_FOUND") throw error;
    }
  }
  throw new Error(
    `Dependência "${name}" não encontrada. Execute "npm install" em docs/final/ferramentas.`
  );
}

const puppeteer = loadModule("puppeteer-core");

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(SCRIPT_DIR, "..");
const MD_PATH = path.join(ROOT, "Slides_Apresentacao.md");
const HTML_PATH = path.join(ROOT, "Slides_Apresentacao.html");
const PDF_PATH = path.join(ROOT, "Slides_Apresentacao.pdf");
const TMP = "/tmp/opencode/oficinapro_slides";
const CHROME = "/usr/bin/google-chrome";

const CSS = `
@page { size: 13.333in 7.5in; margin: 0; }
:root {
  --ink: #0F172A;
  --muted: #64748B;
  --line: #E2E8F0;
  --orange: #F97316;
  --soft: #F8FAFC;
}
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body {
  margin: 0;
  padding: 0;
  font-family: "Segoe UI", "Inter", "Liberation Sans", Arial, sans-serif;
  color: var(--ink);
  background: #0F172A;
}
body {
  padding: 28px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}
.slide {
  width: 1280px;
  height: 720px;
  background: var(--soft);
  position: relative;
  overflow: hidden;
  padding: 54px 64px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  page-break-after: always;
  break-after: page;
}
.slide:last-child { page-break-after: auto; break-after: auto; }
.slide-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.kicker {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--orange);
}
.slide-no { font-size: 12px; color: #94A3B8; font-weight: 700; }
.slide-title {
  font-size: 44px;
  line-height: 1.08;
  letter-spacing: -0.03em;
  margin: 0 0 24px;
  color: var(--ink);
}
.slide-title span { color: var(--orange); }
h3 { font-size: 16px; line-height: 1.25; margin: 0 0 8px; color: var(--ink); }
p { font-size: 15px; line-height: 1.55; margin: 0 0 9px; color: #334155; }
ul { margin: 0; padding-left: 20px; }
li { font-size: 15px; line-height: 1.55; margin: 4px 0; color: #334155; }
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 12.5px;
  background: #F1F5F9;
  padding: 2px 5px;
  border-radius: 4px;
  color: #0F172A;
}
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.grid-62-38 { display: grid; grid-template-columns: 62% 1fr; gap: 26px; align-items: start; }
.grid-58-42 { display: grid; grid-template-columns: 58% 1fr; gap: 26px; align-items: start; }
.grid-55-45 { display: grid; grid-template-columns: 55% 1fr; gap: 26px; align-items: start; }
.grid-38-62 { display: grid; grid-template-columns: 38% 1fr; gap: 28px; align-items: start; }
.card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 19px 21px;
}
.accent-card { border-top: 4px solid var(--orange); }
.quote {
  margin-top: 22px;
  padding: 15px 20px;
  border-left: 5px solid var(--orange);
  background: #FFF7ED;
  color: #7C2D12;
  font-size: 17px;
  font-weight: 600;
  line-height: 1.45;
  border-radius: 0 10px 10px 0;
}
.slide-footer {
  position: absolute;
  left: 64px;
  right: 64px;
  bottom: 20px;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #94A3B8;
  border-top: 1px solid var(--line);
  padding-top: 9px;
}
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}
.metric {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px 19px;
}
.metric strong {
  display: block;
  font-size: 42px;
  line-height: 1;
  color: var(--orange);
  letter-spacing: -0.04em;
}
.metric span { font-size: 12px; color: var(--muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; }
.small-metrics .metric strong { font-size: 34px; }
.mini-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 16px 18px;
}
.mini-card p { font-size: 13px; margin: 0; }
.shot-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 9px;
}
.shot-card img {
  width: 100%;
  display: block;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  background: #F8FAFC;
}
.shots .shot-card img { height: 340px; object-fit: contain; object-position: top center; }
.dashboard img { height: 380px; object-fit: contain; object-position: top center; }
.portrait img { max-height: 480px; width: auto; max-width: 100%; margin: 0 auto; }
.caption { font-size: 11px; color: var(--muted); margin: 8px 2px 0; line-height: 1.4; }
.stack { display: flex; flex-direction: column; gap: 13px; }
.stat-line {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 13px 16px;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.stat-line strong { font-size: 24px; color: var(--orange); letter-spacing: -0.02em; }
.stat-line span { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }
.small { font-size: 13px !important; color: var(--muted) !important; }
.pill-row { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 18px; }
.pill {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 8px 13px;
  font-size: 12px;
  color: #334155;
}
.flow { display: flex; align-items: center; gap: 9px; margin-top: 18px; flex-wrap: wrap; }
.flow-step {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px 13px;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}
.flow-step.done { background: #ECFDF5; border-color: #A7F3D0; color: #047857; }
.arrow { color: #94A3B8; font-weight: 700; }
.flow-cancel {
  margin-left: auto;
  color: #B91C1C;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
}
.clean-table {
  width: 100%;
  border-collapse: collapse;
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
}
.clean-table th {
  background: #F1F5F9;
  font-size: 12px;
  text-align: left;
  padding: 10px 12px;
  color: #475569;
}
.clean-table td {
  font-size: 12px;
  padding: 8px 12px;
  border-top: 1px solid #E2E8F0;
  color: #334155;
}
.code-card { background: #0F172A; border-radius: 12px; padding: 15px 17px; }
.code-card pre {
  margin: 0;
  color: #E2E8F0;
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 12.5px;
  line-height: 1.7;
  white-space: pre-wrap;
}
.check-list { list-style: none; padding-left: 0; }
.check-list li::before { content: "✓"; color: #059669; font-weight: 800; margin-right: 8px; }
.demo-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 13px; margin-top: 16px; }
.demo-step {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 17px 15px;
  min-height: 188px;
}
.demo-step span { font-size: 11px; font-weight: 800; color: var(--orange); letter-spacing: 0.12em; }
.demo-step h3 { font-size: 15px; margin: 14px 0 6px; }
.demo-step p { font-size: 13px; color: var(--muted); }

/* Capa */
.cover {
  padding: 0;
  background:
    radial-gradient(circle at 88% 18%, #FFEDD5 0, rgba(255, 237, 213, 0) 34%),
    radial-gradient(circle at 92% 78%, #E2E8F0 0, rgba(226, 232, 240, 0) 28%),
    #F8FAFC;
}
.cover::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 13px;
  background: linear-gradient(90deg, #0F172A 0 72%, #F97316 72% 100%);
}
.cover::after {
  content: "";
  position: absolute;
  right: -120px;
  bottom: -180px;
  width: 520px;
  height: 520px;
  border: 46px solid #F97316;
  border-radius: 50%;
  opacity: 0.16;
}
.cover-logo { position: absolute; top: 48px; left: 64px; width: 280px; }
.cover-logo img { width: 100%; display: block; }
.cover-main { position: absolute; left: 64px; top: 178px; width: 780px; }
.cover h1 {
  font-size: 82px;
  line-height: 1.02;
  letter-spacing: -0.055em;
  margin: 0 0 10px;
  color: var(--ink);
}
.cover h1 span { color: var(--orange); font-size: 42px; letter-spacing: -0.02em; }
.cover-sub { font-size: 29px; font-weight: 600; color: #334155; margin: 0 0 16px; }
.cover-lead { font-size: 18px; line-height: 1.55; color: #475569; max-width: 700px; }
.cover-meta {
  position: absolute;
  left: 64px;
  bottom: 105px;
  display: flex;
  gap: 48px;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 14px 0;
  width: 760px;
}
.cover-meta div { font-size: 13px; line-height: 1.5; color: #475569; }
.cover-meta strong {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #64748B;
  margin-bottom: 2px;
}
.cover-footer { position: absolute; left: 64px; bottom: 34px; font-size: 12px; color: #64748B; }

/* Fechamento */
.dark { background: #0F172A; color: #F8FAFC; }
.closing::after {
  content: "v1.0";
  position: absolute;
  right: 48px;
  top: 190px;
  font-size: 190px;
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.08em;
  color: rgba(249, 115, 22, 0.10);
  pointer-events: none;
}
.dark .kicker { color: #FB923C; }
.dark .slide-no { color: #64748B; }
.dark .slide-footer { border-color: #334155; color: #64748B; }
.closing-title {
  font-size: 62px;
  line-height: 1.04;
  letter-spacing: -0.045em;
  margin: 20px 0 0;
  color: #F8FAFC;
}
.closing-title span { color: #FB923C; }
.closing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-top: 32px;
  width: 900px;
}
.closing-grid div {
  background: #1E293B;
  border: 1px solid #334155;
  border-radius: 14px;
  padding: 18px 20px;
}
.closing-grid strong {
  display: block;
  color: #FB923C;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 6px;
}
.closing-grid p { color: #CBD5E1; font-size: 14px; margin: 0; }
.thanks { margin-top: 36px; font-size: 29px; font-weight: 800; line-height: 1.25; color: #F8FAFC; }
.thanks span { color: #FB923C; }

@media print {
  html, body { background: #FFFFFF; }
  body { padding: 0; display: block; }
  .slide { margin: 0; box-shadow: none; }
}
`;

async function main() {
  await mkdir(TMP, { recursive: true });
  const md = await readFile(MD_PATH, "utf8");
  const slides = md
    .split("<!-- SLIDE -->")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!slides.length) throw new Error("Nenhum slide encontrado.");

  const baseHref = pathToFileURL(ROOT + path.sep).href;
  const html = `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="${baseHref}">
  <title>OficinaPro v1.0 — Apresentação Final</title>
  <style>${CSS}</style>
</head>
<body>
${slides.join("\n")}
</body>
</html>`;
  await writeFile(HTML_PATH, html, "utf8");

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--font-render-hinting=none",
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720, deviceScaleFactor: 1 });
    await page.goto(pathToFileURL(HTML_PATH).href, { waitUntil: "networkidle0" });
    await page.emulateMediaType("print");
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
      await Promise.all(
        Array.from(document.images).map((img) =>
          img.complete
            ? Promise.resolve()
            : new Promise((resolve) => {
                img.onload = resolve;
                img.onerror = resolve;
              })
        )
      );
    });
    const broken = await page.evaluate(() =>
      Array.from(document.images)
        .filter((img) => !img.complete || img.naturalWidth === 0)
        .map((img) => img.getAttribute("src"))
    );
    if (broken.length) console.warn("Imagens com problema:", broken);
    await page.pdf({
      path: PDF_PATH,
      width: "13.333in",
      height: "7.5in",
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
    });
    await page.close();
  } finally {
    await browser.close();
  }

  console.log(`Slides gerados: ${PDF_PATH}`);
  console.log(`HTML completo: ${HTML_PATH}`);
  console.log(`Total de slides: ${slides.length}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
