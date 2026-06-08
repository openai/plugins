#!/usr/bin/env node

/**
 * WDS Documentation Helper
 *
 * Auto-discovers @wix/design-system in node_modules and provides
 * fast, focused lookups for components, props, examples, and icons.
 *
 * Usage:
 *   node <path-to>/wds.cjs search <keyword>
 *   node <path-to>/wds.cjs component <Name>
 *   node <path-to>/wds.cjs components <Name1> <Name2>...
 *   node <path-to>/wds.cjs example <Name> <ExampleName>
 *   node <path-to>/wds.cjs testkit <Name> [method]
 *   node <path-to>/wds.cjs icons <query>
 */

const fs = require("fs");
const path = require("path");

// ---------------------------------------------------------------------------
// Path discovery
// ---------------------------------------------------------------------------

function tryEnablePnp() {
  // Yarn Berry PnP projects have no node_modules. Walk up from cwd looking for
  // .pnp.cjs and activate it so require.resolve can see PnP-managed packages.
  let dir = process.cwd();
  while (true) {
    const pnp = path.join(dir, ".pnp.cjs");
    if (fs.existsSync(pnp)) {
      try {
        require(pnp).setup();
      } catch {
        // ignore — fall through to other discovery paths
      }
      return;
    }
    const parent = path.dirname(dir);
    if (parent === dir) return;
    dir = parent;
  }
}

function findDocsDir() {
  tryEnablePnp();

  // Primary: use Node's module resolver (handles symlinks, pnpm, yarn PnP, etc.)
  try {
    const pkgPath = require.resolve("@wix/design-system/package.json", {
      paths: [process.cwd()],
    });
    const docsDir = path.join(path.dirname(pkgPath), "dist", "docs");
    if (fs.existsSync(docsDir)) return docsDir;
  } catch {
    // resolve failed — fall through to filesystem scan
  }

  // Fallback: walk up from cwd looking for node_modules
  let dir = process.cwd();
  while (true) {
    const candidate = path.join(
      dir,
      "node_modules",
      "@wix",
      "design-system",
      "dist",
      "docs"
    );
    if (fs.existsSync(candidate)) return candidate;

    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }

  return null;
}

function readFile(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildTermsPattern(args) {
  // Tolerate both `search foo bar` (separate args) and `search "foo bar"`
  // (single quoted arg). Without the split, a single quoted string becomes a
  // literal-phrase match instead of OR-of-words and silently returns nothing.
  return args
    .flatMap((a) => a.split(/\s+/))
    .filter(Boolean)
    .map(escapeRegex)
    .join("|");
}

function validateComponentName(name) {
  if (!/^[A-Za-z0-9]+$/.test(name)) {
    console.error(
      `Invalid component name "${name}". Names may only contain letters and digits.`
    );
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

function cmdSearch(docsDir, terms) {
  if (terms.length === 0) {
    console.error("Usage: wds.cjs search <keyword> [keyword...]");
    console.error('Example: wds.cjs search form input validation');
    process.exit(1);
  }

  const content = readFile(path.join(docsDir, "components.md"));
  if (!content) {
    console.error("Error: components.md not found");
    process.exit(1);
  }

  const regex = new RegExp(buildTermsPattern(terms), "i");
  const sections = content.split(/^\s*### /m).slice(1);
  const matches = [];

  for (const section of sections) {
    if (regex.test(section)) {
      const lines = section.split("\n");
      const name = lines[0].trim();
      const descLine = lines.find((l) => l.trimStart().startsWith("- description:"));
      const desc = descLine ? descLine.replace(/.*- description:/, "").trim() : "";
      const doLine = lines.find((l) => l.trimStart().startsWith("- do:"));
      const doText = doLine ? doLine.replace(/.*- do:/, "").trim() : "";
      const dontLine = lines.find((l) => l.trimStart().startsWith("- donts:"));
      const dontText = dontLine ? dontLine.replace(/.*- donts:/, "").trim() : "";
      matches.push({ name, description: desc, do: doText, donts: dontText });
    }
  }

  if (matches.length === 0) {
    console.log(`No components found matching "${terms.join(" ")}".`);
    return;
  }

  console.log(`Found ${matches.length} component(s):\n`);
  for (const r of matches) {
    console.log(`### ${r.name}`);
    if (r.description) console.log(`  ${r.description}`);
    if (r.do) console.log(`  Do: ${r.do}`);
    if (r.donts) console.log(`  Don't: ${r.donts}`);
    console.log();
  }
}

// Renders one component's props + examples list. Returns true on success,
// false if the component wasn't found (so batch callers can keep going).
function printComponent(docsDir, componentName) {
  validateComponentName(componentName);

  const componentsDir = path.join(docsDir, "components");

  // --- Props ---
  const propsPath = path.join(componentsDir, `${componentName}Props.md`);
  const propsContent = readFile(propsPath);

  if (!propsContent) {
    console.error(
      `Component "${componentName}" not found. Run: wds.cjs search <keyword>`
    );
    return false;
  }

  const propsLines = propsContent.split("\n");
  const propsLineCount = propsLines.length;

  console.log(`## ${componentName} Props (${propsLineCount} lines)\n`);

  if (propsLineCount <= 200) {
    // Small file — include full props
    console.log(propsContent);
  } else {
    // Large file — summarize prop names and types only
    console.log(
      `(Large props file — showing summary. Use grep for specific prop details.)\n`
    );
    for (const line of propsLines) {
      if (line.startsWith("### ")) {
        const propName = line.replace("### ", "").trim();
        // Find the type line (next line starting with "- type:")
        const idx = propsLines.indexOf(line);
        const typeLine = propsLines[idx + 1];
        const type =
          typeLine && typeLine.startsWith("- type:")
            ? typeLine.replace("- type:", "").trim()
            : "";
        console.log(`  ${propName}: ${type}`);
      }
    }
  }

  // --- Examples list ---
  const examplesPath = path.join(componentsDir, `${componentName}Examples.md`);
  const examplesContent = readFile(examplesPath);

  if (examplesContent) {
    const exLines = examplesContent.split("\n");
    const examples = [];
    for (let i = 0; i < exLines.length; i++) {
      if (exLines[i].startsWith("### ")) {
        examples.push(exLines[i].replace("### ", "").trim());
      }
    }

    if (examples.length > 0) {
      console.log(`\n## Available Examples (${examples.length})\n`);
      for (const ex of examples) {
        console.log(`  - ${ex}`);
      }
      console.log(
        `\nGet an example: wds.cjs example ${componentName} "<ExampleName>"`
      );
    }
  }

  return true;
}

function cmdComponent(docsDir, componentName) {
  if (!componentName) {
    console.error("Usage: wds.cjs component <ComponentName>");
    console.error("Example: wds.cjs component Button");
    process.exit(1);
  }
  if (!printComponent(docsDir, componentName)) {
    process.exit(1);
  }
}

// Cheap pre-check so cmdComponents can decide whether to emit a `---`
// separator before invoking the actual renderer. Avoids stale separators
// when a middle component is missing.
function componentExists(docsDir, componentName) {
  if (!/^[A-Za-z0-9]+$/.test(componentName)) return false;
  return fs.existsSync(
    path.join(docsDir, "components", `${componentName}Props.md`)
  );
}

function cmdComponents(docsDir, args) {
  // Accept either `components Button Card` or `components "Button Card"`.
  const names = args.flatMap((a) => a.split(/\s+/)).filter(Boolean);

  if (names.length === 0) {
    console.error("Usage: wds.cjs components <Name1> [Name2] [Name3]...");
    console.error("Example: wds.cjs components Button Card Table");
    process.exit(1);
  }

  let printedAny = false;
  let anyFailed = false;
  for (const name of names) {
    // Match the single-component flow: invalid names get a distinct error
    // instead of being lumped under "not found".
    if (!/^[A-Za-z0-9]+$/.test(name)) {
      console.error(
        `Invalid component name "${name}". Names may only contain letters and digits.`
      );
      anyFailed = true;
      continue;
    }
    if (!componentExists(docsDir, name)) {
      console.error(
        `Component "${name}" not found. Run: wds.cjs search <keyword>`
      );
      anyFailed = true;
      continue;
    }
    if (printedAny) console.log("\n---\n");
    printComponent(docsDir, name);
    printedAny = true;
  }

  // Exit non-zero only if every requested component failed.
  if (anyFailed && !printedAny) process.exit(1);
}

function cmdExample(docsDir, componentName, exampleName) {
  if (!componentName || !exampleName) {
    console.error('Usage: wds.cjs example <ComponentName> "<ExampleName>"');
    console.error('Example: wds.cjs example Button "Loading state"');
    process.exit(1);
  }
  validateComponentName(componentName);

  const filePath = path.join(
    docsDir,
    "components",
    `${componentName}Examples.md`
  );
  const content = readFile(filePath);

  if (!content) {
    console.error(`No examples file for "${componentName}".`);
    process.exit(1);
  }

  const lines = content.split("\n");
  let startLine = -1;
  let endLine = lines.length;
  const searchName = exampleName.toLowerCase();

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith("### ")) {
      const name = lines[i].replace("### ", "").trim().toLowerCase();
      if (startLine >= 0) {
        // Found the next section — stop here
        endLine = i;
        break;
      }
      if (name === searchName || name.includes(searchName)) {
        startLine = i;
      }
    }
  }

  if (startLine < 0) {
    console.error(
      `Example "${exampleName}" not found for ${componentName}.\n`
    );
    // List available examples
    const available = [];
    for (const line of lines) {
      if (line.startsWith("### ")) {
        available.push(line.replace("### ", "").trim());
      }
    }
    if (available.length > 0) {
      console.log("Available examples:");
      for (const ex of available) {
        console.log(`  - ${ex}`);
      }
    }
    process.exit(1);
  }

  console.log(lines.slice(startLine, endLine).join("\n"));
}

function cmdTestkit(docsDir, componentName, methodName) {
  if (!componentName) {
    console.error("Usage: wds.cjs testkit <ComponentName> [methodName]");
    console.error("Example: wds.cjs testkit Button");
    console.error('Example: wds.cjs testkit Button click');
    process.exit(1);
  }
  validateComponentName(componentName);

  const filePath = path.join(
    docsDir,
    "components",
    `${componentName}Testkit.md`,
  );
  const content = readFile(filePath);

  if (!content) {
    console.error(
      `Testkit docs for "${componentName}" not found. Run: wds.cjs search <keyword>`,
    );
    process.exit(1);
  }

  if (!methodName) {
    console.log(content);
    return;
  }

  const lines = content.split("\n");
  const searchName = methodName.toLowerCase();
  let startLine = -1;
  let endLine = lines.length;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith("### ") && !lines[i].startsWith("### API")) {
      const name = lines[i].replace("### ", "").trim().toLowerCase();
      if (startLine >= 0) {
        endLine = i;
        break;
      }
      if (name === searchName || name.includes(searchName)) {
        startLine = i;
      }
    }
  }

  if (startLine < 0) {
    console.error(
      `Method "${methodName}" not found on ${componentName} testkit.\n`,
    );
    const available = [];
    let inApiSection = false;
    for (const line of lines) {
      if (line.startsWith("### API")) {
        inApiSection = true;
        continue;
      }
      if (inApiSection && line.startsWith("### ")) {
        available.push(line.replace("### ", "").trim());
      }
    }
    if (available.length > 0) {
      console.log("Available methods:");
      for (const m of available) {
        console.log(`  - ${m}`);
      }
    }
    process.exit(1);
  }

  console.log(lines.slice(startLine, endLine).join("\n"));
}

function cmdIcons(docsDir, terms) {
  if (terms.length === 0) {
    console.error("Usage: wds.cjs icons <query> [query...]");
    console.error("Example: wds.cjs icons Add Edit Delete");
    process.exit(1);
  }

  const content = readFile(path.join(docsDir, "icons.md"));
  if (!content) {
    console.error("Error: icons.md not found");
    process.exit(1);
  }

  const regex = new RegExp(buildTermsPattern(terms), "i");
  const matches = [];

  for (const line of content.split("\n")) {
    if (line.trim() && regex.test(line)) {
      matches.push(line.trim());
    }
  }

  if (matches.length === 0) {
    console.log(`No icons found matching "${terms.join(" ")}".`);
    return;
  }

  console.log(`Found ${matches.length} icon(s):\n`);
  for (const m of matches) {
    console.log(`  ${m}`);
  }
  console.log(
    "\nIcons are from @wix/wix-ui-icons-common. Each icon has a Small variant (e.g., Add + AddSmall)."
  );
}

function cmdHelp(docsDir) {
  const scriptPath = path.resolve(__dirname, "wds.cjs");
  console.log(`WDS Documentation Helper

Usage:
  node ${scriptPath} search <keyword>              Search components by keyword
  node ${scriptPath} component <Name>              Get props + example list
  node ${scriptPath} components <Name1> <Name2>... Get props + example list for multiple components in one call
  node ${scriptPath} example <Name> "<ExampleName>" Get a specific example
  node ${scriptPath} testkit <Name> [method]       Get testkit imports + API (or one method)
  node ${scriptPath} icons <query>                 Search for icons

Examples:
  node ${scriptPath} search table list
  node ${scriptPath} search form input validation
  node ${scriptPath} component Button
  node ${scriptPath} components Button Card Table Input
  node ${scriptPath} example Button "Loading state"
  node ${scriptPath} testkit Button
  node ${scriptPath} testkit Button click
  node ${scriptPath} icons Add Edit Delete

Docs found at: ${docsDir}`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const docsDir = findDocsDir();
if (!docsDir) {
  console.error(
    "Error: @wix/design-system not found in node_modules.\n" +
      "Install it first: npm i @wix/design-system"
  );
  process.exit(1);
}

const [command, ...args] = process.argv.slice(2);

switch (command) {
  case "search":
    cmdSearch(docsDir, args);
    break;
  case "component":
    cmdComponent(docsDir, args[0]);
    break;
  case "components":
    cmdComponents(docsDir, args);
    break;
  case "example":
    cmdExample(docsDir, args[0], args.slice(1).join(" "));
    break;
  case "testkit":
    cmdTestkit(docsDir, args[0], args[1]);
    break;
  case "icons":
    cmdIcons(docsDir, args);
    break;
  default:
    cmdHelp(docsDir);
    break;
}
