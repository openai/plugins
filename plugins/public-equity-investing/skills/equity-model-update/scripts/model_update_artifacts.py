from __future__ import annotations


def build_change_log(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    change_rows: list[dict[str, str]] = []
    counter = 1
    change_actions = {"update", "add_or_map", "input_required"}
    for row in source_rows:
        if row["update_action"] not in change_actions:
            continue
        status = "ready_for_review"
        if row.get("applied_to_workbook") == "yes":
            status = "applied_to_copy"
        elif row["issue_flags"] or row.get("blocked_reason"):
            status = "blocked"
        change_rows.append(
            {
                "change_id": f"CHG-{counter:03d}",
                "company": row["company"],
                "ticker": row["ticker"],
                "fiscal_period": row["fiscal_period"],
                "model_section": row["model_section"],
                "model_line": row["model_line"],
                "workbook_sheet": row.get("workbook_sheet", ""),
                "workbook_cell": row.get("workbook_cell", ""),
                "current_model_value": row["current_model_value"],
                "proposed_model_value": row["proposed_model_value"],
                "delta": row["delta"],
                "delta_pct": row["delta_pct"],
                "update_action": row["update_action"],
                "change_reason": "source-to-model refresh mapping",
                "source_id": row["source_id"],
                "confidence": row["confidence"],
                "status": status,
                "applied_to_workbook": row.get("applied_to_workbook", ""),
                "blocked_reason": row.get("blocked_reason", ""),
                "requires_model_audit_tieout": "yes",
            }
        )
        counter += 1
    return change_rows


def build_tieout_checklist(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = [
        {
            "check_id": "TIE-001",
            "check_area": "model_audit_handoff",
            "related_model_line": "all changed lines",
            "workbook_sheet": "all workbook targets",
            "workbook_cell": "",
            "check_description": "Run model-audit-tieout before relying on workbook formulas.",
            "owner": "model owner",
            "status": "required",
            "handoff_skill": "model-audit-tieout",
        }
    ]
    for idx, row in enumerate(source_rows, start=2):
        treatment = row.get("mapping_treatment", "")
        if treatment == "reference_only":
            check_status = "reference_only"
            check_description = (
                f"Confirm {row['model_line']} is retained only as a cited reference "
                f"from {row['source_id']}."
            )
        else:
            check_status = "blocked" if row["issue_flags"] or row.get("blocked_reason") else "open"
            check_description = f"Verify {row['model_line']} maps to source {row['source_id']}."
        checks.append(
            {
                "check_id": f"TIE-{idx:03d}",
                "check_area": "source_to_model",
                "related_model_line": row["model_line"],
                "workbook_sheet": row.get("workbook_sheet", ""),
                "workbook_cell": row.get("workbook_cell", ""),
                "check_description": check_description,
                "owner": "analyst",
                "status": check_status,
                "handoff_skill": "model-audit-tieout",
            }
        )
        if row["freshness_status"] in {"stale", "unknown"}:
            checks.append(
                {
                    "check_id": f"TIE-{idx:03d}F",
                    "check_area": "freshness",
                    "related_model_line": row["model_line"],
                    "workbook_sheet": row.get("workbook_sheet", ""),
                    "workbook_cell": row.get("workbook_cell", ""),
                    "check_description": f"Refresh/caveat {row['model_line']}; freshness is {row['freshness_status']}.",
                    "owner": "analyst",
                    "status": "open",
                    "handoff_skill": "financial-source-of-truth",
                }
            )
    return checks
