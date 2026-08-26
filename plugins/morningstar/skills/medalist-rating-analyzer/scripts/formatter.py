"""
Response Formatter Tool  (self-contained — no external project dependencies)

Transforms the raw API JSON into human-readable text for each section
described in the Medalist Rating Analyzer project definition.

Output structure mirrors the Medalist Rating Analyzer screen layout:
  1) Product Info
  2) Overall Rating Breakdown
     - Historical Ratings
     - Price Score
  3) Pillar Analysis
     - Pillar assignment explanation
     - People  (Algorithmic People Score Derivation + Pillar Score Characteristics)
     - Process (Algorithmic Process Score Derivation)
     - Parent  (Algorithmic Parent Score Derivation)
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import date as _date, datetime as _datetime

try:
    from dateutil import parser as _dateutil_parser
    _HAS_DATEUTIL = True
except ImportError:
    _dateutil_parser = None
    _HAS_DATEUTIL = False

# ── Inlined constants from Morningstar Medalist Rating Methodology ────────────

PILLAR_ASSIGNMENT_INTRO: str = (
    "Morningstar assigns pillars ratings in one of four ways: "
    "(1) Directly, by Analysts; (2) Indirectly, by Analyst; "
    "(3) Directly, by Algorithm; (4) Indirectly, by Algorithm. "
    "Use this section to learn more about how a specific product's "
    "pillar ratings were assigned."
)

# ── Disclosure text mapping ───────────────────────────────────────────────────

DISCLOSURE_TEXTS: Dict[str, str] = {
    "Issuer Initiated Rating": (
        "In Australia and New Zealand only, starting from June 2026, Morningstar may receive a fee from "
        "product issuers for preparing Morningstar Medalist Rating on their financial product(s) domiciled "
        'in Australia or New Zealand (an "Issuer Initiated Rating"). An Issuer Initiated Rating will apply '
        "to a strategy and its associated share classes. Morningstar will clearly identify each Issuer "
        "Initiated Rating on the front page of the report and will provide disclosure relating to the party "
        "that has paid the associated fee. Fees for an Issuer Initiated Rating are not linked to the rating "
        "outcome, and the paying entity has no influence over the analytical process or rating outcome."
    ),
    "Tracks Morningstar Index": (
        "Certain managed investments use indexes created by and licensed from Morningstar, Inc., and its "
        "subsidiaries as their tracking index. We mitigate any actual or potential conflicts of interest "
        "arising from these activities by maintaining and enforcing information barriers, including both "
        "technological and non-technological controls, and conducting ongoing monitoring through Morningstar's "
        "Compliance department. Morningstar will clearly identify manager research related to such indexes on "
        "the front page of the report. Morningstar does not provide qualitative ratings or opinions for "
        "investments managed by Morningstar or managed investments that track Morningstar indexes that "
        "incorporate discretionary inputs assigned by Morningstar employees on an ongoing basis, such as "
        "Morningstar Economic Moat Ratings, or ESG Ratings."
    ),
}

PEOPLE_METHODOLOGY_NOTE: str = (
    "See the full methodology for further details on the scaling and "
    "postprocessing steps utilized for algorithmic People score assignment."
)

PROCESS_METHODOLOGY_NOTE: str = (
    "See the full methodology for further details on the scaling and "
    "postprocessing steps utilized for algorithmic Process score assignment."
)

PILLAR_SCORE_CHARACTERISTICS: str = (
    "**Pillar Score Characteristics**\n\n"
    "• **High** — top-tier conviction.\n"
    "• **Above Average** — better than most peers.\n"
    "• **Average** — in line with peers.\n"
    "• **Below Average** — weaker than peers.\n"
    "• **Low** — bottom-tier.\n\n"
    "The numeric Parent score uses a −2 to +2 range."
)

PILLAR_SCORE_SCALE_LINE: str = (
    "Pillar score scale: High (+2), Above Average (+1), "
    "Average (0), Below Average (-1), Low (-2)."
)


# ── Date utilities ────────────────────────────────────────────────────────────

def _get_record_date(record: Dict) -> str:
    """Return the date string from a record, preferring EndDate then Date."""
    return str(record.get("EndDate") or record.get("Date") or "")


def parse_date(date_str) -> Optional[_date]:
    """
    Parse a flexible date string into a Python date object.

    Accepted formats (examples):
      • ISO        — "2020-01-01", "2020-01"
      • US         — "1/1/2020", "06/01/2020"
      • Natural    — "June 1 2020", "Jan 2020", "2020"
      • Special    — "now", "today"

    Returns None when the input is None, empty, or cannot be parsed.
    """
    if not date_str:
        return None
    s = str(date_str).strip().lower()
    if s in ("now", "today"):
        return _date.today()
    if _HAS_DATEUTIL:
        try:
            return _dateutil_parser.parse(str(date_str), default=_datetime(1900, 1, 1)).date()
        except Exception:
            pass
    # Built-in fallback for the most common explicit formats
    from datetime import datetime
    for fmt in (
        "%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d",
        "%B %d %Y", "%b %d %Y", "%B %Y", "%b %Y", "%Y-%m", "%Y",
    ):
        try:
            return datetime.strptime(str(date_str).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _filter_by_date(
    records: List[Dict],
    start: Optional[_date] = None,
    end: Optional[_date] = None,
) -> List[Dict]:
    """
    Return records whose date falls within [start, end] (inclusive).
    Records with no parseable date are always kept.
    A None bound means unbounded on that side.
    """
    if not records or (start is None and end is None):
        return records
    out = []
    for r in records:
        ds = _get_record_date(r)
        if not ds:
            out.append(r)
            continue
        rd = parse_date(ds)
        if rd is None:
            out.append(r)
            continue
        if start and rd < start:
            continue
        if end and rd > end:
            continue
        out.append(r)
    return out


def _date_range_label(start: Optional[_date], end: Optional[_date]) -> str:
    """Return a short label like ' — from 2020-01-01 to 2022-12-31'."""
    if start and end:
        return " — {} to {}".format(start, end)
    if start:
        return " — from {}".format(start)
    if end:
        return " — up to {}".format(end)
    return ""


def _resolve_dates(
    start_date=None, end_date=None
) -> Tuple[Optional[_date], Optional[_date]]:
    """Accept string or date objects and return a (start, end) pair of date objects."""
    s = start_date if isinstance(start_date, _date) else parse_date(start_date)
    e = end_date   if isinstance(end_date,   _date) else parse_date(end_date)
    return s, e


def _display_value(value) -> str:
    """Render values exactly as stored, using N/A only for missing values."""
    return str(value) if value is not None else "N/A"


def _display_rating_type(value) -> str:
    """Render assignment type labels without surrounding brackets."""
    if value is None:
        return "N/A"
    text = str(value).strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    return text or "N/A"


def _display_pillar_value(value) -> str:
    """Render pillar labels without Morningstar's ^Q suffix marker."""
    if value is None:
        return "N/A"
    text = re.sub(r"\s*\^Q\s*", "", str(value)).strip()
    return text or "N/A"


def _score_with_type(score_val, type_val) -> str:
    """Render a score followed by its assignment type, without bracket notation."""
    score_str = _display_pillar_value(score_val)
    if not type_val:
        return score_str
    return f"{score_str}  {_display_rating_type(type_val)}"


def _latest(records: List[Dict], date_key: str = "EndDate") -> Optional[Dict]:
    """Return the record with the most recent date (handles both EndDate and Date keys)."""
    if not records:
        return None
    return sorted(records, key=lambda r: _get_record_date(r), reverse=True)[0]


# ═══════════════════════════════════════════════════════════════════════════
# Section formatters — each returns a plain-text block
# ═══════════════════════════════════════════════════════════════════════════

class Formatter:
    """Converts raw API data into readable text per project-definition section."""

    # ── Disclosure wrapper ────────────────────────────────────────────────
    @staticmethod
    def _with_disclosure(data: Dict, body: str) -> str:
        """Prepend the mandatory disclosure text (if applicable) to a rendered body.

        Every section method routes its return value through this so the
        legally-required disclosure can never be skipped on an early-return
        path (e.g. "no data available" branches).
        """
        disclosure = Formatter._format_disclosure(data)
        if disclosure:
            return disclosure + "\n\n" + body
        return body

    # ── Fund identity header ──────────────────────────────────────────────
    @staticmethod
    def fund_header(data: Dict) -> str:
        """
        Return a bold one-liner identifying the fund, e.g.:

            **Vanguard 500 Index Fund Admiral (VFIAX)**

        Works for both the normal list-style ``fund_info`` and the
        dict-style ``fund_info`` returned by partial (HTTP 206) responses.
        Returns an empty string when the data carries no fund identity.
        """
        fi   = data.get("fund_info")
        name = ""
        ticker = ""

        if isinstance(fi, list):
            for row in fi:
                attr = row.get("Attribute", "")
                val  = (row.get("Value") or "").strip()
                if attr == "Share Class Name" and not name:
                    name = val
                elif attr in ("Ticker", "ticker") and not ticker:
                    ticker = val

        elif isinstance(fi, dict):
            name   = (fi.get("share_class_name") or fi.get("fund_name") or "").strip()
            ticker = (fi.get("ticker") or "").strip()

        if not name:
            name = (data.get("share_class_id") or data.get("morningstar_id") or "").strip()

        if not name:
            return ""

        if ticker:
            return "**{} ({})**".format(name, ticker)
        return "**{}**".format(name)

    # ── 1. Product Info ──────────────────────────────────────────────────
    @staticmethod
    def product_info(data: Dict) -> str:
        rows = data.get("fund_info", [])
        if not rows:
            return "Product information is not available."
        lines = ["**Product Info**\n"]
        for r in rows:
            lines.append(f"• **{r['Attribute']}:** {r['Value']}")
        lines.append(f"• **Share Class ID:** {data.get('share_class_id', data.get('morningstar_id', 'N/A'))}")
        # Show MCP metadata if present
        if data.get("published_at"):
            lines.append(f"• **Research Published:** {data['published_at'][:10]}")
        if data.get("reference_url"):
            lines.append(f"• **Reference URL:** {data['reference_url']}")
        if data.get("source") == "mcp":
            lines.append("• **Data Source:** Morningstar MCP")
        return "\n".join(lines)

    # ── Shared rating-breakdown building blocks ───────────────────────────
    # Used by both overall_rating() and the full_report() section builder so
    # the two entry points can never drift apart on the actual score logic.
    @staticmethod
    def _rating_breakdown_lines(data: Dict, hist: List[Dict]) -> List[str]:
        """Medalist Rating + Weighted Score + latest component scores."""
        rating_num = data.get("overall_rating")
        breakdown = data.get("rating_breakdown", {})
        weighted = breakdown.get("weighted_score")
        rating_value = data.get("overall_rating_raw")
        if rating_value is None:
            rating_value = rating_num

        lines: List[str] = []
        if rating_value is not None:
            lines.append(f"• **Medalist Rating:** {_display_value(rating_value)}")
        else:
            lines.append("• **Medalist Rating:** Not available")
        medal_line_idx = len(lines) - 1

        if weighted is not None:
            lines.append(f"• **Weighted Medalist Rating Score:** {weighted:.4f}")

        latest = _latest(hist)
        if latest:
            rating_type = latest.get("Medalist Rating Type")
            if rating_type:
                lines[medal_line_idx] = lines[medal_line_idx].rstrip() + f"  {_display_rating_type(rating_type)}"

            lines.append(f"• **People Score:** {_score_with_type(latest.get('People'), latest.get('People Type'))}")
            lines.append(f"• **Process Score:** {_score_with_type(latest.get('Process'), latest.get('Process Type'))}")
            lines.append(f"• **Parent Score:** {_score_with_type(latest.get('Parent'), latest.get('Parent Type'))}")
            price_score = latest.get("Price Score")
            if price_score is None:
                price_score = data.get("medalist_price_score")
            lines.append(f"• **Price Score:** {_display_value(price_score)}")
        return lines

    @staticmethod
    def _formula_and_derivation_lines(breakdown: Dict) -> List[str]:
        lines: List[str] = []
        formula = breakdown.get("formula_text", "")
        if formula:
            clean = formula.replace("$$", "\n").replace("\\times", "×").replace("\\Big(", "(").replace("\\Big)", ")")
            clean = clean.replace("\\text{", "").replace("}", "").replace("\\quad", "  ").replace("\\le", "≤").replace("\\ge", "≥")
            lines.append(f"\n**Formula:**\n{clean.strip()}")

        deriv = breakdown.get("derivation_text", "")
        if deriv:
            lines.append(f"\n{deriv}")
        return lines

    @staticmethod
    def _historical_table_rows(hist: List[Dict]) -> List[str]:
        """Render the historical ratings markdown table (header + one row per month)."""
        sorted_hist = sorted(hist, key=lambda r: _get_record_date(r), reverse=True)
        lines = [
            "| Date | Medalist Rating | Medalist Rating Type | People | People Type | Process | Process Type | Parent | Parent Type | Price |",
            "|------|-----------------|----------------------|--------|-------------|---------|--------------|--------|-------------|-------|",
        ]
        for r in sorted_hist:
            dt = _get_record_date(r)[:10]
            lines.append(
                f"| {dt} | {_display_value(r.get('Medalist Rating'))} | {_display_rating_type(r.get('Medalist Rating Type'))} "
                f"| {_display_pillar_value(r.get('People'))} | {_display_rating_type(r.get('People Type'))} "
                f"| {_display_pillar_value(r.get('Process'))} | {_display_rating_type(r.get('Process Type'))} "
                f"| {_display_pillar_value(r.get('Parent'))} | {_display_rating_type(r.get('Parent Type'))} "
                f"| {_display_value(r.get('Price Score'))} |"
            )
        return lines

    @staticmethod
    def _price_score_lines(data: Dict, s, e) -> List[str]:
        price_obj = data.get("price", {})
        price_data = _filter_by_date(price_obj.get("data", []), s, e)
        price_text = price_obj.get("text", "")
        medalist_price = data.get("medalist_price_score")

        lines: List[str] = []
        if medalist_price is not None:
            lines.append(f"• **Medalist Price Score:** {medalist_price}")
        else:
            lines.append("• **Medalist Price Score:** Not available")

        latest = _latest(price_data) if price_data else None
        if latest:
            lines.append(f"• **Annual Fee:** {latest.get('AnnualFee', 'N/A')}")
            lines.append(f"• **Category Median Annual Fee:** {latest.get('CategoryMedianAnnualFee', 'N/A')}")
            lines.append(f"• **Fee Type:** {latest.get('FeeType', 'N/A')}")
            raw = latest.get("PriceScoreRaw")
            if raw is not None:
                lines.append(f"• **Price Score Raw:** {raw:.4f}")
        elif not price_data:
            lines.append("\n> Price score data is not available for this fund.")

        if price_text:
            lines.append(f"\n**Price Score Methodology**\n{price_text.strip()}")
        return lines

    # ── 2. Overall Rating Breakdown ──────────────────────────────────────
    @staticmethod
    def overall_rating(data: Dict, start_date=None, end_date=None) -> str:
        s, e = _resolve_dates(start_date, end_date)
        hist = _filter_by_date(data.get("historical_ratings", []), s, e)

        lines = ["**Overall Rating Breakdown**\n"]
        lines.extend(Formatter._rating_breakdown_lines(data, hist))
        if not hist:
            lines.append("\n> Rating breakdown data is not available.")
        lines.extend(Formatter._formula_and_derivation_lines(data.get("rating_breakdown", {})))

        return Formatter._with_disclosure(data, "\n".join(lines))

    # ── 3. Historical Ratings ────────────────────────────────────────────
    @staticmethod
    def historical_ratings(data: Dict, start_date=None, end_date=None) -> str:
        s, e = _resolve_dates(start_date, end_date)
        hist = _filter_by_date(data.get("historical_ratings", []), s, e)
        label = _date_range_label(s, e)
        if not hist:
            msg = "No historical rating data available"
            body = "{}{}.".format(msg, " for the specified date range" if label else "")
            return Formatter._with_disclosure(data, body)

        lines = [f"**Historical Ratings** ({len(hist)} months){label}\n"]
        lines.extend(Formatter._historical_table_rows(hist))

        warning = data.get("historical_data_warning")
        if warning:
            lines.append(f"\n> ⚠ {warning}")

        return Formatter._with_disclosure(data, "\n".join(lines))

    # ── 4. Price Score ───────────────────────────────────────────────────
    @staticmethod
    def price_score(data: Dict, start_date=None, end_date=None) -> str:
        s, e = _resolve_dates(start_date, end_date)
        label = _date_range_label(s, e)

        lines = [f"**Price Score**{label}\n"]
        lines.extend(Formatter._price_score_lines(data, s, e))

        return Formatter._with_disclosure(data, "\n".join(lines))

    # ── Shared "Algorithmic Inputs" table renderer ────────────────────────
    # Used by people_pillar/process_pillar/parent_pillar, which differ only
    # in which extra per-row field(s) they append (weight+adjustment vs
    # rule-score). `extra_renderers` are called per-row and their output is
    # appended after "raw=..., ranked=...".
    @staticmethod
    def _render_algorithmic_inputs(algo: List[Dict], extra_renderers=None) -> List[str]:
        if not algo:
            return []
        latest_date = max(_get_record_date(r) for r in algo)
        latest_algo = [r for r in algo if _get_record_date(r) == latest_date]
        if not latest_algo:
            return []
        lines = [f"\n**Algorithmic Inputs ({latest_date}):**"]
        for r in latest_algo:
            feat = r.get("Feature", "")
            raw = r.get("RawValue", r.get("Raw Value", "N/A"))
            ranked = r.get("RankedValue", r.get("Ranked Value", "N/A"))
            extra = "".join(render(r) for render in (extra_renderers or []))
            lines.append(f"  • {feat}: raw={raw}, ranked={ranked}{extra}")
        return lines

    @staticmethod
    def _weight_and_adjustment(r: Dict) -> str:
        w = r.get("Weight", "")
        adj = r.get("AdjustmentAmount")
        adj_str = f"  adj={adj}" if adj and str(adj) != "nan" and adj == adj else ""
        w_str = f"  weight={w}" if w else ""
        return w_str + adj_str

    @staticmethod
    def _rule_based_score(r: Dict) -> str:
        rule = r.get("RuleBasedScore", r.get("Score", ""))
        return f"  rule-score={rule}" if rule != "" else ""

    # ── 5. Pillar Analysis (People) ──────────────────────────────────────
    @staticmethod
    def _people_pillar_body(data: Dict, start_date=None, end_date=None) -> str:
        """People pillar content without disclosure — shared by people_pillar() and
        full_report()'s _section_pillar_analysis() so disclosure is never double-applied."""
        s, e = _resolve_dates(start_date, end_date)
        pp = data.get("people_pillar", {})
        records = _filter_by_date(pp.get("data", []), s, e)
        algo    = _filter_by_date(pp.get("algorithmic_data", []), s, e)
        text = pp.get("text", "")
        label = _date_range_label(s, e)

        lines = [f"**People**{label}\n"]
        latest = _latest(records) if records else None
        if latest:
            lines.append(f"• **Score:** {_display_pillar_value(latest.get('PeopleScore'))}")
            lines.append(f"• **Assignment:** {_display_rating_type(latest.get('PeopleScoreType'))}")
        elif not pp:
            lines.append("> People pillar data is not available for this fund.")
            return "\n".join(lines)

        if text:
            lines.append(f"\n**Algorithmic People Score Derivation**\n{text.strip()}")
            lines.append(f"\n{PEOPLE_METHODOLOGY_NOTE}")

        lines.extend(Formatter._render_algorithmic_inputs(algo, [Formatter._weight_and_adjustment]))

        lines.append(f"\n{PILLAR_SCORE_SCALE_LINE}")
        lines.append(f"\n{PILLAR_SCORE_CHARACTERISTICS}")

        return "\n".join(lines)

    @staticmethod
    def people_pillar(data: Dict, start_date=None, end_date=None) -> str:
        return Formatter._with_disclosure(data, Formatter._people_pillar_body(data, start_date, end_date))

    # ── 6. Pillar Analysis (Process) ─────────────────────────────────────
    @staticmethod
    def _process_pillar_body(data: Dict, start_date=None, end_date=None) -> str:
        """Process pillar content without disclosure — see _people_pillar_body."""
        s, e = _resolve_dates(start_date, end_date)
        pp = data.get("process_pillar", {})
        records = _filter_by_date(pp.get("data", []), s, e)
        algo    = _filter_by_date(pp.get("algorithmic_data", []), s, e)
        text = pp.get("text", "")
        label = _date_range_label(s, e)

        lines = [f"**Process**{label}\n"]
        latest = _latest(records) if records else None
        if latest:
            lines.append(f"• **Score:** {_display_pillar_value(latest.get('ProcessScore'))}")
            lines.append(f"• **Assignment:** {_display_rating_type(latest.get('ProcessScoreType'))}")
        elif not pp:
            lines.append("> Process pillar data is not available for this fund.")
            return "\n".join(lines)

        if text:
            lines.append(f"\n**Algorithmic Process Score Derivation**\n{text.strip()}")
            lines.append(f"\n{PROCESS_METHODOLOGY_NOTE}")

        lines.extend(Formatter._render_algorithmic_inputs(algo, [Formatter._weight_and_adjustment]))
        lines.append(f"\n{PILLAR_SCORE_SCALE_LINE}")

        return "\n".join(lines)

    @staticmethod
    def process_pillar(data: Dict, start_date=None, end_date=None) -> str:
        return Formatter._with_disclosure(data, Formatter._process_pillar_body(data, start_date, end_date))

    # ── 7. Pillar Analysis (Parent) ──────────────────────────────────────
    @staticmethod
    def _parent_pillar_body(data: Dict, start_date=None, end_date=None) -> str:
        """Parent pillar content without disclosure — see _people_pillar_body."""
        s, e = _resolve_dates(start_date, end_date)
        pp = data.get("parent_pillar", {})
        records = _filter_by_date(pp.get("data", []), s, e)
        algo    = _filter_by_date(pp.get("algorithmic_data", []), s, e)
        text = pp.get("text", "")
        label = _date_range_label(s, e)

        lines = [f"**Parent**{label}\n"]
        latest = _latest(records) if records else None
        if latest:
            for key in latest:
                if key not in ("EndDate", "Date"):
                    value = latest[key]
                    if key == "ParentScore":
                        value = _display_pillar_value(value)
                    elif key == "ParentScoreType":
                        value = _display_rating_type(value)
                    lines.append(f"• **{key}:** {value}")
        elif not pp:
            lines.append("> Parent pillar data is not available for this fund.")
            return "\n".join(lines)

        if text:
            lines.append(f"\n**Algorithmic Parent Score Derivation**\n{text.strip()}")

        lines.extend(Formatter._render_algorithmic_inputs(algo, [Formatter._rule_based_score]))
        lines.append(f"\n{PILLAR_SCORE_SCALE_LINE}")

        return "\n".join(lines)

    @staticmethod
    def parent_pillar(data: Dict, start_date=None, end_date=None) -> str:
        return Formatter._with_disclosure(data, Formatter._parent_pillar_body(data, start_date, end_date))

    # ── Routing flags (for agent formula selection) ──────────────────────
    @staticmethod
    def routing_flags(data: Dict) -> str:
        """Return a concise block of fund routing flags for agent prompt context.

        Values are taken exactly as stored — never inferred or defaulted.
        None (not returned by the API) is rendered as 'Not available'.
        """
        def _fmt(v) -> str:
            if v is True:
                return "true"
            if v is False:
                return "false"
            return "Not available"

        domicile = data.get("domicile_country") or "Not available"
        is_index = _fmt(data.get("is_index_fund"))
        is_super  = _fmt(data.get("is_australian_superannuation_fund"))

        lines = [
            "Internal routing flags (use these values directly; do not infer missing values):",
            f"- domicile_country: {domicile}",
            f"- is_index_fund (OF00C): {is_index}",
            f"- is_australian_superannuation_fund (OS280): {is_super}",
        ]
        if is_super == "Not available":
            lines.append(
                "- OS280 was not returned by the data tool. "
                'Respond with exactly: "Is this an Australian superannuation fund? '
                'I need this information to determine how the rating is calculated." '
                "Output those two sentences only — no formula names, no routing explanation, no additional text."
            )
        return "\n".join(lines)

    # ── Disclosure section ───────────────────────────────────────────────
    @staticmethod
    def _format_disclosure(data: Dict) -> str:
        """
        Return formatted disclosure text if applicable, empty string otherwise.

        Checks data["disclosure_type"] and returns the corresponding disclosure
        text wrapped in a section header if the type is recognized.
        """
        disclosure_type = data.get("disclosure_type")
        if not disclosure_type:
            return ""

        disclosure_text = DISCLOSURE_TEXTS.get(disclosure_type)
        if not disclosure_text:
            return ""

        lines = [
            "─" * 80,
            "Disclosure",
            "─" * 80,
            disclosure_text,
            "─" * 80,
        ]
        return "\n".join(lines)

    # ── Full report (all sections, structured per docx layout) ──────────
    @staticmethod
    def full_report(data: Dict, start_date=None, end_date=None) -> str:
        """
        Generate full report with all available sections.
        Gracefully handles missing data by showing available sections.

        Optional start_date / end_date filter all time-series sections.
        Accepts any format understood by parse_date() — e.g. "2020-01-01",
        "June 2020", "1/1/2020", "now".

        Guarantees that every narrative text field present in the API response
        is included in the output.
        """
        sections = []

        s1 = Formatter._section_product_info(data)
        sections.append(s1)

        s2 = Formatter._section_overall_breakdown(data, start_date=start_date, end_date=end_date)
        sections.append(s2)

        s3 = Formatter._section_pillar_analysis(data, start_date=start_date, end_date=end_date)
        sections.append(s3)

        Formatter._ensure_narrative_texts(data, sections)

        # Add notice at the beginning if present
        notice = Formatter._get_data_notice(data)
        if notice:
            sections.insert(0, notice)

        # Add disclosure at the VERY BEGINNING (before notice)
        disclosure = Formatter._format_disclosure(data)
        if disclosure:
            sections.insert(0, disclosure)

        return "\n\n" + "\n\n---\n\n".join(sections)

    @staticmethod
    def _ensure_narrative_texts(data: Dict, sections: List[str]) -> None:
        """
        Append a supplemental section for any narrative text field that is
        present in the API response but was not rendered by the main sections.
        This acts as a safety net so no text is ever silently dropped.
        """
        # Build a combined string of everything already in sections to check
        # coverage (case-insensitive prefix match on first 80 chars).
        combined = "\n".join(sections)

        extras: List[str] = []

        def _add_if_missing(label: str, text: str) -> None:
            if text and text.strip()[:80] not in combined:
                extras.append(f"**{label}**\n{text.strip()}")

        bd = data.get("rating_breakdown", {})
        _add_if_missing("Rating Formula", bd.get("formula_text", ""))
        _add_if_missing("Rating Score Derivation", bd.get("derivation_text", ""))
        _add_if_missing("Price Score Methodology", (data.get("price") or {}).get("text", ""))
        _add_if_missing("People Pillar Derivation", (data.get("people_pillar") or {}).get("text", ""))
        _add_if_missing("Process Pillar Derivation", (data.get("process_pillar") or {}).get("text", ""))
        _add_if_missing("Parent Pillar Derivation", (data.get("parent_pillar") or {}).get("text", ""))

        if extras:
            sections.append("**Narrative Details**\n\n" + "\n\n".join(extras))

    @staticmethod
    def _get_data_notice(data: Dict) -> str:
        """Generate a notice if data is incomplete."""
        notice_lines: List[str] = []

        if data.get("status") == "partial_data":
            missing = data.get("missing_field", "some fields")
            notice_lines.append(
                f"> Some data is unavailable (missing: {missing}). "
                "Showing all available information below."
            )
        else:
            # Check if key sections are missing
            missing_sections = []
            if not data.get("overall_rating") and not data.get("historical_ratings"):
                missing_sections.append("rating data")
            if not data.get("price") and not data.get("medalist_price_score"):
                missing_sections.append("price score")

            if missing_sections:
                notice_lines.append(
                    f"> {', '.join(missing_sections).capitalize()} not available. "
                    "Showing available information below."
                )

        warning = data.get("historical_data_warning")
        if warning:
            notice_lines.append(f"> ⚠ {warning}")

        if not notice_lines:
            return ""
        return "**Data Availability Notice**\n\n" + "\n".join(notice_lines)

    # ── Section builders used by full_report ─────────────────────────

    @staticmethod
    def _section_product_info(data: Dict) -> str:
        """Section 1: Product Info."""
        rows = data.get("fund_info", [])
        lines = ["**1) Product Info**\n"]
        if not rows:
            lines.append("Product information is not available.")
        else:
            for r in rows:
                lines.append(f"• **{r['Attribute']}:** {r['Value']}")
            lines.append(f"• **Share Class ID:** {data.get('share_class_id', 'N/A')}")
        return "\n".join(lines)

    @staticmethod
    def _section_overall_breakdown(data: Dict, start_date=None, end_date=None) -> str:
        """Section 2: Overall Rating Breakdown (includes Historical Ratings and Price Score).

        Built from the same shared helpers as overall_rating() / historical_ratings() /
        price_score() so the two report entry points can't drift apart on the underlying
        score logic — only header formatting differs here (numbered section titles).
        """
        s, e = _resolve_dates(start_date, end_date)
        label = _date_range_label(s, e)
        lines = [f"**2) Overall Rating Breakdown**{label}\n"]

        hist = _filter_by_date(data.get("historical_ratings", []), s, e)
        lines.extend(Formatter._rating_breakdown_lines(data, hist))
        lines.extend(Formatter._formula_and_derivation_lines(data.get("rating_breakdown", {})))

        # ── Historical Ratings sub-section ────────────────────────────
        lines.append(f"\n**Historical Ratings**{label}\n")
        if not hist:
            lines.append("No historical rating data available{}.".format(
                " for the specified date range" if label else ""))
        else:
            lines.append(f"({len(hist)} months)\n")
            lines.extend(Formatter._historical_table_rows(hist))

        # ── Price Score sub-section ───────────────────────────────────
        lines.append("\n**Price Score**\n")
        lines.extend(Formatter._price_score_lines(data, s, e))

        return "\n".join(lines)

    @staticmethod
    def _section_pillar_analysis(data: Dict, start_date=None, end_date=None) -> str:
        """Section 3: Pillar Analysis (People / Process / Parent)."""
        lines = [
            "**3) Pillar Analysis**\n",
            PILLAR_ASSIGNMENT_INTRO,
        ]

        lines.append("\n" + Formatter._people_pillar_body(data, start_date=start_date, end_date=end_date))
        lines.append("\n" + Formatter._process_pillar_body(data, start_date=start_date, end_date=end_date))
        lines.append("\n" + Formatter._parent_pillar_body(data, start_date=start_date, end_date=end_date))

        return "\n".join(lines)

    # ── Partial report (HTTP 206 — some data missing) ────────────────────
    @staticmethod
    def partial_report(data: Dict) -> str:
        """
        Render whatever is available in a partial (HTTP 206) API response.
        Shows a clear notice about what is missing, then displays all
        available fund information and pillar scores.
        """
        missing   = data.get("missing_field", "unknown field")
        message   = data.get("message") or data.get("error", "Partial data available")
        suggestion = data.get("suggestion", "")
        fi        = data.get("fund_info", {})

        lines: List[str] = []

        # ── Fund header (name and ticker) ─────────────────────────────
        header = Formatter.fund_header(data)
        if header:
            lines.append(header)
            lines.append("")

        # ── Data-availability notice ──────────────────────────────────
        lines.append("**Partial Data Notice**\n")
        lines.append("> **{}**".format(message))
        if missing and missing != "unknown field":
            lines.append("> Missing field: `{}`".format(missing))
        if suggestion:
            lines.append("> {}".format(suggestion))
        lines.append("")

        if not fi:
            lines.append("No fund information is available for this share class.")
            return "\n".join(lines)

        # ── Product information ───────────────────────────────────────
        lines.append("**Product Information**\n")
        fields = [
            ("Share Class",       fi.get("share_class_name")),
            ("Share Class ID",    fi.get("share_class_id")),
            ("Ticker",            fi.get("ticker")),
            ("Fund Name",         fi.get("fund_name")),
            ("Strategy",          fi.get("strategy_name")),
            ("Branding",          fi.get("branding_name")),
            ("Domicile",          fi.get("domicile")),
            ("Category",          fi.get("category_name")),
            ("Broad Category",    fi.get("broad_category_group")),
            ("Investment Type",   fi.get("investment_type")),
            ("Index Fund",        fi.get("index_fund")),
            ("Strategic Beta",    fi.get("strategic_beta")),
            ("Primary Benchmark", fi.get("primary_benchmark")),
            ("Active",            fi.get("active")),
        ]
        for label, val in fields:
            if val not in (None, "", "N/A"):
                lines.append("• **{}:** {}".format(label, val))

        # ── Available pillar scores ───────────────────────────────────
        pillar_rows = [
            ("People",  "people_score",  "people_score_type"),
            ("Process", "process_score", "process_score_type"),
            ("Parent",  "parent_score",  "parent_score_type"),
        ]
        available_pillars = [(p, fi.get(sk), fi.get(tk))
                             for p, sk, tk in pillar_rows
                             if fi.get(sk) is not None]

        if available_pillars:
            lines.append("\n**Available Pillar Scores**\n")
            for pillar, score, ptype in available_pillars:
                type_str = "  ({})".format(ptype) if ptype else ""
                lines.append("• **{}:** {}{}".format(pillar, _display_value(score), type_str))

            # Note which pillar is unavailable
            missing_pillars = [p for p, sk, _ in pillar_rows if fi.get(sk) is None]
            missing_pillars.append("Price")           # price score caused the 206
            if missing_pillars:
                lines.append("\n• **{}:** Not available — `{}` is missing.".format(
                    " / ".join(missing_pillars), missing))

        # ── Overall rating (if present) ───────────────────────────────
        overall = fi.get("overall_rating")
        if overall is not None:
            lines.append("\n**Overall Rating Score:** {}  (incomplete — price data missing)".format(overall))

        return "\n".join(lines)
