import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from chart_contract import (  # noqa: E402
    SUPPORTED_CHART_TYPES,
    chart_quality_warnings,
    validate_chart_data_compatibility,
    validate_chart_field_compatibility,
    validate_chart_intent_metadata,
    validate_chart_presentation_options,
    validate_chart_type,
)
from design_contract import validate_design_contract  # noqa: E402
from package_utils import (  # noqa: E402
    ContractError,
    copy_template,
    slugify,
    validate_no_sensitive_files,
    validate_relative_source_path,
)


def test_slugify_uses_stable_package_safe_default() -> None:
    assert slugify("Codex Workspace Adoption!", "fallback") == "codex-workspace-adoption"
    assert slugify("...", "fallback") == "fallback"


def test_copy_template_omits_generated_app_artifacts(tmp_path: Path) -> None:
    template = tmp_path / "template"
    template.mkdir()
    (template / "src").mkdir()
    (template / "src" / "App.tsx").write_text("export {};\n", encoding="utf-8")
    (template / "dist").mkdir()
    (template / "dist" / "bundle.js").write_text("generated\n", encoding="utf-8")
    (template / "node_modules").mkdir()
    (template / "node_modules" / "package.js").write_text("generated\n", encoding="utf-8")

    output = tmp_path / "output"
    copy_template(template, output)

    assert (output / "src" / "App.tsx").exists()
    assert not (output / "dist").exists()
    assert not (output / "node_modules").exists()


def test_copy_template_materializes_symlinked_runtime_files(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    template = tmp_path / "template"
    runtime.mkdir()
    template.mkdir()
    (runtime / "tokens.css").write_text(":root { --ds-surface: #fff; }\n", encoding="utf-8")
    (template / "tokens.css").symlink_to(runtime / "tokens.css")

    output = tmp_path / "output"
    copy_template(template, output)

    assert (output / "tokens.css").read_text(encoding="utf-8") == ":root { --ds-surface: #fff; }\n"
    assert not (output / "tokens.css").is_symlink()


def test_validate_relative_source_path_stays_inside_package(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="inside the analytics app package"):
        validate_relative_source_path(tmp_path, "../queries.sql", "manifest.sources[0]")


def test_validate_relative_source_path_uses_custom_package_label(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="inside the dashboard package"):
        validate_relative_source_path(
            tmp_path, "../queries.sql", "manifest.sources[0]", "dashboard package"
        )


def test_validate_no_sensitive_files_rejects_private_keys(tmp_path: Path) -> None:
    (tmp_path / "id_rsa").write_text("secret\n", encoding="utf-8")

    with pytest.raises(ContractError, match="sensitive files"):
        validate_no_sensitive_files(tmp_path, "report")


def test_shared_chart_contract_rejects_removed_or_malformed_chart_types() -> None:
    assert "bullet" not in SUPPORTED_CHART_TYPES
    assert validate_chart_type("line", "manifest.charts[0]") == "line"

    with pytest.raises(ContractError, match="must be one of"):
        validate_chart_type("bullet", "manifest.charts[0]")


def test_shared_chart_contract_requires_intent_and_chart_type_fit() -> None:
    trend_chart = {
        "id": "active_users",
        "title": "Active users trend",
        "type": "line",
        "intent": "trend",
        "question": "How are active users moving by week?",
        "rationale": "A line chart fits a weekly time series and makes trend shape easy to compare.",
        "dataset": "active_users",
        "encodings": {"x": {"field": "week"}, "y": {"field": "wau"}},
    }
    assert (
        validate_chart_intent_metadata(trend_chart, "manifest.charts[0]", require=True) == "trend"
    )

    with pytest.raises(ContractError, match="intent is required"):
        validate_chart_intent_metadata(
            {**trend_chart, "intent": None}, "manifest.charts[0]", require=True
        )

    with pytest.raises(ContractError, match="not compatible"):
        validate_chart_intent_metadata(
            {**trend_chart, "intent": "distribution"}, "manifest.charts[0]", require=True
        )

    custom_chart = {
        **trend_chart,
        "intent": "custom",
        "rationale": "The user explicitly asked for this unusual line-based diagnostic view.",
    }
    assert (
        validate_chart_intent_metadata(custom_chart, "manifest.charts[0]", require=True) == "custom"
    )


def test_shared_chart_contract_allows_grouped_scatter_encodings() -> None:
    validate_chart_data_compatibility(
        {
            "id": "relationship",
            "title": "Activation and retention by segment",
            "type": "scatter",
            "dataset": "segments",
            "encodings": {
                "x": {"field": "users"},
                "y": {"field": "activation"},
                "color": {"field": "segment"},
            },
            "combinationRationale": "Color groups segment-level relationships without pivoting the Y measure.",
        },
        [
            {"segment": "A", "users": 100, "activation": 0.45},
            {"segment": "B", "users": 240, "activation": 0.58},
        ],
        "manifest.charts[0]",
    )


def test_shared_chart_contract_allows_hardened_presentation_options() -> None:
    validate_chart_presentation_options(
        {
            "id": "usage-trend",
            "palette": {"kind": "semantic", "name": "actual-vs-forecast"},
            "legend": {
                "interactive": True,
                "position": "bottom",
                "sort": "labelAsc",
                "title": "Segment",
            },
            "labels": {"values": "endpoints"},
            "referenceLines": [
                {
                    "axis": "y",
                    "color": "neutral",
                    "label": "Target",
                    "lineStyle": "dashed",
                    "value": 100,
                }
            ],
        },
        "manifest.charts[0]",
    )


def test_shared_chart_contract_rejects_invalid_presentation_options() -> None:
    with pytest.raises(ContractError, match="palette.kind"):
        validate_chart_presentation_options(
            {"palette": {"kind": "rainbow"}},
            "manifest.charts[0]",
        )

    with pytest.raises(ContractError, match="labels.values"):
        validate_chart_presentation_options(
            {"labels": {"values": "everywhere"}},
            "manifest.charts[0]",
        )

    with pytest.raises(ContractError, match="referenceLines\\[0\\].color"):
        validate_chart_presentation_options(
            {"referenceLines": [{"value": 0, "color": "brand"}]},
            "manifest.charts[0]",
        )


def test_shared_chart_contract_requires_categorical_palette_for_metric_movement() -> None:
    with pytest.raises(ContractError, match="distinct category"):
        validate_chart_field_compatibility(
            "bar",
            "metric",
            ["change_pct"],
            "manifest.charts[0]",
        )

    validate_chart_field_compatibility(
        "horizontalBar",
        "metric",
        ["wow_change"],
        "manifest.charts[0]",
        {"palette": {"kind": "categorical"}},
    )

    with pytest.raises(ContractError, match="omit fixed measure colors"):
        validate_chart_field_compatibility(
            "horizontalBar",
            "metric",
            ["wow_change"],
            "manifest.charts[0]",
            {"palette": {"kind": "categorical"}, "encodings": {"color": {"scale": "green"}}},
        )

    with pytest.raises(ContractError, match="ranks metric definitions"):
        validate_chart_field_compatibility(
            "leaderboard",
            "metric",
            ["latest_value"],
            "manifest.charts[1]",
        )


def test_shared_chart_contract_rejects_latest_active_user_leaderboard() -> None:
    chart = {
        "id": "latest_active_user_values",
        "title": "Latest DAU WAU MAU values",
        "type": "leaderboard",
        "intent": "lookup",
        "question": "What are the latest DAU, WAU, and MAU values?",
        "rationale": "This intentionally bad fixture should be rejected before it ranks KPI definitions.",
        "dataset": "latest_active_users",
        "encodings": {"x": {"field": "metric_name"}, "y": {"field": "latest_value"}},
    }

    with pytest.raises(ContractError, match="ranks metric definitions"):
        validate_chart_field_compatibility(
            "leaderboard",
            chart["encodings"]["x"]["field"],
            [chart["encodings"]["y"]["field"]],
            "manifest.charts[0]",
            chart,
        )


def test_shared_chart_quality_warnings_flag_redundant_questions() -> None:
    chart = {
        "id": "wau_trend",
        "title": "WAU trend",
        "type": "line",
        "intent": "trend",
        "question": "How is WAU trending?",
        "rationale": "A line chart is the right family for a weekly user metric over time.",
        "dataset": "active_users",
        "encodings": {"x": {"field": "week"}, "y": {"field": "wau"}},
    }
    sibling = {**chart, "id": "wau_trend_copy"}

    warnings = chart_quality_warnings(chart, sibling_charts=[chart, sibling])

    assert "Chart repeats another chart question." in warnings


def test_shared_chart_contract_rejects_mixed_scale_measures() -> None:
    with pytest.raises(ContractError, match="materially different scales"):
        validate_chart_data_compatibility(
            {
                "id": "movement",
                "title": "Movement",
                "type": "line",
                "dataset": "trend",
                "encodings": {"x": {"field": "week"}, "y": {"fields": ["large", "small"]}},
            },
            [
                {"week": "W1", "large": 1_000_000, "small": 10},
                {"week": "W2", "large": 1_200_000, "small": 12},
            ],
            "manifest.charts[0]",
        )


def test_shared_chart_contract_rejects_non_numeric_measure_fields() -> None:
    with pytest.raises(ContractError, match="must reference a numeric dataset field"):
        validate_chart_data_compatibility(
            {
                "id": "product_line_share",
                "title": "Product-line share by country",
                "type": "bar",
                "dataset": "product_line_share",
                "encodings": {"x": {"field": "country_name"}, "y": {"field": "product_line"}},
            },
            [
                {"country_name": "India", "product_line": "Consumer", "share_pct": 71},
                {"country_name": "India", "product_line": "API", "share_pct": 18},
            ],
            "manifest.charts[0]",
        )


def test_design_contract_validates_template_file() -> None:
    template_root = Path(__file__).resolve().parents[3]

    validate_design_contract(template_root)


def test_design_contract_requires_frontmatter(tmp_path: Path) -> None:
    (tmp_path / "DESIGN.md").write_text("# Missing front matter\n", encoding="utf-8")

    with pytest.raises(ContractError, match="front matter"):
        validate_design_contract(tmp_path)


def test_design_contract_requires_design_tokens(tmp_path: Path) -> None:
    (tmp_path / "DESIGN.md").write_text(
        """---
name: Example
description: Generic design file
colors: {}
typography: {}
spacing: {}
rounded: {}
surfaces: {}
components:
  top-bar: {}
  metric-card: {}
  report-block: {}
  chart-block: {}
  table-list: {}
  popover-menu: {}
implementation: {}
---

# Example

## Overview

Generated artifacts are customizable.

## Colors

Generic source.

## Typography

Generic tokens.

## Layout

Generic surfaces.

## Elevation & Depth

Generic elevation.

## Shapes

Generic shapes.

## Components

Generic components.

## Do's and Don'ts

Generic visuals.
""",
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="design token"):
        validate_design_contract(tmp_path)
