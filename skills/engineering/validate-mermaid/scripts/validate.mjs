import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [manifestPath, modulesPath, resultPath] = process.argv.slice(2);
if (!manifestPath || !modulesPath || !resultPath) {
  console.error(
    "usage: validate.mjs <manifest.json> <node_modules> <result.json>",
  );
  process.exit(2);
}

const jsdomUrl = pathToFileURL(path.join(modulesPath, "jsdom", "lib", "api.js"));
const { JSDOM } = await import(jsdomUrl.href);
const mdastUrl = pathToFileURL(
  path.join(modulesPath, "mdast-util-from-markdown", "index.js"),
);
const { fromMarkdown } = await import(mdastUrl.href);
const dedentUrl = pathToFileURL(
  path.join(modulesPath, "ts-dedent", "esm", "index.js"),
);
const { dedent } = await import(dedentUrl.href);

// Mermaid initializes DOMPurify during import, so provide a DOM first even
// when the documents being checked are Markdown or standalone diagrams.
const parserDom = new JSDOM("<!doctype html>");
globalThis.window = parserDom.window;
globalThis.document = parserDom.window.document;

const mermaidUrl = pathToFileURL(
  path.join(modulesPath, "mermaid", "dist", "mermaid.core.mjs"),
);
const { default: mermaid } = await import(mermaidUrl.href);
mermaid.initialize({ startOnLoad: false });

const files = JSON.parse(await fs.readFile(manifestPath, "utf8"));

function isMermaidLanguage(info) {
  const normalized = info.trim().toLowerCase();
  return (
    /^mermaid(?:\s|$)/.test(normalized) ||
    /^\{\s*\.?mermaid(?:\s|,|\})/.test(normalized)
  );
}

function extractMarkdown(source) {
  const tree = fromMarkdown(source);
  const diagrams = [];

  function visit(node) {
    if (
      node.type === "code" &&
      typeof node.lang === "string" &&
      isMermaidLanguage(node.lang)
    ) {
      diagrams.push({
        source: node.value.trim(),
        line: (node.position?.start.line ?? 0) + 1,
      });
    }
    for (const child of node.children ?? []) visit(child);
  }

  visit(tree);
  return diagrams;
}

function entityDecode(document, html) {
  const decoder = document.createElement("div");
  const encoded = escape(html)
    .replace(/%26/g, "&")
    .replace(/%23/g, "#")
    .replace(/%3B/g, ";");
  decoder.innerHTML = encoded;
  return unescape(decoder.textContent);
}

function extractHtml(source) {
  const dom = new JSDOM(source, { includeNodeLocations: true });
  return [...dom.window.document.querySelectorAll(".mermaid")].map((element) => {
    const location = dom.nodeLocation(element);
    const contentOffset = location?.startTag?.endOffset ?? location?.startOffset ?? 0;
    const contentEnd = location?.endTag?.startOffset ?? location?.endOffset ?? contentOffset;
    const rawContent = source.slice(contentOffset, contentEnd);
    const leadingWhitespace = rawContent.match(/^\s*/)?.[0] ?? "";
    const contentLine = (source.slice(0, contentOffset).match(/\n/g) ?? []).length + 1;
    const skippedLines = (leadingWhitespace.match(/\n/g) ?? []).length;
    return {
      source: dedent(entityDecode(dom.window.document, element.innerHTML))
        .trim()
        .replace(/<br\s*\/?>/gi, "<br/>"),
      line: contentLine + skippedLines,
    };
  });
}

function extractDiagrams(file, source) {
  const extension = path.extname(file.path).toLowerCase();
  if (extension === ".mmd" || extension === ".mermaid") {
    return [{ source: source.trim(), line: 1 }];
  }
  if (extension === ".html" || extension === ".htm") {
    return extractHtml(source);
  }
  return extractMarkdown(source);
}

let diagrams = 0;
let failures = 0;
let filesWithDiagrams = 0;

function parserLine(error) {
  const message = error instanceof Error ? error.message : String(error);
  const match = message.match(/\bon line\s+(\d+)\b/i);
  return match ? Number.parseInt(match[1], 10) : null;
}

for (const file of files) {
  let extracted;
  try {
    const source = await fs.readFile(file.path, "utf8");
    extracted = extractDiagrams(file, source);
  } catch (error) {
    failures += 1;
    console.error(`invalid ${file.display}:1`);
    console.error(error instanceof Error ? error.message : String(error));
    continue;
  }

  if (extracted.length > 0) filesWithDiagrams += 1;
  for (const diagram of extracted) {
    diagrams += 1;
    const location = `${file.display}:${diagram.line}`;
    try {
      await mermaid.parse(diagram.source);
      console.log(`ok ${location}`);
    } catch (error) {
      failures += 1;
      const relativeLine = parserLine(error);
      const failureLine = relativeLine
        ? diagram.line + relativeLine - 1
        : diagram.line;
      console.error(`invalid ${file.display}:${failureLine}`);
      console.error(error instanceof Error ? error.message : String(error));
    }
  }
}

await fs.writeFile(
  resultPath,
  JSON.stringify({ diagrams, failures, files: filesWithDiagrams }),
  "utf8",
);
