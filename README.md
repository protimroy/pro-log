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

## Preview

```sh
/home/protim/Documents/zig-x86_64-linux-0.15.0-dev.885+e83776595/zig build serve
```

## Notes

- `build.zig` uses the same simple consumer pattern as the other site repos.
- Goku is pinned through `build.zig.zon` to `protimroy/goku` on the `v0.1.0-dev` branch.
- CI is expected to use the same Zig compiler version as local development: `0.15.0-dev.885+e83776595`.
- The site template currently uses the `theme` and `component` hooks.


## ALOPEX microsite

The ALOPEX research publication is mounted at:

```text
/pro-log/alopex/
```

The deploy workflow builds the private `protimroy/alopex_article` repository as a Vite microsite with base path `/pro-log/alopex/`, then copies the generated `dist/` tree into Pro Log's `build/alopex/` before GitHub Pages publication.

The deployment is pinned to ALOPEX commit:

```text
311fe2c6753b6ae5641cbb728e8fff30c96da35a
```

This pin keeps publication reproducible. Update `ALOPEX_REF` in `.github/workflows/build-and-publish.yml` when a reviewed ALOPEX release should be published.

Because `alopex_article` is private, the Pro Log repository needs an `ALOPEX_REPO_TOKEN` Actions secret with read-only Contents access to `protimroy/alopex_article`. The normal repository `GITHUB_TOKEN` remains responsible only for publishing Pro Log's `gh-pages` branch.
