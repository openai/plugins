#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const MARKER = "const D = __DATA_JSON__;";

function usage() {
  console.error(
    "Usage: node scripts/inject-template.mjs <template.html> <data.json> <output.html>"
  );
}

const [templatePath, dataPath, outputPath] = process.argv.slice(2);

if (!templatePath || !dataPath || !outputPath) {
  usage();
  process.exit(2);
}

const [template, rawData] = await Promise.all([
  readFile(templatePath, "utf8"),
  readFile(dataPath, "utf8"),
]);

const markerCount = template.split(MARKER).length - 1;
if (markerCount !== 1) {
  throw new Error(
    `Expected exactly one template marker (${MARKER}); found ${markerCount}.`
  );
}

const data = JSON.parse(rawData);
validateData(data);

const serializedData = JSON.stringify(data, null, 2)
  .replaceAll("<", "\\u003c")
  .replaceAll("\u2028", "\\u2028")
  .replaceAll("\u2029", "\\u2029");
const injected = template.replace(MARKER, `const D = ${serializedData};`);

await writeFile(outputPath, injected, "utf8");
const resolvedOutputPath = path.resolve(outputPath);
console.log(`Output: ${resolvedOutputPath}`);
console.log("Validation: passed");
console.log(`Bytes: ${Buffer.byteLength(injected, "utf8")}`);

function validateData(data) {
  const errors = [];

  requirePlainObject(data, "D", errors);
  if (!errors.length) {
    validateMeta(data.meta, errors);
    validateOverviewGroups(data.overview_groups, errors);
    validateDisplayRows(data.portfolio_characteristics, "portfolio_characteristics", "label", errors);
    validateAssetAllocation(data.asset_allocation, errors);
    validateStyle(data.equity_style_a, "equity_style_a", errors, true);
    validateStyle(data.equity_style_b, "equity_style_b", errors, true);
    validateSectorRows(data.equity_sectors, "equity_sectors", errors, true);
    validateSectorRows(data.equity_regions, "equity_regions", errors, false);
    validateStyle(data.fi_style_a, "fi_style_a", errors, false);
    validateStyle(data.fi_style_b, "fi_style_b", errors, false);
    validateSectorRows(data.fi_sectors, "fi_sectors", errors, false);
    validateSectorRows(data.fi_maturity, "fi_maturity", errors, false);
    validateGrowthChart(data.growth_chart, errors);
    validateComparisonRows(data.trailing_returns, "trailing_returns", "period", errors);
    validateAnnualReturns(data.annual_returns, errors);
    validateCategoryRankings(data.category_rankings, errors);
    validateRisk(data.risk, errors);
    validateRiskReturn(data.risk_return, errors);
    validateDisplayRows(data.ratings, "ratings", "metric", errors);
    requireTextWithinWordLimit(data.analyst_a, "analyst_a", 50, errors);
    requireTextWithinWordLimit(data.analyst_b, "analyst_b", 50, errors);
    requireTextWithinWordLimit(data.narrative_p1, "narrative_p1", 75, errors);
    requireTextWithinWordLimit(data.narrative_p2, "narrative_p2", 75, errors);
    requireTextWithinWordLimit(data.narrative_p3, "narrative_p3", 75, errors);
  }

  if (errors.length) {
    throw new Error(`Invalid comparison data:\n- ${errors.join("\n- ")}`);
  }
}

function validateMeta(meta, errors) {
  requirePlainObject(meta, "meta", errors);
  if (!isPlainObject(meta)) return;

  for (const key of ["ticker_a", "name_a", "ticker_b", "name_b"]) {
    requireString(meta[key], `meta.${key}`, errors);
  }
  requireIsoDate(meta.report_date, "meta.report_date", errors);
  requireIsoDateOrNA(meta.data_as_of_date, "meta.data_as_of_date", errors);
  requireBoolean(meta.cross_category_warning, "meta.cross_category_warning", errors);
}

function validateOverviewGroups(groups, errors) {
  requireArray(groups, "overview_groups", errors);
  if (!Array.isArray(groups)) return;

  groups.forEach((group, groupIndex) => {
    requirePlainObject(group, `overview_groups.${groupIndex}`, errors);
    if (!isPlainObject(group)) return;
    requireString(group.group, `overview_groups.${groupIndex}.group`, errors);
    requireArray(group.rows, `overview_groups.${groupIndex}.rows`, errors);
    if (!Array.isArray(group.rows)) return;
    group.rows.forEach((row, rowIndex) => {
      requirePlainObject(row, `overview_groups.${groupIndex}.rows.${rowIndex}`, errors);
      if (!isPlainObject(row)) return;
      requireString(row.label, `overview_groups.${groupIndex}.rows.${rowIndex}.label`, errors);
      requireDisplayValue(row.a, `overview_groups.${groupIndex}.rows.${rowIndex}.a`, errors);
      requireDisplayValue(row.b, `overview_groups.${groupIndex}.rows.${rowIndex}.b`, errors);
    });
  });
}

function validateAssetAllocation(rows, errors) {
  validateComparisonRows(rows, "asset_allocation", "label", errors);
  if (!Array.isArray(rows)) return;

  const expectedLabels = ["US Equity", "Non-US Equity", "Bonds", "Cash", "Other"];
  if (rows.length !== expectedLabels.length) {
    errors.push(`asset_allocation must contain exactly ${expectedLabels.length} rows`);
    return;
  }
  rows.forEach((row, index) => {
    if (isPlainObject(row) && row.label !== expectedLabels[index]) {
      errors.push(`asset_allocation.${index}.label must be "${expectedLabels[index]}"`);
    }
  });
}

function validateStyle(style, label, errors, allowEquityFields) {
  requireNullablePlainObject(style, label, errors);
  if (!isPlainObject(style)) return;

  const cellNames = allowEquityFields
    ? [
        "large_value", "large_blend", "large_growth",
        "mid_value", "mid_blend", "mid_growth",
        "small_value", "small_blend", "small_growth",
      ]
    : [
        "limited_high", "moderate_high", "extensive_high",
        "limited_medium", "moderate_medium", "extensive_medium",
        "limited_low", "moderate_low", "extensive_low",
      ];

  for (const key of cellNames) {
    requireNullableInteger(style[key], `${label}.${key}`, errors);
  }
  if (style.portfolio_analyzed != null) {
    requireFiniteNumber(style.portfolio_analyzed, `${label}.portfolio_analyzed`, errors);
  }
}

function validateSectorRows(rows, label, errors, grouped) {
  requireNullableArray(rows, label, errors);
  if (!Array.isArray(rows)) return;

  rows.forEach((row, index) => {
    const rowLabel = `${label}.${index}`;
    requirePlainObject(row, rowLabel, errors);
    if (!isPlainObject(row)) return;
    if (grouped) requireString(row.group, `${rowLabel}.group`, errors);
    requireString(row.sector, `${rowLabel}.sector`, errors);
    requireNullableNumber(row.a, `${rowLabel}.a`, errors);
    requireNullableNumber(row.b, `${rowLabel}.b`, errors);
  });
}

function validateComparisonRows(rows, label, keyName, errors) {
  requireArray(rows, label, errors);
  if (!Array.isArray(rows)) return;

  rows.forEach((row, index) => {
    const rowLabel = `${label}.${index}`;
    requirePlainObject(row, rowLabel, errors);
    if (!isPlainObject(row)) return;
    requireString(row[keyName], `${rowLabel}.${keyName}`, errors);
    requireNullableNumber(row.a, `${rowLabel}.a`, errors);
    requireNullableNumber(row.b, `${rowLabel}.b`, errors);
  });
}

function validateAnnualReturns(rows, errors) {
  requireArray(rows, "annual_returns", errors);
  if (!Array.isArray(rows)) return;

  rows.forEach((row, index) => {
    const label = `annual_returns.${index}`;
    requirePlainObject(row, label, errors);
    if (!isPlainObject(row)) return;
    requireInteger(row.year, `${label}.year`, errors);
    requireNullableNumber(row.a, `${label}.a`, errors);
    requireNullableNumber(row.b, `${label}.b`, errors);
  });
}

function validateCategoryRankings(rankings, errors) {
  requirePlainObject(rankings, "category_rankings", errors);
  if (!isPlainObject(rankings)) return;
  validateComparisonRows(rankings.trailing, "category_rankings.trailing", "period", errors);
  const annual = rankings.annual;
  requireArray(annual, "category_rankings.annual", errors);
  if (!Array.isArray(annual)) return;
  annual.forEach((row, index) => {
    const label = `category_rankings.annual.${index}`;
    requirePlainObject(row, label, errors);
    if (!isPlainObject(row)) return;
    requireInteger(row.year, `${label}.year`, errors);
    requireNullableNumber(row.a, `${label}.a`, errors);
    requireNullableNumber(row.b, `${label}.b`, errors);
  });
}

function validateRiskReturn(rows, errors) {
  if (rows == null) return;
  requireArray(rows, "risk_return", errors);
  if (!Array.isArray(rows)) return;

  rows.forEach((row, rowIndex) => {
    requirePlainObject(row, `risk_return.${rowIndex}`, errors);
    if (!isPlainObject(row)) return;
    requireString(row.period, `risk_return.${rowIndex}.period`, errors);
    for (const key of ["a_return", "a_risk", "b_return", "b_risk"]) {
      requireNullableNumber(row[key], `risk_return.${rowIndex}.${key}`, errors);
    }
  });
}

function validateRisk(risk, errors) {
  requirePlainObject(risk, "risk", errors);
  if (!isPlainObject(risk)) return;

  for (const period of Object.keys(risk)) {
    if (!["1y", "3y", "5y", "10y"].includes(period)) {
      errors.push(`risk has unsupported period "${period}"`);
      continue;
    }
    requireArray(risk[period], `risk.${period}`, errors);
    if (!Array.isArray(risk[period])) continue;
    risk[period].forEach((row, index) => {
      const label = `risk.${period}.${index}`;
      requirePlainObject(row, label, errors);
      if (!isPlainObject(row)) return;
      requireString(row.metric, `${label}.metric`, errors);
      requireNullableNumber(row.a, `${label}.a`, errors);
      requireNullableNumber(row.b, `${label}.b`, errors);
    });
  }
}

function validateGrowthChart(growthChart, errors) {
  requirePlainObject(growthChart, "growth_chart", errors);
  if (!isPlainObject(growthChart)) return;

  const dates = growthChart.Date;
  requireArray(dates, "growth_chart.Date", errors);
  if (!Array.isArray(dates)) return;
  dates.forEach((date, index) => requireIsoDate(date, `growth_chart.Date.${index}`, errors));

  const seriesKeys = Object.keys(growthChart).filter(key => key !== "Date");
  if (seriesKeys.length !== 2) {
    errors.push("growth_chart must include exactly two fund series");
  }

  for (const key of seriesKeys) {
    requireArray(growthChart[key], `growth_chart.${key}`, errors);
    if (Array.isArray(growthChart[key]) && growthChart[key].length !== dates.length) {
      errors.push(
        `growth_chart.${key} length ${growthChart[key].length} does not match Date length ${dates.length}`
      );
    }
    if (Array.isArray(growthChart[key])) {
      growthChart[key].forEach((value, index) =>
        requireNullableNumber(value, `growth_chart.${key}.${index}`, errors)
      );
    }
  }
}

function validateDisplayRows(rows, label, keyName, errors) {
  requireArray(rows, label, errors);
  if (!Array.isArray(rows)) return;

  rows.forEach((row, index) => {
    const rowLabel = `${label}.${index}`;
    requirePlainObject(row, rowLabel, errors);
    if (!isPlainObject(row)) return;
    requireString(row[keyName], `${rowLabel}.${keyName}`, errors);
    requireDisplayValue(row.a, `${rowLabel}.a`, errors);
    requireDisplayValue(row.b, `${rowLabel}.b`, errors);
  });
}

function requireString(value, label, errors) {
  if (typeof value !== "string" || value.trim() === "") {
    errors.push(`${label} must be a non-empty string`);
  }
}

function requireTextWithinWordLimit(value, label, maxWords, errors) {
  requireString(value, label, errors);
  if (typeof value !== "string" || value.trim() === "") return;
  const wordCount = value.trim().split(/\s+/u).length;
  if (wordCount > maxWords) {
    errors.push(`${label} must contain at most ${maxWords} words; found ${wordCount}`);
  }
}

function requireIsoDate(value, label, errors) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    errors.push(`${label} must be a valid YYYY-MM-DD date`);
    return;
  }
  const parsed = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) {
    errors.push(`${label} must be a valid YYYY-MM-DD date`);
  }
}

function requireIsoDateOrNA(value, label, errors) {
  if (value === "N/A") return;
  requireIsoDate(value, label, errors);
}

function requireBoolean(value, label, errors) {
  if (typeof value !== "boolean") {
    errors.push(`${label} must be a boolean`);
  }
}

function requireFiniteNumber(value, label, errors) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    errors.push(`${label} must be a finite number`);
  }
}

function requireNullableNumber(value, label, errors) {
  if (value !== null) requireFiniteNumber(value, label, errors);
}

function requireInteger(value, label, errors) {
  if (!Number.isInteger(value)) {
    errors.push(`${label} must be an integer`);
  }
}

function requireNullableInteger(value, label, errors) {
  if (value !== null && !Number.isInteger(value)) {
    errors.push(`${label} must be null or an integer`);
  }
}

function requireDisplayValue(value, label, errors) {
  if (
    value !== null &&
    typeof value !== "string" &&
    (typeof value !== "number" || !Number.isFinite(value))
  ) {
    errors.push(`${label} must be a string, finite number, or null`);
  }
}

function requireArray(value, label, errors) {
  if (!Array.isArray(value)) {
    errors.push(`${label} must be an array`);
  }
}

function requireNullableArray(value, label, errors) {
  if (value !== null && !Array.isArray(value)) {
    errors.push(`${label} must be null or an array`);
  }
}

function requirePlainObject(value, label, errors) {
  if (!isPlainObject(value)) {
    errors.push(`${label} must be an object`);
  }
}

function requireNullablePlainObject(value, label, errors) {
  if (value !== null && !isPlainObject(value)) {
    errors.push(`${label} must be null or an object`);
  }
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
