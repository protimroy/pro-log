# pro-log

pro-log is a normal Goku consumer site.

This repo is not using the full internal Goku build system. It builds as a regular site that depends on Goku through `build.zig.zon`.

## Requirements

- Zig 0.15.0-dev.885+e83776595

## Build

From this directory:

```sh
/home/protim/Documents/zig-x86_64-linux-0.15.0-dev.885+e83776595/zig build site
```

The generated site is written to `build/`.
The normal site build is standalone: it uses the checked-in article and assets and does not require the ALOPEX repository or Node.js.

## Preview

```sh
/home/protim/Documents/zig-x86_64-linux-0.15.0-dev.885+e83776595/zig build serve
```

Goku's preview serves at the root, while the deployed site at `https://www.protimroy.com/pro-log/` uses `/pro-log`. To preview the built site with its deployment prefix:

```sh
node scripts/preview-alopex.mjs
```

Open `http://127.0.0.1:8553/pro-log/`. Set `PORT` to use another port.

## ALOPEX Article

The native article is generated from the current reader in the sibling `alopex_article` repository. To refresh it, install that repository's Node dependencies and run:

```sh
node scripts/import-alopex.mjs
/home/protim/Documents/zig-x86_64-linux-0.15.0-dev.885+e83776595/zig build site
```

Set `ALOPEX_SOURCE` to the source repository path when it is not at `../alopex_article`. The importer generates the Goku page and its reader component, KaTeX assets, evidence snapshot, archived verification report, and SHA-256 manifest. It also updates fingerprinted asset URLs and bundles the reader component's script, so rerun it after changing the article CSS or JavaScript. The archived report is historical and is not evidence that the experiments were rerun during import.

With the prefix-aware preview running, the browser checks require Playwright and its Chromium browser installed in the source repository's Node environment:

```sh
node scripts/check-alopex.mjs
```

Set `PRO_LOG_URL` to the preview origin if using a different port.

The focused `pages/activation-space-alopex.md` article is authored separately from the generated retrospective. Its Goku component is `components/alopex-family-evidence.js`, and its frozen MNIST statistics snapshot is `assets/alopex/family-frozen-statistics.json`. When updating that snapshot, update its fingerprinted link in the article and the component's displayed values together; the browser checks compare both with the source research records.

## Notes

- `build.zig` uses the same simple consumer pattern as the other site repos.
- Goku is pinned through `build.zig.zon` to `protimroy/goku` on the `v0.1.0-dev` branch.
- CI is expected to use the same Zig compiler version as local development: `0.15.0-dev.885+e83776595`.
- The site template currently uses the `theme` and `component` hooks.

## Cloudflare Web Analytics

All three sites use the same Cloudflare Web Analytics site token for the hostname `www.protimroy.com`, so traffic can be segmented by path (`/`, `/pro-log/`, `/engineering-log/`). Create a Web Analytics site in the Cloudflare dashboard, select **manual JavaScript installation**, and copy its **public site token** (not an API token). If Cloudflare automatically injects a beacon for this domain, disable automatic injection before using this script to prevent double counting.

After each build and before publishing the generated `build/` directory:

```sh
export CLOUDFLARE_WEB_ANALYTICS_TOKEN="YOUR_32_CHARACTER_PUBLIC_SITE_TOKEN"
python3 scripts/inject_cloudflare_analytics.py --site build
python3 scripts/inject_cloudflare_analytics.py --site build --verify
```

The injector updates all generated HTML pages, including articles, is idempotent, and fails if the token is missing or malformed. It must be rerun **after every build**: `zig build site` regenerates `build/`. Do not run it against source templates. The token is public by design, but do not commit Cloudflare API credentials. The beacon is not included in local previews unless you run the injection step.

### Performance and reliability monitoring

Cloudflare Web Analytics provides traffic and browser-reported Core Web Vitals (LCP, INP, CLS), where supported. Use the dashboard's URL/path filtering to compare the three sites and inspect slow pages. It is not a JavaScript exception or custom-event reporting system. Keep the existing Playwright browser checks for navigation, contrast, console errors, failed requests, broken assets, and responsive overflow; add synthetic uptime checks separately if required. Check the browser Network panel for `beacon.min.js` and Cloudflare's telemetry requests after production deployment. Verify no duplicate beacon and no analytics traffic in local preview.

Privacy: do not add personal identifiers, email addresses, query-string secrets, or custom payloads to analytics. Review the site's privacy disclosure and applicable consent requirements before enabling tracking.
