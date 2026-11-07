// These are function-body lexical estimates, not AST cyclomatic complexity.
// They handle ordinary declarations, multiline signatures and nested functions without a
// language runtime or parser dependency. Python lambdas, JS expression arrows,
// JSX and decisions inside interpolated strings are not measured as functions.
// TypeScript conditional types and unusual syntax can still need a real parser.

function maskLiterals(source, language) {
  const chars = source.split("");
  const blank = (start, end) => {
    for (let i = start; i < end; i += 1) if (chars[i] !== "\n" && chars[i] !== "\r") chars[i] = " ";
  };
  let previous = "";
  for (let i = 0; i < source.length;) {
    const start = i;
    if ((language === "py" && source[i] === "#") || (language === "ts" && source.startsWith("//", i))) {
      while (i < source.length && source[i] !== "\n") i += 1;
      blank(start, i);
    } else if (language === "ts" && source.startsWith("/*", i)) {
      const end = source.indexOf("*/", i + 2);
      i = end < 0 ? source.length : end + 2;
      blank(start, i);
    } else if (source[i] === "'" || source[i] === '"' || (language === "ts" && source[i] === "`")) {
      const quote = source[i];
      const delimiter = language === "py" && source.startsWith(quote.repeat(3), i) ? quote.repeat(3) : quote;
      i += delimiter.length;
      while (i < source.length) {
        if (source[i] === "\\") { i += 2; continue; }
        if (source.startsWith(delimiter, i)) { i += delimiter.length; break; }
        i += 1;
      }
      blank(start, Math.min(i, source.length));
      previous = "literal";
    } else if (language === "ts" && source[i] === "/" && (!previous || /^(?:[=(:,!&|?;{\[]|return|throw|case|=>)$/.test(previous))) {
      // A slash in expression-start position is usually a regular expression.
      // Distinguishing every regex from division requires a JavaScript parser.
      let inClass = false;
      i += 1;
      while (i < source.length && source[i] !== "\n") {
        if (source[i] === "\\") { i += 2; continue; }
        if (source[i] === "[") inClass = true;
        if (source[i] === "]") inClass = false;
        if (source[i++] === "/" && !inClass) break;
      }
      while (/[a-z]/i.test(source[i] || "") && i < source.length) i += 1;
      blank(start, i);
      previous = "literal";
    } else {
      const word = /^[A-Za-z_$][\w$]*/.exec(source.slice(i));
      if (word) { previous = word[0]; i += word[0].length; }
      else { if (!/\s/.test(source[i])) previous = source[i]; i += 1; }
    }
  }
  return chars.join("");
}

function withoutChildren(text, start, end, functions) {
  let cursor = start;
  let own = "";
  for (const child of functions.filter((fn) => fn.start >= start && fn.end <= end).sort((a, b) => a.start - b.start)) {
    if (child.start < cursor) continue;
    own += text.slice(cursor, child.start);
    cursor = child.end;
  }
  return own + text.slice(cursor, end);
}

function indentWidth(line) {
  let width = 0;
  for (const char of /^\s*/.exec(line)[0]) width = char === "\t" ? width + 8 - width % 8 : width + 1;
  return width;
}

export function measurePythonFunctions(source) {
  const clean = maskLiterals(source, "py");
  const lines = clean.split("\n");
  const originalLines = source.split("\n");
  const statements = [];
  let offset = 0;
  let depth = 0;
  let continued = false;
  for (let line = 0; line < lines.length; line += 1) {
    if (depth === 0 && !continued && lines[line].trim()) statements.push({ line, offset, indent: indentWidth(lines[line]) });
    for (const char of lines[line]) {
      if ("([{".includes(char)) depth += 1;
      if (")]}".includes(char)) depth -= 1;
    }
    continued = /\\\s*$/.test(lines[line]);
    offset += lines[line].length + 1;
  }
  const functions = [];
  for (let index = 0; index < statements.length; index += 1) {
    const statement = statements[index];
    const match = /^\s*(?:async\s+)?def\s+([A-Za-z_][\w]*)\s*(?:\[[^\]]*\]\s*)?\(/.exec(clean.slice(statement.offset));
    if (!match) continue;
    let colon = statement.offset + match[0].length;
    let brackets = 1;
    for (; colon < clean.length; colon += 1) {
      const char = clean[colon];
      if ("([{".includes(char)) brackets += 1;
      if (")]}".includes(char)) brackets -= 1;
      if (char === ":" && brackets === 0) break;
    }
    if (colon === clean.length) continue;
    let next = index + 1;
    while (next < statements.length && statements[next].indent > statement.indent) next += 1;
    let endLine = (next < statements.length ? statements[next].line : lines.length) - 1;
    while (endLine > statement.line && !originalLines[endLine].trim()) endLine -= 1;
    const end = lines.slice(0, endLine + 1).reduce((sum, line) => sum + line.length + 1, 0) - 1;
    functions.push({ name: match[1], start: statement.offset, body: colon + 1, end, startLine: statement.line + 1, endLine: endLine + 1, length: endLine - statement.line + 1, indent: statement.indent });
  }
  return functions.map((fn) => {
    const own = withoutChildren(clean, fn.body, fn.end, functions);
    const decisions = (own.match(/\b(?:if|elif|for|while|except|and|or)\b/g) || []).length;
    const children = functions.filter((child) => child.start >= fn.body && child.end <= fn.end);
    const ownStatements = statements.filter((statement) => statement.offset >= fn.body && statement.offset < fn.end &&
      !children.some((child) => statement.offset >= child.start && statement.offset < child.end));
    const bodyIndent = ownStatements.reduce((min, statement) => Math.min(min, statement.indent), Infinity);
    const maxIndent = ownStatements.reduce((max, statement) => Math.max(max, statement.indent), fn.indent);
    const indentStep = Number.isFinite(bodyIndent) ? bodyIndent - fn.indent : 0;
    return { ...fn, complexity: 1 + decisions, nesting: indentStep > 0 ? Math.max(0, Math.round((maxIndent - bodyIndent) / indentStep)) : 0 };
  });
}

function tokenize(source) {
  const tokens = [];
  const expression = /[A-Za-z_$][\w$]*|=>|\?\.|\?\?|&&|\|\||[^\s]/g;
  for (const match of source.matchAll(expression)) tokens.push({ value: match[0], start: match.index });
  return tokens;
}

function typeDeclarations(tokens, pairs, source) {
  const ranges = [];
  for (let i = 0; i < tokens.length; i += 1) {
    const kind = tokens[i].value;
    if (!["type", "interface"].includes(kind) || !/^[A-Za-z_$][\w$]*$/.test(tokens[i + 1]?.value || "")) continue;
    let end = i + 2;
    if (kind === "interface") {
      while (end < tokens.length && !["{", ";"].includes(tokens[end].value)) end += 1;
      if (!pairs.has(end)) continue;
      end = pairs.get(end);
    } else {
      while (end < tokens.length && !["=", ";"].includes(tokens[end].value)) end += 1;
      if (tokens[end]?.value !== "=") continue;
      end += 1;
      while (end < tokens.length && tokens[end].value !== ";") {
        if (pairs.has(end) && "([{".includes(tokens[end].value)) end = pairs.get(end);
        const next = tokens[end + 1];
        if (!next || (/^(?:export|const|let|var|function|async|class|interface|type)$/.test(next.value) && source.slice(tokens[end].start, next.start).includes("\n"))) break;
        end += 1;
      }
    }
    const endOffset = tokens[end] ? tokens[end].start + tokens[end].value.length : source.length;
    ranges.push({ start: tokens[i].start, end: endOffset });
    i = end;
  }
  return ranges;
}

export function measureTypeScriptFunctions(source) {
  const clean = maskLiterals(source, "ts");
  const tokens = tokenize(clean);
  const pairs = new Map();
  const stack = [];
  for (let i = 0; i < tokens.length; i += 1) {
    if ("([{".includes(tokens[i].value)) stack.push(i);
    if (")]}".includes(tokens[i].value)) {
      const open = stack.pop();
      if (open !== undefined) { pairs.set(open, i); pairs.set(i, open); }
    }
  }
  const types = typeDeclarations(tokens, pairs, clean);
  const insideType = (token) => types.some((range) => token.start >= range.start && token.start < range.end);
  const functions = [];
  const bodies = new Set();
  const addFunction = (start, body, name) => {
    if (!pairs.has(body) || bodies.has(body)) return;
    const endToken = pairs.get(body);
    const startLine = clean.slice(0, tokens[start].start).split("\n").length;
    const endLine = clean.slice(0, tokens[endToken].start).split("\n").length;
    functions.push({ name, start: tokens[start].start, body: tokens[body].start + 1, end: tokens[endToken].start + 1, startLine, endLine, length: endLine - startLine + 1 });
    bodies.add(body);
  };
  const controls = new Set(["if", "for", "while", "switch", "catch", "with"]);
  for (let open = 0; open < tokens.length; open += 1) {
    if (tokens[open].value !== "(" || !pairs.has(open) || insideType(tokens[open])) continue;
    const close = pairs.get(open);
    let nameIndex = open - 1;
    if (tokens[nameIndex]?.value === ">") {
      let angleDepth = 1;
      while (--nameIndex >= 0) {
        if (tokens[nameIndex].value === ">") angleDepth += 1;
        if (tokens[nameIndex].value === "<") angleDepth -= 1;
        if (angleDepth === 0) { nameIndex -= 1; break; }
      }
    }
    const before = tokens[nameIndex]?.value;
    const named = /^[A-Za-z_$][\w$]*$/.test(before || "") && !controls.has(before);
    let body = close + 1;
    // Skip return annotations, including balanced object/tuple/function types.
    if (tokens[body]?.value === ":") {
      body += 1;
      while (body < tokens.length) {
        const value = tokens[body].value;
        if ([";", "="].includes(value)) break;
        if (value === "=>") break;
        if (value === "{") {
          const end = pairs.get(body);
          if (end !== undefined && ["{", "=>", "|", "&", "["].includes(tokens[end + 1]?.value)) { body = end + 1; continue; }
          break;
        }
        if (["(", "["].includes(value) && pairs.has(body)) body = pairs.get(body) + 1;
        else body += 1;
      }
    }
    const arrow = tokens[body]?.value === "=>";
    if (arrow) body += 1;
    if ((!named && !arrow && before !== "function") || controls.has(before) || tokens[body]?.value !== "{" || !pairs.has(body) || bodies.has(body)) continue;
    // A call followed by a block is not a declaration when qualified by '.' or 'new'.
    if (!arrow && [".", "?.", "new"].includes(tokens[nameIndex - 1]?.value)) continue;
    let start = nameIndex;
    if (tokens[start - 1]?.value === "function") start -= 1;
    if (arrow) start = open;
    addFunction(Math.max(0, start), body, named ? before : "anonymous");
  }
  for (let i = 1; i < tokens.length - 1; i += 1) {
    if (tokens[i].value === "=>" && !insideType(tokens[i]) && /^[A-Za-z_$][\w$]*$/.test(tokens[i - 1].value) && tokens[i + 1].value === "{") {
      addFunction(i - 1, i + 1, "anonymous");
    }
  }
  return functions.map((fn) => {
    const own = tokenize(withoutChildren(clean, fn.body, fn.end - 1, [...functions, ...types]));
    let decisions = 0;
    let depth = 0;
    let maxDepth = 0;
    for (let i = 0; i < own.length; i += 1) {
      const value = own[i].value;
      if (value === "{") { depth += 1; maxDepth = Math.max(maxDepth, depth); }
      if (value === "}") depth -= 1;
      if ((["if", "for", "while", "case", "catch"].includes(value) && ![".", "?."].includes(own[i - 1]?.value) && own[i + 1]?.value !== ":") || ["&&", "||"].includes(value)) decisions += 1;
      // ?. and ?? are single tokens. Optional-property '?' is followed by ':'.
      if (value === "?" && own[i + 1]?.value !== ":") decisions += 1;
    }
    return { ...fn, complexity: 1 + decisions, nesting: maxDepth };
  });
}
