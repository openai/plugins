#!/usr/bin/env python3
"""Shared chart contract for generated analytics app packages."""

from __future__ import annotations

from typing import Any

from package_utils import ContractError

SUPPORTED_CHART_TYPES = {
    "area",
    "bar",
    "boxPlot",
    "funnel",
    "heatmap",
    "histogram",
    "horizontalBar",
    "horizontalStackedBar",
    "horizontalStackedBar100",
    "leaderboard",
    "line",
    "pie",
    "scatter",
    "sparkline",
    "stackedArea",
    "stackedBar",
    "stackedBar100",
    "waterfall",
}

ALLOWED_CHART_INTENTS = {
    "comparison",
    "composition",
    "custom",
    "decomposition",
    "distribution",
    "funnel",
    "lookup",
    "relationship",
    "status",
    "trend",
}

INTENT_COMPATIBLE_CHART_TYPES = {
    "comparison": {"bar", "horizontalBar", "leaderboard", "scatter"},
    "composition": {
        "horizontalStackedBar",
        "horizontalStackedBar100",
        "pie",
        "stackedArea",
        "stackedBar",
        "stackedBar100",
    },
    "decomposition": {"bar", "horizontalBar", "waterfall"},
    "distribution": {"boxPlot", "histogram"},
    "funnel": {"bar", "funnel", "horizontalBar"},
    "lookup": {"leaderboard"},
    "relationship": {"heatmap", "scatter"},
    "status": {"bar", "horizontalBar", "sparkline"},
    "trend": {"area", "bar", "line", "sparkline", "stackedArea"},
}

ALLOWED_COMPARISON_CONTEXT_FIELDS = {
    "baseline",
    "denominator",
    "grain",
    "normalization",
    "semanticFamily",
    "unit",
}

SINGLE_SERIES_CHART_TYPES = {
    "funnel",
    "histogram",
    "leaderboard",
    "pie",
    "sparkline",
    "waterfall",
}

INTRINSIC_MULTI_SERIES_CHART_TYPES = {
    "boxPlot",
    "heatmap",
    "horizontalStackedBar",
    "horizontalStackedBar100",
    "stackedArea",
    "stackedBar",
    "stackedBar100",
}

ALLOWED_SERIES_COLORS = {"blue", "purple", "green", "neutral", "orange", "yellow", "pink", "red"}
ALLOWED_SERIES_LINE_STYLES = {"solid", "dashed", "dotted"}
ALLOWED_SERIES_ROLES = {"actual", "baseline", "target", "forecast", "plan", "comparison"}
ALLOWED_PALETTE_KINDS = {"categorical", "sequential", "diverging", "semantic", "identity"}
ALLOWED_LEGEND_POSITIONS = {"bottom", "right"}
ALLOWED_LEGEND_SORTS = {"spec", "labelAsc", "labelDesc"}
ALLOWED_VALUE_LABEL_MODES = {"none", "auto", "all", "endpoints"}
LEADERBOARD_MAX_ROWS = 8
MIXED_SCALE_SERIES_RATIO = 25
MIXED_METRIC_AXIS_FIELDS = {"kpi", "measure", "metric"}
MIXED_METRIC_AXIS_MARKERS = ("kpi", "measure", "metric")
MIXED_METRIC_CHANGE_FIELD_MARKERS = (
    "change_pct",
    "delta_pct",
    "movement_pct",
    "wow_change",
    "wow_pct",
    "week_over_week",
    "week_over_week_change",
    "week_over_week_pct",
    "w_w_change",
)
DECOMPOSITION_FIELD_MARKERS = (
    "component",
    "decomp",
    "decomposition",
    "factor",
)


def validate_chart_type(chart_type: Any, path: str) -> str:
    if chart_type not in SUPPORTED_CHART_TYPES:
        raise ContractError(f"{path}.type must be one of {sorted(SUPPORTED_CHART_TYPES)}")
    return chart_type


def validate_chart_intent(intent: Any, path: str) -> str:
    if intent not in ALLOWED_CHART_INTENTS:
        raise ContractError(f"{path}.intent must be one of {sorted(ALLOWED_CHART_INTENTS)}")
    return intent


def require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{path} must be an object")
    return value


def optional_string(value: Any, path: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ContractError(f"{path} must be a string when present")


def optional_bool(value: Any, path: str) -> None:
    if value is not None and not isinstance(value, bool):
        raise ContractError(f"{path} must be a boolean when present")


def chart_intent(chart: dict[str, Any] | None) -> str | None:
    intent = chart.get("intent") if isinstance(chart, dict) else None
    return intent if isinstance(intent, str) and intent in ALLOWED_CHART_INTENTS else None


def field_looks_like_metric_definition(field: str) -> bool:
    normalized = field.lower().replace("-", "_")
    tokens = [token for token in normalized.split("_") if token]
    return any(
        marker in tokens or normalized.endswith(f"{marker}_name")
        for marker in MIXED_METRIC_AXIS_MARKERS
    )


def validate_comparison_context(context: Any, path: str) -> None:
    if context is None:
        return
    context_obj = require_object(context, path)
    for key, value in context_obj.items():
        if key not in ALLOWED_COMPARISON_CONTEXT_FIELDS:
            raise ContractError(
                f"{path}.{key} is not supported; use one of {sorted(ALLOWED_COMPARISON_CONTEXT_FIELDS)}"
            )
        optional_string(value, f"{path}.{key}")


def validate_chart_intent_metadata(
    chart: dict[str, Any],
    path: str,
    *,
    require: bool = False,
) -> str | None:
    intent_value = chart.get("intent")
    if intent_value is None:
        if require:
            raise ContractError(f"{path}.intent is required")
        return None

    intent = validate_chart_intent(intent_value, path)
    question = chart.get("question")
    rationale = chart.get("rationale")
    if require and (not isinstance(question, str) or not question.strip()):
        raise ContractError(f"{path}.question is required")
    if (require or intent == "custom") and (
        not isinstance(rationale, str) or not rationale.strip()
    ):
        raise ContractError(f"{path}.rationale is required")
    optional_string(question, f"{path}.question")
    optional_string(rationale, f"{path}.rationale")
    validate_comparison_context(chart.get("comparisonContext"), f"{path}.comparisonContext")
    chart_type = chart.get("type")
    if isinstance(chart_type, str):
        validate_chart_intent_compatibility(chart_type, chart, path)
    return intent


def validate_chart_intent_compatibility(chart_type: str, chart: dict[str, Any], path: str) -> None:
    intent = chart_intent(chart)
    if intent is None or intent == "custom":
        return
    compatible_types = INTENT_COMPATIBLE_CHART_TYPES.get(intent, set())
    if chart_type not in compatible_types:
        raise ContractError(
            f"{path}.type {chart_type!r} is not compatible with intent {intent!r}; "
            "choose a compatible chart family or use intent custom with a clear rationale"
        )


def chart_encoding(chart: dict[str, Any] | None, role: str) -> dict[str, Any]:
    encodings = chart.get("encodings") if isinstance(chart, dict) else None
    if not isinstance(encodings, dict):
        return {}
    encoding = encodings.get(role)
    return encoding if isinstance(encoding, dict) else {}


def chart_encoding_field(chart: dict[str, Any] | None, role: str) -> str:
    field = chart_encoding(chart, role).get("field")
    return field if isinstance(field, str) else ""


def chart_encoding_fields(chart: dict[str, Any] | None, role: str) -> list[str]:
    fields = chart_encoding(chart, role).get("fields")
    if not isinstance(fields, list):
        return []
    return [field for field in fields if isinstance(field, str) and field]


def chart_y_fields(chart: dict[str, Any]) -> list[str]:
    return chart_encoding_fields(chart, "y") or [chart_encoding_field(chart, "y")]


def chart_quality_warnings(
    chart: dict[str, Any],
    rows: list[Any] | None = None,
    *,
    sibling_charts: list[dict[str, Any]] | None = None,
) -> list[str]:
    warnings: list[str] = []
    intent = chart_intent(chart)
    if intent is None:
        warnings.append("Chart is missing intent metadata.")
    if not isinstance(chart.get("question"), str) or not chart.get("question", "").strip():
        warnings.append("Chart is missing the question it answers.")
    if not isinstance(chart.get("rationale"), str) or len(chart.get("rationale", "").strip()) < 24:
        warnings.append("Chart rationale is missing or too terse.")
    if intent in {"lookup", "status"}:
        warnings.append(f"Intent {intent} may be clearer as a table or KPI card than a chart.")
    if sibling_charts:
        question = str(chart.get("question", "")).strip().lower()
        signature = (
            intent,
            chart.get("dataset"),
            chart_encoding_field(chart, "x"),
            tuple(chart_y_fields(chart)),
        )
        for sibling in sibling_charts:
            if sibling is chart:
                continue
            sibling_question = str(sibling.get("question", "")).strip().lower()
            sibling_signature = (
                chart_intent(sibling),
                sibling.get("dataset"),
                chart_encoding_field(sibling, "x"),
                tuple(chart_y_fields(sibling)),
            )
            if question and question == sibling_question:
                warnings.append("Chart repeats another chart question.")
                break
            if signature == sibling_signature:
                warnings.append(
                    "Chart repeats another chart's intent, dataset, axis, and measures."
                )
                break
    if rows is not None and chart.get("type") == "leaderboard" and len(rows) > LEADERBOARD_MAX_ROWS:
        warnings.append(
            "Leaderboard uses a larger backing row set; verify omitted rows are not material."
        )
    return warnings


def validate_chart_presentation_options(chart: dict[str, Any], path: str) -> None:
    palette = chart.get("palette")
    if palette is not None:
        palette_obj = require_object(palette, f"{path}.palette")
        kind = palette_obj.get("kind")
        if kind not in ALLOWED_PALETTE_KINDS:
            raise ContractError(
                f"{path}.palette.kind must be one of {sorted(ALLOWED_PALETTE_KINDS)}"
            )
        optional_string(palette_obj.get("name"), f"{path}.palette.name")
        midpoint = palette_obj.get("midpoint")
        if midpoint is not None and as_number(midpoint) is None:
            raise ContractError(f"{path}.palette.midpoint must be a number when present")

    legend = chart.get("legend")
    if legend is not None:
        legend_obj = require_object(legend, f"{path}.legend")
        optional_bool(legend_obj.get("interactive"), f"{path}.legend.interactive")
        position = legend_obj.get("position")
        if position is not None and position not in ALLOWED_LEGEND_POSITIONS:
            raise ContractError(
                f"{path}.legend.position must be one of {sorted(ALLOWED_LEGEND_POSITIONS)}"
            )
        sort = legend_obj.get("sort")
        if sort is not None and sort not in ALLOWED_LEGEND_SORTS:
            raise ContractError(f"{path}.legend.sort must be one of {sorted(ALLOWED_LEGEND_SORTS)}")
        optional_string(legend_obj.get("title"), f"{path}.legend.title")

    labels = chart.get("labels")
    if labels is not None:
        labels_obj = require_object(labels, f"{path}.labels")
        values = labels_obj.get("values")
        if values is not None and values not in ALLOWED_VALUE_LABEL_MODES:
            raise ContractError(
                f"{path}.labels.values must be one of {sorted(ALLOWED_VALUE_LABEL_MODES)}"
            )

    reference_lines = chart.get("referenceLines")
    if reference_lines is not None:
        if not isinstance(reference_lines, list):
            raise ContractError(f"{path}.referenceLines must be a list when present")
        for idx, line in enumerate(reference_lines):
            line_obj = require_object(line, f"{path}.referenceLines[{idx}]")
            value = line_obj.get("value")
            if not isinstance(value, (int, float, str)) or isinstance(value, bool):
                raise ContractError(
                    f"{path}.referenceLines[{idx}].value must be a string or number"
                )
            axis = line_obj.get("axis")
            if axis is not None and axis not in {"x", "y"}:
                raise ContractError(f"{path}.referenceLines[{idx}].axis must be x or y")
            color = line_obj.get("color")
            if color is not None and color not in ALLOWED_SERIES_COLORS:
                raise ContractError(
                    f"{path}.referenceLines[{idx}].color must be one of "
                    f"{sorted(ALLOWED_SERIES_COLORS)}"
                )
            line_style = line_obj.get("lineStyle")
            if line_style is not None and line_style not in ALLOWED_SERIES_LINE_STYLES:
                raise ContractError(
                    f"{path}.referenceLines[{idx}].lineStyle must be one of "
                    f"{sorted(ALLOWED_SERIES_LINE_STYLES)}"
                )
            optional_string(line_obj.get("label"), f"{path}.referenceLines[{idx}].label")


def as_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def chart_palette_kind(chart: dict[str, Any] | None) -> str | None:
    palette = chart.get("palette") if isinstance(chart, dict) else None
    if not isinstance(palette, dict):
        return None
    kind = palette.get("kind")
    return kind if isinstance(kind, str) else None


def chart_has_fixed_measure_color(chart: dict[str, Any] | None) -> bool:
    color = chart_encoding(chart, "color")
    return isinstance(color.get("scale"), str) and bool(color.get("scale"))


def validate_chart_field_compatibility(
    chart_type: str,
    x_field: str,
    fields: list[str],
    path: str,
    chart: dict[str, Any] | None = None,
) -> None:
    if not field_looks_like_metric_definition(x_field):
        return

    if chart_type == "leaderboard":
        raise ContractError(
            f"{path} ranks metric definitions against each other; use KPI cards, "
            "a compact table, or a trend/share chart instead"
        )

    if chart_type not in {"bar", "horizontalBar"}:
        return

    if any(
        marker in field.lower() for field in fields for marker in MIXED_METRIC_CHANGE_FIELD_MARKERS
    ):
        if chart_palette_kind(chart) != "categorical" or chart_has_fixed_measure_color(chart):
            raise ContractError(
                f"{path} compares movement across different metric names; use "
                'palette.kind "categorical" and omit fixed measure colors so each metric '
                "bar is encoded as a distinct category"
            )


def validate_chart_data_compatibility(chart: dict[str, Any], rows: list[Any], path: str) -> None:
    chart_type = chart.get("type")
    validate_chart_intent_compatibility(chart_type, chart, path)
    fields = [field for field in chart_y_fields(chart) if field]
    if not rows:
        return

    for field in fields:
        has_numeric_value = any(
            isinstance(row, dict) and as_number(row.get(field)) is not None for row in rows
        )
        if not has_numeric_value:
            raise ContractError(
                f"{path}.encodings.y field {field!r} must reference a numeric "
                "dataset field with at least one numeric value"
            )

    if (
        chart_type not in SINGLE_SERIES_CHART_TYPES | INTRINSIC_MULTI_SERIES_CHART_TYPES
        and len(fields) > 1
    ):
        maxima = []
        for field in fields:
            max_abs = max(
                [
                    abs(value)
                    for row in rows
                    if isinstance(row, dict)
                    if (value := as_number(row.get(field))) is not None
                ],
                default=0,
            )
            if max_abs > 0:
                maxima.append(max_abs)
        if len(maxima) > 1 and max(maxima) / min(maxima) >= MIXED_SCALE_SERIES_RATIO:
            raise ContractError(
                f"{path} combines measures with materially different scales; "
                "split them into separate chart cards"
            )

    if chart_type not in {"bar", "horizontalBar", "leaderboard", "waterfall"} or len(fields) != 1:
        return

    chart_markers = " ".join(
        str(value).lower()
        for value in (
            chart.get("id", ""),
            chart.get("title", ""),
            chart.get("dataset", ""),
            chart_encoding_field(chart, "x"),
            fields[0],
        )
    )
    if not any(marker in chart_markers for marker in DECOMPOSITION_FIELD_MARKERS):
        return

    field = fields[0]
    values = [
        abs(value)
        for row in rows
        if isinstance(row, dict)
        if (value := as_number(row.get(field))) is not None and abs(value) > 0
    ]
    if len(values) > 1 and max(values) / min(values) >= MIXED_SCALE_SERIES_RATIO:
        raise ContractError(
            f"{path} renders decomposition components with materially different scales; "
            "split dominant and small factors into separate chart cards or use a compact table"
        )
