// Render SVG illustrations to PNG at print resolution using headless Chromium.
// Usage: node tools/render.cjs [--dpi 300] [--fonts fonts/] file1.svg [file2.svg ...]
// Output: art/png/<name>.png  (transparent background unless the SVG paints one)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const args = process.argv.slice(2);
  let dpi = 300;
  let outDir = path.join(__dirname, '..', 'art', 'png');
  const files = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--dpi') dpi = parseFloat(args[++i]);
    else if (args[i] === '--out') outDir = args[++i];
    else files.push(args[i]);
  }
  fs.mkdirSync(outDir, { recursive: true });
  const fontDir = path.join(__dirname, '..', 'fonts');
  const fontCss = [
    ['IM Fell English', 'IMFellEnglish-400.ttf', 'normal'],
    ['IM Fell English', 'IMFellEnglish-400i.ttf', 'italic'],
    ['IM Fell English SC', 'IMFellEnglishSC-400.ttf', 'normal'],
    ['IM Fell French Canon', 'IMFellFrenchCanon-400.ttf', 'normal'],
    ['IM Fell French Canon', 'IMFellFrenchCanon-400i.ttf', 'italic'],
    ['EB Garamond', 'EBGaramond-400.ttf', 'normal'],
    ['EB Garamond', 'EBGaramond-400i.ttf', 'italic'],
  ].map(([f, file, st]) => {
    const b64 = fs.readFileSync(path.join(fontDir, file)).toString('base64');
    return `@font-face{font-family:'${f}';font-style:${st};src:url(data:font/ttf;base64,${b64}) format('truetype');}`;
  }).join('\n');

  const browser = await chromium.launch();
  const context = await browser.newContext({ deviceScaleFactor: dpi / 96 });
  const page = await context.newPage();
  for (const f of files) {
    const svg = fs.readFileSync(f, 'utf8');
    const m = svg.match(/width="([\d.]+)in" height="([\d.]+)in"/);
    if (!m) { console.error('no inch size in', f); continue; }
    const w = Math.round(parseFloat(m[1]) * 96), h = Math.round(parseFloat(m[2]) * 96);
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<!doctype html><html><head><style>${fontCss}
      html,body{margin:0;padding:0;background:transparent} svg{display:block;width:${w}px;height:${h}px}</style></head>
      <body>${svg}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    const out = path.join(outDir, path.basename(f).replace(/\.svg$/, '.png'));
    const t0 = Date.now();
    await page.screenshot({ path: out, omitBackground: true, fullPage: false });
    console.log(`${out}  ${Math.round(w * dpi / 96)}x${Math.round(h * dpi / 96)}px  ${Date.now() - t0}ms`);
  }
  await browser.close();
})();
