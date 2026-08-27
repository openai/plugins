function text(value) {
  return value == null ? "" : String(value);
}

function collapseSqlWhitespace(sql) {
  let output = "";
  let quote = "";
  let previousWasSpace = false;
  for (let index = 0; index < sql.length; index += 1) {
    const char = sql[index];
    const next = sql[index + 1];
    if (quote) {
      output += char;
      if (char === quote) {
        if (quote === "'" && next === "'") {
          output += next;
          index += 1;
        } else {
          quote = "";
        }
      }
      previousWasSpace = false;
      continue;
    }
    if (char === "'" || char === '"') {
      quote = char;
      output += char;
      previousWasSpace = false;
      continue;
    }
    if (/\s/.test(char)) {
      if (!previousWasSpace) output += " ";
      previousWasSpace = true;
      continue;
    }
    output += char;
    previousWasSpace = false;
  }
  return output.trim();
}

function uppercaseSqlKeywords(sql) {
  return sql.replace(
    /\b(select|from|where|and|or|group|by|order|having|limit|join|left|right|inner|outer|full|cross|on|with|as|case|when|then|else|end|not|in|is|null|between|like|true|false|desc|asc|union|all|over|partition)\b/gi,
    (match) => match.toUpperCase(),
  );
}

function indentContinuation(line) {
  return line
    .replace(/\bAND\b/g, "\n  AND")
    .replace(/\bOR\b/g, "\n  OR")
    .replace(/\bWHEN\b/g, "\n  WHEN")
    .replace(/\bELSE\b/g, "\n  ELSE");
}

export function formatSql(sql) {
  const normalized = uppercaseSqlKeywords(collapseSqlWhitespace(text(sql)));
  if (!normalized) return "";
  if (!/\b(SELECT|WITH|FROM|WHERE|ORDER BY|GROUP BY|HAVING|LIMIT)\b/.test(normalized)) {
    return normalized;
  }

  let formatted = normalized
    .replace(/\s*,\s*/g, ",\n  ")
    .replace(/\bWITH\b\s*/g, "WITH\n  ")
    .replace(/\bSELECT\b\s*/g, "SELECT\n  ")
    .replace(/\bFROM\b\s*/g, "\nFROM ")
    .replace(/\bWHERE\b\s*/g, "\nWHERE\n  ")
    .replace(/\bGROUP\s+BY\b\s*/g, "\nGROUP BY\n  ")
    .replace(/\bHAVING\b\s*/g, "\nHAVING\n  ")
    .replace(/\bORDER\s+BY\b\s*/g, "\nORDER BY\n  ")
    .replace(/\bLIMIT\b\s*/g, "\nLIMIT ");

  formatted = formatted
    .split("\n")
    .map((line) => indentContinuation(line.trimEnd()))
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]+\n/g, "\n")
    .trim();

  return formatted.endsWith(";") ? formatted : formatted.replace(/\s*;?\s*$/, ";");
}

export function sourceQueryFromSource(source) {
  const sourceObject = source && typeof source === "object" && !Array.isArray(source) ? source : null;
  const query = sourceObject && sourceObject.query && typeof sourceObject.query === "object" && !Array.isArray(sourceObject.query)
    ? sourceObject.query
    : null;
  if (query) {
    return {
      engine: query.engine,
      id: query.id,
      url: query.url,
      sql: query.sql,
      description: query.description,
      language: query.language,
      executed_at: query.executed_at,
      label: sourceObject.label,
      filters: query.filters,
      metric_definitions: query.metric_definitions,
      tables_used: query.tables_used,
    };
  }
  return null;
}

export function sourceCodeText(sourceQuery) {
  const source = sourceQuery && typeof sourceQuery === "object" ? sourceQuery : {};
  const code = text(source.sql).trim();
  return code ? text(source.sql) : "";
}

export function sourceCodeLanguage(sourceQuery) {
  const source = sourceQuery && typeof sourceQuery === "object" ? sourceQuery : {};
  const raw = text(source.language || source.engine).toLowerCase();
  if (raw.includes("python")) return "Python";
  if (raw.includes("sql") || raw.includes("databricks") || raw.includes("trino") || raw.includes("snowflake")) return "SQL";
  return sourceCodeText(sourceQuery) ? "Query" : "";
}

export function formatSourceCode(code, language) {
  return language === "SQL" ? formatSql(code) : text(code);
}

function codeTokenPattern(language) {
  if (language === "Python") {
    return /(#.*|"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:and|as|assert|async|await|break|class|continue|def|elif|else|except|False|finally|for|from|if|import|in|is|lambda|None|not|or|pass|raise|return|True|try|while|with|yield)\b|\b\d+(?:\.\d+)?\b)/g;
  }
  return /(--[^\n]*|\/\*[\s\S]*?\*\/|"(?:\\.|[^"\\])*"|'(?:''|[^'])*'|\b(?:select|from|where|group|by|order|limit|having|join|left|right|inner|outer|full|cross|on|with|as|case|when|then|else|end|and|or|not|in|is|null|between|like|sum|avg|min|max|count|date_trunc|cast|try_cast|coalesce|distinct|union|all|over|partition|row_number|rank|desc|asc|true|false)\b|\b\d+(?:\.\d+)?\b)/gi;
}

function codeTokenClass(token, language) {
  if (language === "Python" && token.startsWith("#")) return "code-comment";
  if (token.startsWith("--") || token.startsWith("/*")) return "code-comment";
  if (token.startsWith("\"") || token.startsWith("'")) return "code-string";
  if (/^\d/.test(token)) return "code-number";
  return "code-keyword";
}

export function renderSourceCode(root, code, language) {
  root.innerHTML = "";
  const formatted = formatSourceCode(code, language);
  const pattern = codeTokenPattern(language);
  let lastIndex = 0;
  formatted.replace(pattern, (match, _token, offset) => {
    if (offset > lastIndex) root.appendChild(document.createTextNode(formatted.slice(lastIndex, offset)));
    const token = document.createElement("span");
    token.className = `code-token ${codeTokenClass(match, language)}`;
    token.textContent = match;
    root.appendChild(token);
    lastIndex = offset + match.length;
    return match;
  });
  if (lastIndex < formatted.length) root.appendChild(document.createTextNode(formatted.slice(lastIndex)));
}
