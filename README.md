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
