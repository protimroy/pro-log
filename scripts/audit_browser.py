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
    "", "function-space-programming-thread/", "function-space-programming/",
    "function-space-programming-shared-functions/", "alopex-thread/",
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
  return {
    title: document.title, viewport, documentWidth: document.documentElement.scrollWidth,
    overflow: document.documentElement.scrollWidth > viewport + 2,
    wide, samples,
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
    problems = [r for r in results if r.get('error') or r.get('status') != 200 or r.get('overflow') or r.get('brokenImages') or r.get('errors') or r.get('badResponses')]
    print(f'Completed {len(results)} cases; {len(problems)} flagged. Report: {out / "report.json"}')
    if problems:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
