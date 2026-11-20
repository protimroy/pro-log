import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const source = resolve(process.env.ALOPEX_SOURCE || '../alopex_article');
const require = createRequire(`${source}/package.json`);
const { chromium } = require('playwright');
const base = process.env.PRO_LOG_URL || 'http://127.0.0.1:8553';
const path = '/pro-log/alopex-partial-negative-result/';
const frozen = JSON.parse(await readFile(resolve(source, 'public/results/statistics.json'), 'utf8'));
const { chapterCloseEvidence } = await import(pathToFileURL(resolve(source, 'src/data/chapterCloseEvidence.js')).href);
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 390, 1024, 1600]) {
    for (const javascriptEnabled of [false, true]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, javaScriptEnabled: javascriptEnabled, reducedMotion: 'reduce' });
      const page = await context.newPage();
      const failures = [];
      page.on('pageerror', error => failures.push(error.message));
      page.on('response', response => {
        if (response.url().startsWith(base) && response.status() >= 400) failures.push(`${response.status()} ${response.url()}`);
      });
      const response = await page.goto(`${base}${path}`, { waitUntil: 'load' });
      assert.equal(response.status(), 200);
      assert.equal(await page.locator('.paper-section').count(), 12);
      assert.equal(await page.locator('.equation-list > li').count(), 38);
      assert.equal(await page.locator('.reference-main').count(), 72);
      assert.equal(await page.locator('.interactive-data').count(), 6);
      assert.equal(await page.locator('.interactive-figure .alopex-native').count(), 1);
      assert.equal(await page.locator('script[src*="/component.js"]').count(), 1);
      assert.equal(await page.locator('script[src*="/assets/alopex/article-"]').count(), 0);
      assert.equal(await page.locator('.article-topbar a[href="/pro-log/"]').count(), 1);
      assert.equal(await page.locator('.interactive-data.is-ready').count(), javascriptEnabled ? 6 : 0);
      assert.ok(await page.locator('.citation-return').count() > 0);
      assert.equal(await page.locator('.interactive-data thead button:disabled').count(), javascriptEnabled ? 0 : await page.locator('.interactive-data thead button').count());
      assert.equal(await page.locator('.article-meta:visible').count(), 0);
      assert.match(await page.locator('.alopex-source-note').textContent(), /schema-v2 campaign remains staging/);
      if (javascriptEnabled && width < 701) assert.equal(await page.locator('.article-toc details').getAttribute('open'), null);
      if (!javascriptEnabled) assert.ok(await page.locator('.article-toc a:visible').count() > 0);
      const missingAnchors = await page.locator('a[href^="#"]').evaluateAll(anchors => anchors.map(anchor => anchor.getAttribute('href')).filter(href => href.length > 1 && !document.getElementById(decodeURIComponent(href.slice(1)))));
      assert.deepEqual(missingAnchors, []);
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      assert.ok(overflow <= 1, `Page overflows at ${width}px by ${overflow}px`);
      if (javascriptEnabled) {
        const table = page.locator('.interactive-data').nth(1);
        await table.locator('input').fill('d32');
        assert.equal(await table.locator('tbody tr:visible').count(), 2);
        await table.getByRole('button', { name: 'Chart', exact: true }).click();
        assert.equal(await table.locator('.alopex-chart svg rect').count(), 4);
        await table.getByRole('button', { name: 'Table', exact: true }).click();
        await table.locator('input').fill('');
        const heading = table.locator('thead th').nth(3);
        await heading.locator('button').click();
        assert.equal(await heading.getAttribute('aria-sort'), 'ascending');
        const bibliography = page.locator('.bibliography-browser');
        await bibliography.locator('input').fill('Adam');
        assert.ok(await bibliography.locator('.references-list > li:visible').count() > 0);
        assert.ok(await bibliography.locator('.references-list > li:visible').count() < 72);
        const point = page.locator('.scale-point[data-scale]').first();
        const item = JSON.parse(await point.getAttribute('data-scale'));
        await point.focus();
        await page.keyboard.press('Enter');
        assert.equal(await point.getAttribute('aria-pressed'), 'true');
        assert.equal(await page.locator('.scale-selected strong').first().textContent(), item.label);
      }
      assert.deepEqual(failures, []);
      const familyResponse = await page.goto(`${base}/pro-log/activation-space-alopex/`, { waitUntil: 'load' });
      assert.equal(familyResponse.status(), 200);
      assert.equal(await page.locator('.family-cohort:visible').count(), 3);
      assert.equal(await page.locator('.family-evidence-control:visible').count(), javascriptEnabled ? 1 : 0);
      const meters = await page.locator('.family-cohort meter').evaluateAll(elements => elements.map(element => Number(element.value)));
      assert.deepEqual(meters, [
        frozen.summary.v43.adamw.best_acc * 100,
        frozen.summary.v43.v43_hybrid.best_acc * 100,
        frozen.summary.v43.v43_full.best_acc * 100,
        chapterCloseEvidence.calibration.values[2].mean,
        chapterCloseEvidence.calibration.values[3].mean,
        chapterCloseEvidence.calibration.values[0].mean,
        chapterCloseEvidence.calibration.values[1].mean,
        chapterCloseEvidence.canonical.hfd.mean,
        chapterCloseEvidence.canonical.adamw.mean,
      ]);
      if (javascriptEnabled) {
        await page.getByLabel('Experiment cohort').selectOption('pilot');
        assert.equal(await page.locator('.family-cohort:visible').count(), 1);
        assert.equal(await page.locator('.family-cohort:visible').getAttribute('data-cohort'), 'pilot');
        await page.getByLabel('Experiment cohort').selectOption('all');
        assert.equal(await page.locator('.family-cohort:visible').count(), 3);
        if (width < 701) assert.equal(await page.locator('.article-toc details').getAttribute('open'), null);
      }
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth) <= 1, `Family article overflows at ${width}px`);
      assert.deepEqual(failures, []);
      console.log(`${width}px, JavaScript ${javascriptEnabled ? 'on' : 'off'}: passed`);
      await context.close();
    }
  }
  const page = await browser.newPage();
  await page.goto(`${base}/pro-log/`);
  assert.equal(await page.getByRole('link', { name: 'ALOPEX: A Partial Negative Result' }).count(), 1);
  assert.equal(await page.getByRole('link', { name: 'Activation-space learning and the ALOPEX family experiments' }).count(), 1);
  await page.goto(`${base}/pro-log/activation-space-alopex/`);
  const statisticsLink = await page.getByRole('link', { name: 'Frozen MNIST and parameter-JVP statistics' }).getAttribute('href');
  const statisticsResponse = await page.request.get(`${base}${statisticsLink}`);
  assert.equal(statisticsResponse.status(), 200);
  assert.deepEqual(await statisticsResponse.json(), frozen);
  const broaderLink = await page.getByRole('link', { name: 'ALOPEX: A Partial Negative Result' }).getAttribute('href');
  assert.equal((await page.request.get(`${base}${broaderLink}`)).status(), 200);
  assert.equal(await page.locator('.alopex-native').count(), 0);
  assert.equal(await page.locator('.article-topbar a[href="/pro-log/"]').count(), 1);
  const sampleResponse = await page.goto(`${base}/pro-log/sample-research-article/`);
  if (sampleResponse.status() === 200) {
    assert.equal(await page.locator('.rp-root').count(), 1);
    assert.equal(await page.locator('.alopex-native').count(), 0);
  }
  await page.goto(`${base}${path}`);
  const evidenceLink = await page.getByRole('link', { name: 'Reader evidence data' }).getAttribute('href');
  const reportLink = await page.getByRole('link', { name: 'Archived verification report' }).getAttribute('href');
  const evidenceResponse = await page.request.get(`${base}${evidenceLink}`);
  assert.equal(evidenceResponse.status(), 200);
  const evidence = await evidenceResponse.json();
  assert.equal(evidence.status, 'reader-replay-not-independent-reproduction');
  assert.ok(evidence.scientificEvidence && evidence.chapterCloseEvidence && evidence.scaleMilestones);
  assert.equal((await page.request.get(`${base}${reportLink}`)).status(), 200);
  console.log('Navigation and evidence downloads: passed');
  await page.close();
} finally {
  await browser.close();
}