#!/usr/bin/env node
/**
 * Gera o PDF da Etapa 3 a partir do Markdown.
 *
 * Estratégia:
 *  1. Renderiza a capa e o corpo em HTML separados (para a capa ficar sem
 *     cabeçalho/rodapé e o corpo ter numeração de páginas).
 *  2. Usa Chrome headless via puppeteer-core para imprimir os dois PDFs.
 *  3. Junta capa + corpo com pdfunite.
 *
 * Dependências instaladas em /tmp/opencode/docgen:
 *   marked, puppeteer-core.
 */

import { createRequire } from "node:module";
import { mkdir, readFile, writeFile, rm } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { marked } = require("/tmp/opencode/docgen/node_modules/marked");
const puppeteer = require("/tmp/opencode/docgen/node_modules/puppeteer-core");

const ROOT = path.resolve("docs/etapa3");
const MD_PATH = path.join(ROOT, "Etapa3_Implementacao.md");
const HTML_PATH = path.join(ROOT, "Etapa3_Implementacao.html");
const PDF_PATH = path.join(ROOT, "Etapa3_Implementacao.pdf");
const TMP = "/tmp/opencode/oficinapro_pdf_etapa3";

const CHROME = "/usr/bin/google-chrome";

const BODY_CSS = `
@page { size: A4; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  padding: 0;
  font-family: "Segoe UI", "Inter", "Liberation Sans", Arial, sans-serif;
  font-size: 10.2pt;
  line-height: 1.55;
  color: #1E293B;
  background: #FFFFFF;
}
p { margin: 0 0 7px; }
strong { color: #0F172A; }
a { color: #EA580C; text-decoration: none; }
h1, h2, h3, h4, h5, h6 {
  color: #1E293B;
  line-height: 1.25;
  page-break-after: avoid;
  break-after: avoid;
}
h1 {
  font-size: 20pt;
  margin: 0 0 14px;
  padding-bottom: 5px;
  border-bottom: 2.5px solid #F97316;
}
#sumário + ol {
  columns: 2;
  column-gap: 26px;
  margin: 2px 0 10px;
  padding-left: 22px;
  font-size: 9.4pt;
  line-height: 1.4;
}
#sumário + ol li { break-inside: avoid; margin: 0 0 1px; }
h2 {
  font-size: 14pt;
  margin: 18px 0 8px;
}
h3 {
  font-size: 11.6pt;
  margin: 14px 0 6px;
}
h4 {
  font-size: 10.4pt;
  margin: 12px 0 5px;
}
ul { margin: 4px 0 9px 0; padding-left: 20px; }
ol { margin: 4px 0 9px 0; padding-left: 26px; }
li { margin: 2px 0; }
blockquote {
  margin: 9px 0 12px;
  padding: 8px 12px;
  background: #FFF7ED;
  border-left: 4px solid #F97316;
  color: #7C2D12;
  border-radius: 0 5px 5px 0;
}
blockquote p { margin: 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 7px 0 12px;
  font-size: 8.2pt;
  line-height: 1.4;
}
thead { display: table-header-group; }
tr { page-break-inside: avoid; break-inside: avoid; }
th {
  background: #F1F5F9;
  color: #334155;
  font-weight: 700;
  text-align: left;
  border: 1px solid #CBD5E1;
  padding: 4px 5px;
  vertical-align: top;
}
td {
  border: 1px solid #E2E8F0;
  padding: 4px 5px;
  vertical-align: top;
}
tbody tr:nth-child(even) { background: #F8FAFC; }
code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  font-size: 8.4pt;
  background: #F1F5F9;
  padding: 1px 3px;
  border-radius: 3px;
  color: #0F172A;
}
pre {
  background: #0F172A;
  color: #E2E8F0;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 7.7pt;
  line-height: 1.45;
  overflow: hidden;
  white-space: pre-wrap;
  word-break: break-word;
  page-break-inside: auto;
  break-inside: auto;
}
pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}
figure {
  margin: 10px 0 14px;
  text-align: center;
  page-break-inside: avoid;
  break-inside: avoid;
}
figure img {
  max-width: 100%;
  height: auto;
  border: 1px solid #E2E8F0;
  border-radius: 4px;
  background: #FFFFFF;
}
figcaption {
  margin-top: 5px;
  font-size: 8.3pt;
  color: #64748B;
  text-align: center;
}
.figure-narrow img { width: 55%; }
.figure-85 img { width: 85%; }
.figure-90 img { width: 90%; }
.figure-row {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  margin: 10px 0 14px;
  page-break-inside: avoid;
  break-inside: avoid;
}
.figure-row figure { flex: 1; min-width: 0; margin: 0; }
.figure-row figure img { width: 100%; }
.page-break {
  height: 0;
  margin: 0;
  padding: 0;
  page-break-after: always;
  break-after: page;
}
.closing {
  margin-top: 26px;
  padding-top: 14px;
  border-top: 1px solid #E2E8F0;
  text-align: center;
  page-break-inside: avoid;
}
.closing-logo { width: 220px; max-width: 70%; margin-bottom: 8px; }
.closing p { margin: 2px 0; font-size: 9pt; }
.muted { color: #64748B; }
hr { border: 0; border-top: 1px solid #E2E8F0; margin: 14px 0; }
`;

const COVER_CSS = `
@page { size: A4; margin: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  padding: 0;
  font-family: "Segoe UI", "Inter", "Liberation Sans", Arial, sans-serif;
  color: #1E293B;
  background: #FFFFFF;
}
.cover {
  position: relative;
  box-sizing: border-box;
  width: 210mm;
  height: 297mm;
  padding: 30mm 24mm 24mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  background: #FFFFFF;
}
.cover::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 11mm;
  background: linear-gradient(90deg, #1E293B 0 72%, #F97316 72% 100%);
}
.cover::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4mm;
  background: #F97316;
}
.cover-logo { width: 330px; max-width: 82%; margin-bottom: 30px; }
.cover-kicker {
  font-size: 10pt;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: #F97316;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.cover-title {
  font-size: 43pt;
  line-height: 1.05;
  font-weight: 800;
  color: #1E293B;
  margin: 0 0 10px;
  border: 0;
  padding: 0;
}
.cover-title span { color: #F97316; font-size: 23pt; font-weight: 700; }
.cover-subtitle {
  font-size: 24pt;
  line-height: 1.15;
  font-weight: 600;
  color: #334155;
  margin-bottom: 18px;
}
.cover-lead {
  font-size: 12pt;
  line-height: 1.6;
  color: #475569;
  max-width: 150mm;
  margin: 0 0 28px;
}
.cover-meta {
  display: flex;
  gap: 12mm;
  border-top: 1px solid #E2E8F0;
  border-bottom: 1px solid #E2E8F0;
  padding: 12px 0;
  margin-bottom: 22px;
}
.cover-meta div {
  font-size: 10pt;
  color: #475569;
  line-height: 1.5;
}
.cover-meta strong {
  display: block;
  font-size: 8pt;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748B;
  margin-bottom: 2px;
}
.cover-footer {
  font-size: 9pt;
  color: #64748B;
  margin-top: auto;
  padding-top: 18px;
}
`;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/<[^>]+>/g, "")
    .replace(/&[a-z]+;/g, "")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim()
    .replace(/\s+/g, "-");
}

function addHeadingIds(html) {
  const seen = new Map();
  return html.replace(/<h([1-6])>(.*?)<\/h\1>/gs, (match, level, inner) => {
    const base = slugify(inner) || `secao-${level}`;
    const count = seen.get(base) || 0;
    seen.set(base, count + 1);
    const id = count === 0 ? base : `${base}-${count}`;
    return `<h${level} id="${id}">${inner}</h${level}>`;
  });
}

function pageHtml(title, body, css, baseHref = "") {
  const base = baseHref ? `<base href="${baseHref}">` : "";
  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  ${base}
  <title>${title}</title>
  <style>${css}</style>
</head>
<body>
${body}
</body>
</html>`;
}

const headerTemplate = `
<div style="font-family:'Segoe UI',Arial,sans-serif;font-size:7px;color:#94A3B8;width:100%;padding:0 16mm;display:flex;justify-content:space-between;align-items:center;border-bottom:0.5px solid #E2E8F0;padding-bottom:2mm;">
  <span>OficinaPro • Etapa 3 — Implementação do Núcleo</span>
  <span>DevSolo Studio</span>
</div>`;

const footerTemplate = `
<div style="font-family:'Segoe UI',Arial,sans-serif;font-size:7px;color:#94A3B8;width:100%;padding:0 16mm;display:flex;justify-content:space-between;align-items:center;">
  <span>Juan Carlos Matos • 26/10/2026</span>
  <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
</div>`;

async function renderPdf(browser, htmlPath, pdfPath, options) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1240, height: 1754, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle0" });
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
  if (broken.length) {
    console.warn("Imagens com problema:", broken);
  }
  await page.pdf({
    path: pdfPath,
    format: "A4",
    printBackground: true,
    preferCSSPageSize: false,
    ...options,
  });
  await page.close();
}

async function main() {
  await mkdir(TMP, { recursive: true });
  const md = await readFile(MD_PATH, "utf8");

  // Separa a capa do restante do documento no primeiro page-break.
  const marker = '<div class="page-break"></div>';
  const firstBreak = md.indexOf(marker);
  if (firstBreak < 0) throw new Error("Page-break da capa não encontrado.");
  const coverMd = md.slice(0, firstBreak).trim();
  const bodyMd = md.slice(firstBreak + marker.length).trim();

  const coverBody = addHeadingIds(marked.parse(coverMd, { gfm: true, mangle: false }));
  const bodyBody = addHeadingIds(marked.parse(bodyMd, { gfm: true, mangle: false }));

  const baseHref = pathToFileURL(ROOT + path.sep).href;
  const fullHtml = pageHtml(
    "OficinaPro — Etapa 3: Implementação do Núcleo",
    addHeadingIds(marked.parse(md, { gfm: true, mangle: false })),
    BODY_CSS + COVER_CSS
  );
  await writeFile(HTML_PATH, fullHtml, "utf8");

  const coverHtmlPath = path.join(TMP, "capa.html");
  const bodyHtmlPath = path.join(TMP, "corpo.html");
  const coverPdfPath = path.join(TMP, "capa.pdf");
  const bodyPdfPath = path.join(TMP, "corpo.pdf");

  await writeFile(
    coverHtmlPath,
    pageHtml("OficinaPro — Capa", coverBody, COVER_CSS, baseHref),
    "utf8"
  );
  await writeFile(
    bodyHtmlPath,
    pageHtml("OficinaPro — Etapa 3", bodyBody, BODY_CSS, baseHref),
    "utf8"
  );

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
    await renderPdf(browser, coverHtmlPath, coverPdfPath, {
      displayHeaderFooter: false,
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
    });
    await renderPdf(browser, bodyHtmlPath, bodyPdfPath, {
      displayHeaderFooter: true,
      headerTemplate,
      footerTemplate,
      margin: { top: "20mm", right: "16mm", bottom: "18mm", left: "16mm" },
    });
  } finally {
    await browser.close();
  }

  execFileSync("pdfunite", [coverPdfPath, bodyPdfPath, PDF_PATH], {
    stdio: "inherit",
  });

  await rm(coverHtmlPath, { force: true });
  await rm(bodyHtmlPath, { force: true });
  await rm(coverPdfPath, { force: true });
  await rm(bodyPdfPath, { force: true });

  console.log(`PDF gerado: ${PDF_PATH}`);
  console.log(`HTML completo: ${HTML_PATH}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
