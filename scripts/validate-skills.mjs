#!/usr/bin/env node

import { readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join, relative } from "node:path";

const repo = new URL("..", import.meta.url).pathname;
const allowedProperties = new Set([
  "name",
  "description",
  "license",
  "allowed-tools",
  "metadata",
]);
const maxSkillNameLength = 64;
const maxDescriptionLength = 1024;

function findSkillDirs(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    if (entry === "node_modules" || entry === ".git") continue;
    const path = join(dir, entry);
    if (!statSync(path).isDirectory()) continue;
    const skillPath = join(path, "SKILL.md");
    try {
      if (statSync(skillPath).isFile()) out.push(path);
    } catch {
      findSkillDirs(path, out);
    }
  }
  return out;
}

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return null;

  const frontmatter = {};
  for (const line of match[1].split(/\r?\n/)) {
    if (!line.trim() || line.trimStart().startsWith("#")) continue;
    if (/^\s/.test(line)) continue;

    const keyMatch = line.match(/^([A-Za-z0-9_-]+):(?:\s*(.*))?$/);
    if (!keyMatch) {
      return { error: `Invalid frontmatter line: ${line}` };
    }

    let value = keyMatch[2] ?? "";
    value = value.trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    frontmatter[keyMatch[1]] = value;
  }

  return { frontmatter };
}

function validateSkill(skillDir) {
  const skillMd = join(skillDir, "SKILL.md");
  let content;
  try {
    content = readFileSync(skillMd, "utf8");
  } catch {
    return ["SKILL.md not found"];
  }

  if (!content.startsWith("---")) return ["No YAML frontmatter found"];

  const parsed = parseFrontmatter(content);
  if (!parsed) return ["Invalid frontmatter format"];
  if (parsed.error) return [parsed.error];

  const frontmatter = parsed.frontmatter;
  const errors = [];

  for (const key of Object.keys(frontmatter)) {
    if (!allowedProperties.has(key)) {
      errors.push(
        `Unexpected key '${key}'. Allowed properties: ${[
          ...allowedProperties,
        ]
          .sort()
          .join(", ")}`,
      );
    }
  }

  if (!("name" in frontmatter)) errors.push("Missing 'name' in frontmatter");
  if (!("description" in frontmatter)) {
    errors.push("Missing 'description' in frontmatter");
  }

  const name = (frontmatter.name ?? "").trim();
  if (name) {
    if (!/^[a-z0-9-]+$/.test(name)) {
      errors.push(
        `Name '${name}' should be hyphen-case: lowercase letters, digits, and hyphens only`,
      );
    }
    if (name.startsWith("-") || name.endsWith("-") || name.includes("--")) {
      errors.push(
        `Name '${name}' cannot start/end with hyphen or contain consecutive hyphens`,
      );
    }
    if (name.length > maxSkillNameLength) {
      errors.push(
        `Name '${name}' is too long (${name.length}); maximum is ${maxSkillNameLength}`,
      );
    }
    if (basename(skillDir) !== name) {
      errors.push(
        `Skill folder '${basename(skillDir)}' must match frontmatter name '${name}'`,
      );
    }
  }

  const description = (frontmatter.description ?? "").trim();
  if (description) {
    if (description.includes("<") || description.includes(">")) {
      errors.push("Description cannot contain angle brackets (< or >)");
    }
    if (description.length > maxDescriptionLength) {
      errors.push(
        `Description is too long (${description.length}); maximum is ${maxDescriptionLength}`,
      );
    }
  }

  return errors;
}

const skillDirs =
  process.argv.length > 2
    ? process.argv.slice(2)
    : findSkillDirs(join(repo, "skills")).sort();

let failed = false;
for (const skillDir of skillDirs) {
  const errors = validateSkill(skillDir);
  const label = relative(repo, skillDir);
  if (errors.length === 0) {
    console.log(`ok ${label}`);
    continue;
  }
  failed = true;
  console.error(`fail ${label}`);
  for (const error of errors) console.error(`  - ${error}`);
}

process.exit(failed ? 1 : 0);
