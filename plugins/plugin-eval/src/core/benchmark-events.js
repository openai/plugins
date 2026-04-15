function toNumber(value) {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function normalizeUsageCandidate(candidate) {
  if (!candidate || typeof candidate !== "object") {
    return null;
  }

  const usage = candidate.usage && typeof candidate.usage === "object"
    ? candidate.usage
    : candidate.response?.usage && typeof candidate.response?.usage === "object"
      ? candidate.response.usage
      : candidate;

  const inputTokens = toNumber(usage.input_tokens);
  const outputTokens = toNumber(usage.output_tokens);
  const totalTokens = toNumber(usage.total_tokens) ?? ((inputTokens || 0) + (outputTokens || 0));

  if (inputTokens === null && outputTokens === null && totalTokens === null) {
    return null;
  }

  return {
    input_tokens: inputTokens || 0,
    output_tokens: outputTokens || 0,
    total_tokens: totalTokens || 0,
    ...(usage.input_token_details ? { input_token_details: usage.input_token_details } : {}),
    ...(usage.output_token_details ? { output_token_details: usage.output_token_details } : {}),
    ...(usage.output_tokens_details ? { output_tokens_details: usage.output_tokens_details } : {}),
    raw: usage,
  };
}

function collectUsageCandidate(value, matches) {
  if (!value || typeof value !== "object") {
    return;
  }

  const normalized = normalizeUsageCandidate(value);
  if (normalized) {
    matches.push(normalized);
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      collectUsageCandidate(item, matches);
    }
    return;
  }

  for (const nested of Object.values(value)) {
    collectUsageCandidate(nested, matches);
  }
}

function extractLatestUsage(events) {
  const matches = [];
  for (const event of events) {
    collectUsageCandidate(event, matches);
  }
  return matches.length > 0 ? matches[matches.length - 1] : null;
}

function collectErrorMessage(event) {
  if (!event || typeof event !== "object") {
    return null;
  }

  if (typeof event.message === "string" && event.type === "error") {
    return event.message;
  }

  if (typeof event.error?.message === "string") {
    return event.error.message;
  }

  return null;
}

function extractShellCommand(event) {
  if (!event || typeof event !== "object") {
    return null;
  }

  const candidates = [
    event.command,
    event.cmd,
    event.parameters?.cmd,
    event.arguments?.cmd,
    event.payload?.command,
    event.payload?.cmd,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) {
      return candidate.trim();
    }
  }

  if (event.recipient_name === "functions.exec_command") {
    return event.parameters?.cmd || event.arguments?.cmd || event.command || "functions.exec_command";
  }

  return null;
}

function extractToolName(event) {
  if (!event || typeof event !== "object") {
    return null;
  }

  const candidates = [
    event.tool_name,
    event.tool?.name,
    event.name,
    event.recipient_name,
    event.payload?.tool_name,
  ];

  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) {
      return candidate.trim();
    }
  }

  if (typeof event.type === "string" && event.type.includes("tool")) {
    return event.type;
  }

  return null;
}

function isShellEvent(event) {
  const type = typeof event?.type === "string" ? event.type : "";
  return Boolean(
    extractShellCommand(event) ||
      type.includes("exec_command") ||
      type.includes("shell"),
  );
}

function isToolEvent(event) {
  const type = typeof event?.type === "string" ? event.type : "";
  return Boolean(
    extractToolName(event) ||
      type.includes("tool"),
  );
}

function isFailureEvent(event) {
  const type = typeof event?.type === "string" ? event.type : "";
  return type.includes("failed") || type === "error" || Boolean(event?.error);
}

export function parseCodexJsonStream(text) {
  const lines = String(text || "").split(/\r?\n/);
  const events = [];
  const ignoredLines = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    try {
      events.push(JSON.parse(trimmed));
    } catch {
      ignoredLines.push(line);
    }
  }

  return {
    events,
    ignoredLines,
  };
}

export function summarizeCodexEvents(events) {
  const errorMessages = [];
  const toolNames = [];
  const shellCommands = [];
  const failedShellCommands = [];
  let threadId = null;
  let turnFailed = false;

  for (const event of events) {
    if (!threadId && typeof event.thread_id === "string") {
      threadId = event.thread_id;
    }

    const errorMessage = collectErrorMessage(event);
    if (errorMessage) {
      errorMessages.push(errorMessage);
    }

    if (isToolEvent(event)) {
      toolNames.push(extractToolName(event) || event.type || "tool");
    }

    if (isShellEvent(event)) {
      const command = extractShellCommand(event) || event.type || "shell";
      shellCommands.push(command);
      if (isFailureEvent(event)) {
        failedShellCommands.push(command);
      }
    }

    if (event.type === "turn.failed") {
      turnFailed = true;
    }
  }

  const usage = extractLatestUsage(events);
  const completed = events.some((event) => event.type === "turn.completed");
  const failed = turnFailed || events.some((event) => event.type === "turn.cancelled");

  return {
    threadId,
    eventCount: events.length,
    ignoredLineCount: 0,
    finalStatus: failed ? "failed" : completed ? "completed" : "unknown",
    errorMessages,
    toolCallCount: toolNames.length,
    shellCommandCount: shellCommands.length,
    failedShellCommandCount: failedShellCommands.length,
    toolNames,
    shellCommands,
    usage,
    usageAvailability: usage ? "present" : "unavailable",
  };
}
