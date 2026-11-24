#!/usr/bin/env python3
"""Audit the built Pro-Log site in Chromium, including light/dark and mobile.

Run preview separately: node scripts/preview-alopex.mjs
uv run --with playwright python scripts/audit_browser.py
uv run --with playwright python -m playwright install chromium
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

PAGES = [
    "", "mechanisms-of-neural-computation/",
    "function-space-programming-thread/", "function-space-programming/",
    "function-space-programming-shared-functions/",
    "function-space-programming-r14-r18/", "function-space-programming-frozen-functions/",
    "alopex-thread/",
    "activation-space-alopex/", "alopex-partial-negative-result/",
]
JS = r"""() => {
  const nodes = [...document.querySelectorAll('body *')];
  const viewport = document.documentElement.clientWidth;
  const wide = nodes.filter(el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' || s.position === 'fixed') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && (r.right > viewport + 2 || r.left < -2);
  }).slice(0, 25).map(el => ({
    tag: el.tagName, className: String(el.className).slice(0, 100),
    text: (el.innerText || '').slice(0, 70),
    right: Math.round(el.getBoundingClientRect().right)
  }));
  const colors = ['body', '.article-shell', '.article-toc', '.research-thread-nav',
    '.research-series-head td', '.paper-section', '.claim', '.in-brief', 'pre', 'table'];
  const samples = {};
  for (const selector of colors) {
    const el = document.querySelector(selector);
    if (!el) continue;
    const s = getComputedStyle(el);
    samples[selector] = { color: s.color, background: s.backgroundColor, width: Math.round(el.getBoundingClientRect().width) };
  }
  const parse = s => {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const a = m[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return a.length >= 3 ? [a[0], a[1], a[2], a[3] ?? 1] : null;
  };
  const blend = (front, back) => front.slice(0, 3).map((v, i) => v * front[3] + back[i] * (1 - front[3]));
  const lum = rgb => {
    const a = rgb.map(v => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
  };
  const background = el => {
    let bg = matchMedia('(prefers-color-scheme: dark)').matches ? [20, 22, 26] : [255, 255, 255];
    const ancestors = [];
    for (let p = el; p; p = p.parentElement) ancestors.unshift(p);
    for (const p of ancestors) {
      const color = parse(getComputedStyle(p).backgroundColor);
      if (color && color[3] > 0) bg = blend(color, bg);
    }
    return bg;
  };
  const contrastSelectors = [
    '.article-content .content', '.article-content .content p',
    '.article-toc a', '.research-thread-nav', '.research-thread-nav a',
    '.paper-section p', '.in-brief p', '.claim p', '.claim strong',
    '.article-content .content a', '.research-series-head .post_title',
    '.post_date'
  ];
  const contrast = [];
  for (const selector of contrastSelectors) {
    const el = document.querySelector(selector);
    if (!el) continue;
    const fg = parse(getComputedStyle(el).color);
    if (!fg) continue;
    const bg = background(el);
    const foreground = blend(fg, bg);
    const l1 = lum(foreground), l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    contrast.push({selector, ratio: Math.round(ratio * 100) / 100,
      fg: getComputedStyle(el).color, bg: bg.map(Math.round)});
  }
  return {
    title: document.title, viewport, documentWidth: document.documentElement.scrollWidth,
    overflow: document.documentElement.scrollWidth > viewport + 2,
    wide, samples, contrast,
    brokenImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src).slice(0, 30),
    missingLinks: [...document.querySelectorAll('a[href]')].filter(a => a.getAttribute('href') === '#').length
  };
}"""
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', default='http://127.0.0.1:8553/pro-log/')
    p.add_argument('--out', default='runs/browser-audit')
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for theme in ('light', 'dark'):
            for width, height in ((390, 844), (768, 1024), (1440, 900)):
                context = browser.new_context(viewport={'width': width, 'height': height}, color_scheme=theme, reduced_motion='reduce')
                for slug in PAGES:
                    page = context.new_page()
                    errors = []
                    bad_responses = []
                    page.on('pageerror', lambda e: errors.append(str(e)))
                    page.on('console', lambda m: errors.append('console: ' + m.text) if m.type == 'error' else None)
                    page.on('response', lambda r: bad_responses.append({'status': r.status, 'url': r.url}) if r.status >= 400 else None)
                    url = args.base.rstrip('/') + '/' + slug
                    try:
                        response = page.goto(url, wait_until='networkidle', timeout=30000)
                        page.evaluate('document.fonts.ready')
                        page.wait_for_timeout(500)
                        snapshot = page.evaluate(JS)
                        name = (slug.strip('/') or 'home').replace('/', '_')
                        screenshot = f'{name}-{theme}-{width}.png'
                        page.screenshot(path=str(out / screenshot), full_page=True, animations='disabled', timeout=30000)
                        results.append({'page': slug or '/', 'theme': theme, 'width': width,
                                        'status': response.status if response else None, 'screenshot': screenshot,
                                        'errors': errors[:30], 'badResponses': bad_responses[:30], **snapshot})
                        print(f'{slug or "/"} {theme} {width}: HTTP {response.status if response else "?"}, overflow={snapshot["overflow"]}, brokenImages={len(snapshot["brokenImages"])}, errors={len(errors)}')
                    except Exception as exc:
                        results.append({'page': slug or '/', 'theme': theme, 'width': width, 'error': str(exc)})
                        print(f'FAIL {url} {theme} {width}: {exc}')
                    finally:
                        page.close()
                context.close()
        browser.close()
    (out / 'report.json').write_text(json.dumps(results, indent=2))
    problems = [r for r in results if r.get('error') or r.get('status') != 200 or r.get('overflow') or r.get('brokenImages') or r.get('errors') or r.get('badResponses') or any(v['ratio'] < 4.5 for v in r.get('contrast', []))]
    print(f'Completed {len(results)} cases; {len(problems)} flagged. Report: {out / "report.json"}')
    if problems:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
