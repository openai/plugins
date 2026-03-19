// hooks/src/logger.mts
import { randomBytes } from "crypto";
var LEVELS = ["off", "summary", "debug", "trace"];
var LEVEL_INDEX = {
  off: 0,
  summary: 1,
  debug: 2,
  trace: 3
};
var VERCEL_PLUGIN_SHARED_LOGGER_CONTEXT_KEY = "__vercelPluginSharedLoggerContext__";
function readErrorField(error, field) {
  return field in error ? error[field] : void 0;
}
function serializeErrorForLog(error) {
  if (error instanceof Error) {
    const maybeCode = "code" in error && typeof error.code !== "undefined" ? { code: error.code } : {};
    return {
      name: error.name,
      message: error.message,
      ...maybeCode,
      ...error.stack ? { stack: error.stack } : {}
    };
  }
  if (typeof error === "object" && error !== null) {
    const record = error;
    return {
      type: error.constructor?.name || "Object",
      ...readErrorField(record, "name") !== void 0 ? { name: readErrorField(record, "name") } : {},
      ...readErrorField(record, "message") !== void 0 ? { message: readErrorField(record, "message") } : {},
      ...readErrorField(record, "code") !== void 0 ? { code: readErrorField(record, "code") } : {},
      ...readErrorField(record, "stack") !== void 0 ? { stack: readErrorField(record, "stack") } : {}
    };
  }
  return { value: error };
}
function logCaughtError(logger, event, error, context = {}) {
  logger.debug(event, { ...context, error: serializeErrorForLog(error) });
}
function resolveLogLevel() {
  const explicit = (process.env.VERCEL_PLUGIN_LOG_LEVEL || "").toLowerCase().trim();
  if (explicit && LEVEL_INDEX[explicit] !== void 0) {
    return explicit;
  }
  if (explicit) {
    console.error(
      `[vercel] Unknown VERCEL_PLUGIN_LOG_LEVEL="${explicit}". Valid levels: ${LEVELS.join(", ")}. Falling back to "off".`
    );
  }
  if (process.env.VERCEL_PLUGIN_DEBUG === "1" || process.env.VERCEL_PLUGIN_HOOK_DEBUG === "1") {
    return "debug";
  }
  return "off";
}
function getSharedLoggerContext() {
  const loggerGlobal = globalThis;
  if (!loggerGlobal[VERCEL_PLUGIN_SHARED_LOGGER_CONTEXT_KEY]) {
    loggerGlobal[VERCEL_PLUGIN_SHARED_LOGGER_CONTEXT_KEY] = {};
  }
  return loggerGlobal[VERCEL_PLUGIN_SHARED_LOGGER_CONTEXT_KEY];
}
function resolveInvocationId(active, explicitInvocationId) {
  if (!active) return "";
  if (explicitInvocationId) return explicitInvocationId;
  const sharedContext = getSharedLoggerContext();
  if (!sharedContext.invocationId) {
    sharedContext.invocationId = randomBytes(4).toString("hex");
  }
  return sharedContext.invocationId;
}
function createLogger(opts) {
  const options = typeof opts === "string" ? { level: opts } : opts || {};
  const level = options.level || resolveLogLevel();
  const rank = LEVEL_INDEX[level] || 0;
  const active = rank > 0;
  const invocationId = resolveInvocationId(active, options.invocationId);
  const safeNow = typeof performance !== "undefined" && typeof performance.now === "function" ? () => performance.now() : () => Date.now();
  const t0 = active ? safeNow() : 0;
  function emit(minLevel, event, data) {
    if (rank < (LEVEL_INDEX[minLevel] || 0)) return;
    const line = JSON.stringify({
      invocationId,
      event,
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      ...data
    });
    process.stderr.write(line + "\n");
  }
  return {
    level,
    active,
    t0,
    now: safeNow,
    elapsed() {
      return Math.round(safeNow() - t0);
    },
    summary(event, data) {
      emit("summary", event, data);
    },
    issue(code, message, hint, context) {
      emit("summary", "issue", { code, message, hint, context });
    },
    complete(reason, counts, timing) {
      const {
        matchedCount = 0,
        injectedCount = 0,
        dedupedCount = 0,
        cappedCount = 0,
        tsxReviewTriggered,
        devServerVerifyTriggered,
        matchedSkills,
        injectedSkills,
        droppedByCap,
        droppedByBudget,
        boostsApplied
      } = counts || {};
      emit("summary", "complete", {
        reason,
        matchedCount,
        injectedCount,
        dedupedCount,
        cappedCount,
        ...tsxReviewTriggered !== void 0 ? { tsxReviewTriggered } : {},
        ...devServerVerifyTriggered !== void 0 ? { devServerVerifyTriggered } : {},
        ...matchedSkills ? { matchedSkills } : {},
        ...injectedSkills ? { injectedSkills } : {},
        ...droppedByCap && droppedByCap.length > 0 ? { droppedByCap } : {},
        ...droppedByBudget && droppedByBudget.length > 0 ? { droppedByBudget } : {},
        ...boostsApplied && boostsApplied.length > 0 ? { boostsApplied } : {},
        elapsed_ms: Math.round(safeNow() - t0),
        ...timing ? { timing_ms: timing } : {}
      });
    },
    debug(event, data) {
      emit("debug", event, data);
    },
    trace(event, data) {
      emit("trace", event, data);
    },
    isEnabled(minLevel) {
      return rank >= (LEVEL_INDEX[minLevel] || 0);
    }
  };
}
function logDecision(logger, fields) {
  logger.debug(`decision:${fields.event}`, fields);
}
export {
  LEVELS,
  LEVEL_INDEX,
  createLogger,
  logCaughtError,
  logDecision,
  resolveLogLevel,
  serializeErrorForLog
};
