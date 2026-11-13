/**
 * Remark plugin that inlines the benchmark plots on the Starlight docs site.
 *
 * benchmarks/harness/render_guidance.py draws each benchmark's plot as an SVG under
 * images/benchmark-guidance/ and links it from docs/benchmark-guidance/*.md as an
 * ordinary Markdown image, which GitHub renders as a picture. An SVG loaded through
 * <img> cannot see the page, so it can follow the reader's system color scheme but
 * not the site's theme toggle. This plugin replaces each such image with the SVG
 * itself, so the plot's own `:root[data-theme="dark"]` rule follows the toggle.
 *
 * Only images under images/benchmark-guidance/ are touched; every other image is
 * left to Astro. A missing file leaves the image node as it was.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { visit } from "unist-util-visit";

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
const PLOT_PATH = /(?:^|\/)images\/benchmark-guidance\/([\w.-]+\.svg)$/;

export default function remarkInlineBenchmarkPlots() {
  return (tree) => {
    visit(tree, "image", (node, index, parent) => {
      const match = PLOT_PATH.exec(node.url || "");
      if (!match || !parent || index === undefined) return;
      const file = join(PROJECT_ROOT, "images", "benchmark-guidance", match[1]);
      if (!existsSync(file)) return;
      const svg = readFileSync(file, "utf-8").replace(
        "<svg ",
        `<svg aria-label="${(node.alt || "").replace(/"/g, "&quot;")}" `,
      );
      parent.children[index] = { type: "html", value: svg };
    });
  };
}
