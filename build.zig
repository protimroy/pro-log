const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const site_path = b.path("");
    const out_path = b.path("build");
    const url_prefix = "/pro-log";

    const goku_dep = b.dependency("goku", .{
        .target = target,
        .optimize = optimize,
    });

    const site_step = b.step("site", "Build the site with Goku");
    const build_site = b.addRunArtifact(goku_dep.artifact("goku"));
    build_site.addArg("build");
    build_site.addDirectoryArg(site_path);
    build_site.addArg("-o");
    build_site.addDirectoryArg(out_path);
    build_site.addArg("-p");
    build_site.addArg(url_prefix);
    site_step.dependOn(&build_site.step);

    const serve_step = b.step("serve", "Serve the built Goku site");
    const serve_site = b.addRunArtifact(goku_dep.artifact("goku"));
    serve_site.addArg("preview");
    serve_site.addDirectoryArg(site_path);
    serve_site.addArg("-o");
    serve_site.addDirectoryArg(out_path);
    serve_site.addArg("-p");
    serve_site.addArg(url_prefix);
    serve_site.step.dependOn(&build_site.step);
    serve_step.dependOn(&serve_site.step);
}
