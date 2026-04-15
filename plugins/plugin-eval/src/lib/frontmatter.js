function countIndent(line) {
  return line.length - line.trimStart().length;
}

function parseScalar(rawValue) {
  const value = rawValue.trim();
  if (!value) {
    return "";
  }
  if (
    (value.startsWith("\"") && value.endsWith("\"")) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  if (value === "null") {
    return null;
  }
  if (/^-?\d+(\.\d+)?$/.test(value)) {
    return Number(value);
  }
  if (value.startsWith("[") && value.endsWith("]")) {
    return value
      .slice(1, -1)
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
      .map(parseScalar);
  }
  return value;
}

function nextMeaningfulIndex(lines, startIndex) {
  for (let index = startIndex; index < lines.length; index += 1) {
    const trimmed = lines[index].trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }
    return index;
  }
  return -1;
}

function parseBlockScalarHeader(rawValue) {
  const value = rawValue.trim();
  if (!value) {
    return null;
  }
  if (!value.startsWith(">") && !value.startsWith("|")) {
    return null;
  }
  return {
    style: value[0],
  };
}

function foldBlockScalarLines(lines) {
  let result = "";
  for (let index = 0; index < lines.length; index += 1) {
    const current = lines[index];
    const next = lines[index + 1];

    result += current;
    if (next === undefined) {
      continue;
    }
    if (current === "" || next === "") {
      result += "\n";
    } else {
      result += " ";
    }
  }
  return result;
}

function parseBlockScalar(lines, startIndex, parentIndent, style) {
  const blockLines = [];
  let index = startIndex;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();
    const currentIndent = countIndent(line);

    if (trimmed && currentIndent <= parentIndent) {
      break;
    }

    blockLines.push(line);
    index += 1;
  }

  const contentIndent = blockLines.reduce((minimumIndent, line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      return minimumIndent;
    }
    const currentIndent = countIndent(line);
    if (currentIndent <= parentIndent) {
      return minimumIndent;
    }
    return minimumIndent === null ? currentIndent : Math.min(minimumIndent, currentIndent);
  }, null);

  const normalizedLines = blockLines.map((line) => {
    if (!line.trim()) {
      return "";
    }
    if (contentIndent === null) {
      return line.trim();
    }
    return line.slice(contentIndent);
  });

  return {
    value: style === "|" ? normalizedLines.join("\n") : foldBlockScalarLines(normalizedLines),
    nextIndex: index,
  };
}

function parseBlock(lines, startIndex, indent) {
  const firstIndex = nextMeaningfulIndex(lines, startIndex);
  if (firstIndex === -1) {
    return { value: {}, nextIndex: lines.length };
  }

  const firstLine = lines[firstIndex];
  const isArray = firstLine.trim().startsWith("- ");
  const container = isArray ? [] : {};
  let index = firstIndex;

  while (index < lines.length) {
    const line = lines[index];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      index += 1;
      continue;
    }

    const currentIndent = countIndent(line);
    if (currentIndent < indent) {
      break;
    }
    if (currentIndent > indent) {
      throw new Error(`Unexpected indentation at line ${index + 1}`);
    }

    if (isArray) {
      if (!trimmed.startsWith("- ")) {
        break;
      }
      const payload = trimmed.slice(2).trim();
      index += 1;
      if (!payload) {
        const nested = parseBlock(lines, index, indent + 2);
        container.push(nested.value);
        index = nested.nextIndex;
      } else {
        container.push(parseScalar(payload));
      }
      continue;
    }

    const match = /^([A-Za-z0-9_-]+):(.*)$/.exec(trimmed);
    if (!match) {
      throw new Error(`Invalid key/value pair at line ${index + 1}`);
    }

    const [, key, remainder] = match;
    if (remainder.trim()) {
      const blockScalar = parseBlockScalarHeader(remainder);
      if (blockScalar) {
        const parsed = parseBlockScalar(lines, index + 1, indent, blockScalar.style);
        container[key] = parsed.value;
        index = parsed.nextIndex;
        continue;
      }

      container[key] = parseScalar(remainder.trim());
      index += 1;
      continue;
    }

    const nestedIndex = nextMeaningfulIndex(lines, index + 1);
    if (nestedIndex === -1 || countIndent(lines[nestedIndex]) <= indent) {
      container[key] = "";
      index += 1;
      continue;
    }

    const nested = parseBlock(lines, index + 1, indent + 2);
    container[key] = nested.value;
    index = nested.nextIndex;
  }

  return { value: container, nextIndex: index };
}

export function extractFrontmatter(markdown) {
  const normalized = markdown.replace(/\r\n/g, "\n");
  const lines = normalized.split("\n");
  if (lines[0] !== "---") {
    return {
      frontmatterText: "",
      body: normalized,
      errors: ["No YAML frontmatter found."],
    };
  }

  const closingIndex = lines.indexOf("---", 1);
  if (closingIndex === -1) {
    return {
      frontmatterText: "",
      body: normalized,
      errors: ["Frontmatter opening delimiter is missing a closing delimiter."],
    };
  }

  return {
    frontmatterText: lines.slice(1, closingIndex).join("\n"),
    body: lines.slice(closingIndex + 1).join("\n"),
    errors: [],
  };
}

export function parseFrontmatter(markdown) {
  const extracted = extractFrontmatter(markdown);
  if (extracted.errors.length > 0) {
    return {
      data: null,
      body: extracted.body,
      errors: extracted.errors,
    };
  }

  try {
    const parsed = parseBlock(extracted.frontmatterText.split("\n"), 0, 0).value;
    return {
      data: parsed,
      body: extracted.body,
      errors: [],
    };
  } catch (error) {
    return {
      data: null,
      body: extracted.body,
      errors: [error instanceof Error ? error.message : String(error)],
    };
  }
}
