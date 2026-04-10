# pro-log

pro-log is a normal Goku consumer site.

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

- This repo is no longer using the full internal Goku build system.
- `build.zig` is now the same simple consumer pattern used by the other site repos.
- This site is pinned to the `v0.0.9-dev` Goku line.
- The template is wired for the `theme` and `component` hooks supported by the `v0.0.9-dev` line.
