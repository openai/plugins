"""Executable safeguards for one source-grounded, consolidated seller workspace."""

from __future__ import annotations

import re
import unittest
from datetime import date, timedelta
from pathlib import Path

from sales_test_support import SalesTestCase

SKILLS = Path(__file__).resolve().parents[2]
TEMPLATE = (
    SKILLS / "demo-exec-and-seller-dash" / "assets" / "account-priority-workspace.template.html"
)
SELLER_SKILL = SKILLS / "seller-account-dashboard" / "SKILL.md"
SIGNALS_SKILL = SKILLS / "analyze-account-signals" / "SKILL.md"

NODE_BOOTSTRAP = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const text = (value, fallback = '') => {
  const supplied = value == null ? '' : String(value).trim();
  return supplied || fallback;
};

function bodyFor(name) {
  const matched = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(matched, 'Expected executable consolidated seller helper ' + name);
  return matched[1];
}

function helper(name, dependencies) {
  const signature = template.match(new RegExp('function ' + name + '\\(([^)]*)\\)'));
  assert.ok(signature, 'Expected callable helper signature for ' + name);
  const parameters = signature[1].split(',').map(value => value.trim()).filter(Boolean);
  return new Function(...Object.keys(dependencies), ...parameters, bodyFor(name)).bind(
    null, ...Object.values(dependencies)
  );
}

class Element {
  constructor(tag, className = '', content = '') {
    this.tagName = tag.toUpperCase();
    this.className = className;
    this.copy = content == null ? '' : String(content);
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this.style = {};
    this.handlers = {};
    this.hidden = false;
  }
  append(...nodes) { nodes.forEach(node => this.appendChild(node)); }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren(...nodes) { this.children = [...nodes]; this.copy = ''; }
  setAttribute(key, value) { this.attributes[key] = String(value); }
  addEventListener(name, handler) { this.handlers[name] = handler; }
  get textContent() {
    return [this.copy, ...this.children.map(child => child.textContent)].join(' ');
  }
  set textContent(value) { this.copy = String(value); }
}

function descendants(node, predicate) {
  return node.children.flatMap(child => [
    ...(predicate(child) ? [child] : []), ...descendants(child, predicate)
  ]);
}
"""

FOCUS_BOOTSTRAP = r"""
function inspectFocus(goal, rows, payloadOverrides = {}) {
  const payload = {...(goal == null ? {} : {dashboardGoal: goal}), ...payloadOverrides};
  const card = new Element('section');
  const heading = new Element('h2');
  const list = new Element('div');
  const opened = [];
  const document = {
    getElementById(id) {
      return {
        'seller-focus-card': card,
        'seller-focus-heading': heading,
        'seller-focus-list': list
      }[id];
    }
  };
  const create = (tag, className, content) => new Element(tag, className, content);
  const openAccountDrawer = account => opened.push(account);
  const accountButton = helper('accountButton', {create, openAccountDrawer});
  const selectedDashboardGoal = helper('selectedDashboardGoal', {payload, text});
  const renderDashboardFocus = helper('renderDashboardFocus', {
    selectedDashboardGoal, document, sortedAccounts: () => [...rows],
    priorityScore: row => row.priorityScore ?? null,
    rationalesFor: row => row.rationale || [],
    verifiedChangeEvents: row => row.changes || [],
    detailFor: row => row.detail || {},
    text,
    verifiedOpportunity: row => row.opportunity || {present: false, amount: null},
    verifiedMeetingEvents: row => row.meetings || [],
    openItemsFor: row => row.openItems ?? null,
    meetingWhen: event => event.when || '',
    accountButton
  });
  renderDashboardFocus();
  return {card, heading, list, opened, mode: selectedDashboardGoal()};
}
"""


class SellerDashboardConsolidationTests(SalesTestCase):
    def assert_node(self, assertions: str) -> None:
        self.assert_node_script(NODE_BOOTSTRAP + assertions, str(TEMPLATE))

    def test_owned_book_ranking_routes_to_seller_not_bounded_signal_monitor(self) -> None:
        signals = SIGNALS_SKILL.read_text(encoding="utf-8")
        signal_description = signals.split("---", maxsplit=2)[1].lower()
        seller_description = (
            SELLER_SKILL.read_text(encoding="utf-8").split("---", maxsplit=2)[1].lower()
        )

        self.assertIn("one named account", signal_description)
        self.assertIn("explicitly", signal_description)
        self.assertIn("bounded", signal_description)
        self.assertIn("owner portfolio or watchlist", signal_description)
        self.assertIn("owned-account prioritization", signal_description)
        self.assertIn("seller-account-dashboard", signal_description)
        self.assertNotIn("or rank accounts needing attention", signal_description)
        self.assertIn("prioritiz", seller_description)
        self.assertRegex(seller_description, r"rank(?:ed|ings?)")
        self.assertIn("account dashboard", seller_description)

        self.assertIn("Monitor Summary for accounts I own in CRM", signals)
        self.assertIn("Monitor Summary for a watchlist, owner, or territory", signals)

    def test_historical_account_signals_bound_provider_queries_before_retrieval(self) -> None:
        signals = SIGNALS_SKILL.read_text(encoding="utf-8")
        self.assertIn("actual requested dates, as-of cutoff, and relevant timezone", signals)
        self.assertIn("never reuse another request's dates", signals)
        self.assertIn("before every time-varying provider call", signals)
        self.assertIn("actual date field appropriate to the requested signal", signals)
        self.assertIn("<history-date-field> >= <window-start>", signals)
        self.assertIn("<history-date-field> < <exclusive-window-end>", signals)
        self.assertIn("after:<day-before-window-start> before:<exclusive-window-end>", signals)
        self.assertIn("an exact `on:<in-window-day>`", signals)
        self.assertIn("**Example only:**", signals)
        self.assertIn("Never fetch an unbounded denormalized timeline", signals)
        self.assertIn("`Next_Step_History__c`", signals)
        self.assertIn("never issue an unbounded Slack/email/file search", signals)
        self.assertIn("never retrieve out-of-window records for later filtering", signals)
        self.assertIn("skip that retrieval", signals)
        self.assertIn("explicitly disclose the unavailable in-window evidence", signals)

        def has_exact_server_window(
            arguments: str, provider: str, start: date, inclusive_end: date
        ) -> bool:
            exclusive_end = inclusive_end + timedelta(days=1)
            if provider == "salesforce":
                return bool(
                    re.search(rf"\bCreatedDate\s*>=\s*{start.isoformat()}T00:00:00Z", arguments)
                    and re.search(
                        rf"\bCreatedDate\s*<\s*{exclusive_end.isoformat()}T00:00:00Z",
                        arguments,
                    )
                )
            day_match = re.search(r"\bon:(\d{4}-\d{2}-\d{2})\b", arguments)
            if day_match:
                return start <= date.fromisoformat(day_match.group(1)) <= inclusive_end
            return bool(
                re.search(rf"\bafter:{(start - timedelta(days=1)).isoformat()}\b", arguments)
                and re.search(rf"\bbefore:{exclusive_end.isoformat()}\b", arguments)
            )

        unbounded_history = "SELECT Id, Next_Step_History__c FROM Opportunity WHERE Id = '006x'"
        unbounded_slack = '"NVIDIA" "renewal"'
        for start, inclusive_end in (
            (date(2026, 6, 16), date(2026, 7, 16)),
            (date(2025, 11, 3), date(2025, 11, 8)),
        ):
            with self.subTest(start=start, inclusive_end=inclusive_end):
                exclusive_end = inclusive_end + timedelta(days=1)
                bounded_soql = (
                    f"CreatedDate >= {start.isoformat()}T00:00:00Z "
                    f"AND CreatedDate < {exclusive_end.isoformat()}T00:00:00Z"
                )
                bounded_slack = (
                    f"after:{(start - timedelta(days=1)).isoformat()} "
                    f"before:{exclusive_end.isoformat()}"
                )
                self.assertTrue(
                    has_exact_server_window(bounded_soql, "salesforce", start, inclusive_end)
                )
                self.assertTrue(
                    has_exact_server_window(bounded_slack, "slack", start, inclusive_end)
                )
                self.assertTrue(
                    has_exact_server_window(
                        f"on:{start.isoformat()}", "slack", start, inclusive_end
                    )
                )
                self.assertTrue(
                    has_exact_server_window(
                        f"on:{inclusive_end.isoformat()}", "slack", start, inclusive_end
                    )
                )
                self.assertFalse(
                    has_exact_server_window(
                        f"on:{exclusive_end.isoformat()}", "slack", start, inclusive_end
                    )
                )
                self.assertFalse(
                    has_exact_server_window(unbounded_history, "salesforce", start, inclusive_end)
                )
                self.assertFalse(
                    has_exact_server_window(unbounded_slack, "slack", start, inclusive_end)
                )
                self.assertFalse(
                    has_exact_server_window(
                        f"CreatedDate >= {start.isoformat()}T00:00:00Z",
                        "salesforce",
                        start,
                        inclusive_end,
                    )
                )
                self.assertFalse(
                    has_exact_server_window(
                        f"after:{(start - timedelta(days=1)).isoformat()}",
                        "slack",
                        start,
                        inclusive_end,
                    )
                )

    def test_one_dashboard_has_three_view_tabs_and_accessible_account_filters(self) -> None:
        source = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r'role="tab"', source)), 3)
        self.assertIn('id="tab-home"', source)
        self.assertIn('id="tab-accounts"', source)
        self.assertIn('id="tab-pipeline"', source)
        self.assertIn('id="account-search"', source)
        self.assertIn('id="account-search-clear"', source)

        for key in ("all", "workNow", "watch", "paused"):
            button = re.search(rf'<button\b(?=[^>]*\bid="account-filter-{key}")[^>]*>', source)
            self.assertIsNotNone(button, f"Missing accessible {key} account filter")
            assert button is not None
            self.assertIn("aria-pressed=", button.group(0))
            self.assertNotIn('role="tab"', button.group(0))

        clear = re.search(r"\.account-search-clear\s*\{([^}]*)\}", source)
        self.assertIsNotNone(clear, "Search clear needs a reusable touch-target rule")
        assert clear is not None
        self.assertRegex(clear.group(1), r"(?:min-)?width\s*:\s*44px")
        self.assertRegex(clear.group(1), r"(?:min-)?height\s*:\s*44px")
        self.assertNotIn('id="filter-stack"', source)
        self.assertNotIn('id="sidebar"', source)
        self.assertNotIn('role="tab" id="account-filter-', source)

    def test_search_and_group_filters_compose_with_source_grounded_priority_sort(self) -> None:
        self.assert_node(
            r"""
const harbor = {
  account: 'Harbor Health', owner: 'Priya Desai', stage: 'Customer review',
  nextAction: 'Share renewal proposal', priorityScore: 84, rank: 3
};
const atlas = {
  account: 'Atlas Retail', owner: 'Morgan Lee', stage: 'Negotiation',
  nextAction: 'Confirm security review', priorityScore: 97, rank: 1
};
const cedar = {
  account: 'Cedar Financial', owner: 'Priya Desai', stage: 'Discovery',
  nextAction: 'Send product notes', priorityScore: 31, rank: 2
};
const dormant = {
  account: 'Orchard Logistics', owner: 'Jamie Chen', stage: 'Renewal paused',
  whyItMatters: 'Customer requested a pause', priorityScore: null, rank: 4
};
const groups = {workNow: [harbor, atlas], watch: [cedar], paused: [dormant]};
const allRows = [...groups.workNow, ...groups.watch, ...groups.paused];
const state = {accountQuery: '', accountFilter: 'all', sortDescending: true};
const detailFor = row => row.detail || {};
const priorityScore = row => row.priorityScore;
const sortedAccounts = helper('sortedAccounts', {allRows, priorityScore, state});
const filteredAccounts = helper('filteredAccounts', {
  sortedAccounts, groups, state, text, detailFor,
  rationalesFor: row => [row.whyItMatters].filter(Boolean)
});
const names = () => filteredAccounts().map(row => row.account);

assert.deepEqual(names(), ['Atlas Retail', 'Harbor Health', 'Cedar Financial', 'Orchard Logistics']);
state.accountFilter = 'workNow';
assert.deepEqual(names(), ['Atlas Retail', 'Harbor Health'],
  'Work-now filtering preserves grounded descending priority score order');
state.sortDescending = false;
assert.deepEqual(names(), ['Harbor Health', 'Atlas Retail'],
  'Changing priority sort composes with the selected group instead of resetting it');

state.accountQuery = 'priya';
assert.deepEqual(names(), ['Harbor Health'], 'Search can find the sourced account owner');
state.accountFilter = 'all';
assert.deepEqual(names(), ['Cedar Financial', 'Harbor Health'],
  'Changing group retains the active search and selected ascending order');
state.accountQuery = 'security review';
assert.deepEqual(names(), ['Atlas Retail'], 'Search includes a verified next action');
state.accountQuery = 'customer review';
assert.deepEqual(names(), ['Harbor Health'], 'Search includes a sourced opportunity stage');
state.accountQuery = '  orchard  ';
state.accountFilter = 'paused';
assert.deepEqual(names(), ['Orchard Logistics']);
state.accountFilter = 'watch';
assert.deepEqual(names(), [], 'Filters never widen a user-selected scope to manufacture results');
state.accountQuery = '';
assert.deepEqual(names(), ['Cedar Financial']);
"""
        )

    def test_priority_sort_retains_canonical_accessible_header_after_refinement(self) -> None:
        source = TEMPLATE.read_text(encoding="utf-8")
        instructions = SELLER_SKILL.read_text(encoding="utf-8")
        canonical = re.search(
            r'<th\b(?=[^>]*\bid="priority-column")(?=[^>]*\baria-sort="descending")[^>]*>'
            r'\s*<button\b(?=[^>]*\bid="priority-sort")[^>]*>',
            source,
        )

        self.assertIsNotNone(canonical, "The sort button must live in its actual aria-sort header")
        self.assertIn('document.getElementById("priority-column").setAttribute("aria-sort"', source)
        self.assertIn("never `apply_patch`, replace, rewrite, or move", instructions)
        self.assertIn(
            "`priority-sort` button MUST remain inside the original `priority-column`", instructions
        )
        self.assertIn("verify a real click toggles its direction", instructions)
        self.assertIn("Never create `account-sort-column`", instructions)
        self.assertIn("or replace a true priority score with account value", instructions.lower())

    def test_verified_account_name_sort_reverses_and_resets_without_priority_scores(self) -> None:
        source = TEMPLATE.read_text(encoding="utf-8")
        instructions = SELLER_SKILL.read_text(encoding="utf-8")
        self.assertRegex(
            source,
            r'<th id="account-name-column"[^>]*aria-sort="none"[^>]*>\s*'
            r'<button[^>]*id="account-name-sort"',
        )
        self.assertIn("alphabetical sorting of verified account names", instructions)
        self.assertIn("never invent them", instructions)
        self.assertIn("resets to the original source order", instructions)
        self.assert_node(
            r"""
const allRows = [
  {account: 'Harbor Health', accountValue: 250000},
  {account: 'Cedar Energy'},
];
const state = {
  sortMode: 'source', sortDescending: true, accountSortDirection: 'none'
};
const priorityScore = row => row.priorityScore ?? null;
const sortedAccounts = helper('sortedAccounts', {allRows, state, priorityScore, text});
const originalNames = allRows.map(row => row.account);
assert.deepEqual(sortedAccounts().map(row => row.account), originalNames);
const nameHeader = new Element('th');
const priorityHeader = new Element('th');
const nameIndicator = new Element('span', 'sort-indicator', '↕');
const priorityIndicator = new Element('span', 'sort-indicator', '↓');
const nameButton = new Element('button');
nameButton.querySelector = () => nameIndicator;
nameButton.disabled = false;
const priorityButton = new Element('button');
priorityButton.querySelector = () => priorityIndicator;
const nodes = {
  'account-name-column': nameHeader,
  'account-name-sort': nameButton,
  'priority-column': priorityHeader,
  'priority-sort': priorityButton,
};
const snapshots = [];
const renderAccounts = () => snapshots.push(sortedAccounts().map(row => row.account));
const document = {getElementById: id => nodes[id]};
const setupAccountSorting = helper('setupAccountSorting', {
  document, state, allRows, priorityScore, renderAccounts
});
setupAccountSorting();
nameButton.handlers.click();
assert.equal(nameHeader.attributes['aria-sort'], 'ascending');
assert.deepEqual(snapshots.at(-1), ['Cedar Energy', 'Harbor Health']);
nameButton.handlers.click();
assert.equal(nameHeader.attributes['aria-sort'], 'descending');
assert.deepEqual(snapshots.at(-1), ['Harbor Health', 'Cedar Energy']);
nameButton.handlers.click();
assert.equal(nameHeader.attributes['aria-sort'], 'none');
assert.deepEqual(snapshots.at(-1), originalNames);
assert.equal(state.sortMode, 'source');
assert.ok(allRows.every(row => !Object.hasOwn(row, 'priorityScore')));
nameButton.disabled = true;
nameButton.handlers.click();
assert.equal(snapshots.length, 3, 'No unsupported sort runs for fewer than two names');
const scoredRows = [
  {account: 'Alpha Health', priorityScore: 20},
  {account: 'Zulu Energy', priorityScore: 90},
];
const scoredState = {sortMode: 'priority', sortDescending: true};
const scoredAccounts = helper('sortedAccounts', {
  allRows: scoredRows, state: scoredState, priorityScore, text
});
assert.deepEqual(scoredAccounts().map(row => row.account), ['Zulu Energy', 'Alpha Health']);
scoredState.sortDescending = false;
assert.deepEqual(scoredAccounts().map(row => row.account), ['Alpha Health', 'Zulu Energy']);
const distinctNames = rows => new Set(
  rows.map(row => text(row.account).toLocaleLowerCase()).filter(Boolean)
).size;
assert.equal(distinctNames([]), 0);
assert.equal(distinctNames([{account: 'Harbor Health'}]), 1);
assert.equal(distinctNames([{account: 'Harbor Health'}, {account: 'harbor health'}]), 1);
assert.equal(distinctNames(allRows), 2);
"""
        )

    def test_search_clear_escape_and_filter_counts_use_the_verified_account_universe(self) -> None:
        self.assert_node(
            r"""
const input = {value: '', handlers: {}, focus() { this.focused = true; }};
const clear = {hidden: true, handlers: {}};
const keys = ['all', 'workNow', 'watch', 'paused'];
const buttons = Object.fromEntries(keys.map(key => {
  const counter = {textContent: ''};
  return [key, {
    attributes: {'aria-pressed': String(key === 'all')}, handlers: {},
    get textContent() { return key + ' ' + counter.textContent; },
    querySelector() { return counter; },
    setAttribute(name, value) { this.attributes[name] = String(value); }
  }];
}));
for (const node of [input, clear, ...Object.values(buttons)]) {
  node.addEventListener = (name, handler) => { node.handlers[name] = handler; };
}
const groups = {workNow: [{account: 'A'}, {account: 'B'}],
  watch: [{account: 'C'}], paused: [{account: 'D'}]};
const allRows = [...groups.workNow, ...groups.watch, ...groups.paused];
const state = {accountQuery: '', accountFilter: 'all'};
const document = {
  getElementById(id) {
    if (id === 'account-search') return input;
    if (id === 'account-search-clear') return clear;
    return buttons[id.replace('account-filter-', '')];
  },
  querySelectorAll(selector) {
    return selector.includes('account-filter') ? Object.values(buttons) : [];
  }
};
let renderCount = 0;
const renderAccounts = () => { renderCount += 1; };
const setupAccountFilters = helper('setupAccountFilters', {
  document, groups, groupKeys: ['workNow', 'watch', 'paused'], allRows, state,
  text, renderAccounts
});
setupAccountFilters();

for (const [key, count] of Object.entries({all: 4, workNow: 2, watch: 1, paused: 1})) {
  assert.match(buttons[key].textContent, new RegExp(String(count)),
    'Every filter count reflects only its complete verified account group: ' + key);
}
assert.equal(buttons.all.attributes['aria-pressed'], 'true');

input.value = 'Harbor';
input.handlers.input({target: input});
assert.equal(state.accountQuery, 'Harbor');
assert.equal(clear.hidden, false);

buttons.watch.handlers.click();
assert.equal(state.accountFilter, 'watch');
assert.equal(buttons.watch.attributes['aria-pressed'], 'true');
assert.equal(buttons.all.attributes['aria-pressed'], 'false');
assert.equal(state.accountQuery, 'Harbor', 'Choosing a group retains the active query');

let prevented = false;
input.handlers.keydown({key: 'Escape', preventDefault() { prevented = true; }});
assert.equal(prevented, true);
assert.equal(state.accountQuery, '');
assert.equal(input.value, '');
assert.equal(clear.hidden, true);
assert.equal(state.accountFilter, 'watch', 'Escape clears only search, never scope');

input.value = 'Cedar';
input.handlers.input({target: input});
clear.handlers.click();
assert.equal(state.accountQuery, '');
assert.equal(input.value, '');
assert.equal(input.focused, true, 'Search clear returns keyboard focus to the input');
assert.ok(renderCount >= 4, 'Search, filtering, Escape, and clear all refresh live rows');
"""
        )

    def test_only_verified_customer_people_checklist_changes_and_https_links_are_shown(
        self,
    ) -> None:
        self.assert_node(
            r"""
const detailFor = row => row.detail || {};
const safeAccountUrl = helper('safeAccountUrl', {text, detailFor});
assert.equal(safeAccountUrl({accountUrl: 'https://example.com/accounts/harbor'}),
  'https://example.com/accounts/harbor');
assert.equal(safeAccountUrl({detail: {accountUrl: 'https://example.com/accounts/detail'}}),
  'https://example.com/accounts/detail');
for (const value of [undefined, '', 'javascript:alert(1)', 'data:text/html,hello',
                     'file:///etc/passwd', 'http://example.com/account']) {
  assert.equal(safeAccountUrl({accountUrl: value}), '',
    'Only a verified HTTPS customer-record URL may create an account link');
}

const calendarEvent = {source: 'Google Calendar', title: 'Upcoming meeting'};
const genuineChange = {source: 'Salesforce', title: 'Renewal stage advanced'};
const verifiedAccountEvents = () => [calendarEvent, genuineChange];
const verifiedChangeEvents = helper('verifiedChangeEvents', {verifiedAccountEvents, text});
assert.deepEqual(verifiedChangeEvents({}), [genuineChange],
  'What changed remains sourced and never relabels an upcoming calendar meeting');

const priorityInfo = helper('priorityInfo', {
  isFictionalDemo: false, text, detailFor, groups: {workNow: [], watch: [], paused: []}
});
assert.deepEqual(priorityInfo({account: 'No sourced status'}), {label: '', tone: ''},
  'Worklist membership or missing status never invents a customer relationship state');
assert.deepEqual(priorityInfo({status: 'Customer security review'}),
  {label: 'Customer security review', tone: 'watch'});

assert.match(template, /account-person/);
assert.match(template, /account-checklist-item/);
assert.match(template, /account-record-link/);
assert.match(template, /account-change/);
assert.doesNotMatch(template, /appendSection\([^\n]*["'](?:Buying team|Customer context|Why this matters)["']/);
assert.doesNotMatch(template, /appendSection\([^\n]*["'](?:People(?: and| &)? ownership|What changed|Checklist)["']/,
  'Supplementary account evidence lives inside Context and Next Steps, not a fifth section');
assert.match(template, /appendSection\(overview, "Context and Next Steps"\)/);
assert.match(template, /appendSection\(overview, "Priority Rationale"\)/);
"""
        )

    def test_grounded_drawer_context_is_embedded_and_sparse_context_is_omitted(self) -> None:
        self.assert_node(
            r"""
const grounded = {
  account: 'Harbor Health', owner: 'Priya Desai',
  accountUrl: 'https://example.com/accounts/harbor',
  nextAction: 'Share the requested renewal proposal',
  detail: {
    stakeholders: [{name: 'Jordan Park', role: 'Director of Operations'}],
    checklist: [{title: 'Confirm customer security review'}],
    rationale: ['Customer requested a renewal review'],
    events: [{source: 'Salesforce', title: 'Renewal stage advanced'}]
  }
};
const sparse = {account: 'Cedar Financial', detail: {}};
const state = {selected: grounded};
const panel = new Element('div');
const document = {getElementById(id) {
  assert.equal(id, 'detail-panel');
  return panel;
}};
const create = (tag, className, content) => new Element(tag, className, content);
const groups = {workNow: [grounded], watch: [sparse], paused: []};
const detailFor = row => row.detail || {};
const sourcedAccountValue = value => typeof value === 'number' ? value : null;
const suggestedNextAction = row => row.nextAction || '';
const verifiedAccountEvents = row => detailFor(row).events || [];
const verifiedChangeEvents = helper('verifiedChangeEvents', {verifiedAccountEvents, text});
const safeAccountUrl = helper('safeAccountUrl', {text, detailFor});
const appendSection = (parent, label) => {
  const section = create('section', 'detail-section');
  section.appendChild(create('h3', 'section-label', label));
  parent.appendChild(section);
  return section;
};
const renderDetail = helper('renderDetail', {
  state, document, create, groups, text, sourcedAccountValue,
  isFictionalDemo: false, suggestedNextAction, detailFor,
  detailPeople: () => { throw new Error('Never infer fictional people for real accounts'); },
  safeAccountUrl, verifiedChangeEvents, appendSection,
  rationalesFor: row => detailFor(row).rationale || [],
  verifiedMeetingEvents: () => [], verifiedAccountEvents,
  sourceStyle: () => ({}), meetingWhen: () => '',
  communicationStatus: () => ''
});

renderDetail();
const sections = descendants(panel, node => node.className === 'detail-section');
assert.deepEqual(sections.map(section => section.children[0].textContent.trim()),
  ['Context and Next Steps', 'Priority Rationale'],
  'People, checklist, CRM changes, and records belong in the existing context section');
const context = sections[0];
const people = descendants(context, node => node.className === 'account-person');
assert.equal(people.length, 2);
assert.match(people[0].textContent, /Jordan Park.*Director of Operations/);
assert.match(people[1].textContent, /Priya Desai.*Account owner/);
assert.doesNotMatch(context.textContent, /Primary buyer contact|Engaged|Sales Manager/);
assert.match(descendants(context, node => node.className === 'account-checklist-item')[0]
  .textContent, /Confirm customer security review/);
assert.match(descendants(context, node => node.className === 'account-change')[0]
  .textContent, /Renewal stage advanced.*Salesforce/);
const link = descendants(context, node => node.className === 'account-record-link')[0];
assert.equal(link.href, 'https://example.com/accounts/harbor');
assert.equal(link.rel, 'noopener noreferrer');

state.selected = sparse;
renderDetail();
assert.deepEqual(descendants(panel, node => node.className === 'detail-section'), [],
  'Sparse real accounts never invent a context section, people, tasks, changes, or links');
assert.match(panel.textContent, /Cedar Financial/);

state.selected = {account: 'Bare Contact', primaryContact: 'Ava Kim', detail: {}};
renderDetail();
const barePeople = descendants(panel, node => node.className === 'account-person');
assert.equal(barePeople.length, 1);
assert.equal(barePeople[0].textContent.trim(), 'Ava Kim');
assert.doesNotMatch(panel.textContent, /Primary buyer contact|Engaged|Account owner/,
  'A sourced name alone must not acquire an invented role, status, or owner');
"""
        )

    def test_fictional_account_drawer_stays_concise_until_presentation_step(self) -> None:
        self.assert_node(
            r"""
const path = require('node:path');
const portfolio = JSON.parse(fs.readFileSync(path.join(
  path.dirname(process.argv[1]), '../references/demo-portfolio.json'
), 'utf8'));
const account = portfolio.workNow.find(row => row.account === 'Northstar Health');
const state = {selected: account};
const panel = new Element('div');
const document = {getElementById: () => panel};
const create = (tag, className, content) => new Element(tag, className, content);
const groups = {workNow: [account], watch: [], paused: []};
const detailFor = row => portfolio.accountDetails[row.account] || {};
const verifiedAccountEvents = row => detailFor(row).events || [];
const verifiedChangeEvents = helper('verifiedChangeEvents', {verifiedAccountEvents, text});
const suggestedNextAction = helper('suggestedNextAction', {text});
const appendSection = (parent, label) => {
  const section = create('section', 'detail-section');
  section.appendChild(create('h3', 'section-label', label));
  parent.appendChild(section);
  return section;
};
const neverShowVerboseEvidence = () => {
  throw new Error('Fictional demo details must stop before verbose evidence sections');
};
const renderDetail = helper('renderDetail', {
  state, document, create, groups, text,
  sourcedAccountValue: value => value ? 420000 : null,
  isFictionalDemo: true, suggestedNextAction, detailFor,
  detailPeople: row => detailFor(row).stakeholders,
  safeAccountUrl: () => '', verifiedChangeEvents, appendSection,
  rationalesFor: neverShowVerboseEvidence,
  verifiedMeetingEvents: neverShowVerboseEvidence,
  verifiedAccountEvents, sourceStyle: () => ({}), meetingWhen: () => '',
  communicationStatus: () => ''
});

renderDetail();
const sections = descendants(panel, node => node.className === 'detail-section');
assert.deepEqual(sections.map(section => section.children[0].textContent.trim()),
  ['What’s happening', 'Next step', 'People', 'Key signals']);
assert.match(panel.textContent,
  /The 1,200-user pilot met most adoption and deployment goals.*Expansion to 4,500 users depends on resolving the reported uptime concern/);
assert.match(panel.textContent,
  /Review your pilot scorecard and the uptime concern with Jordan Lee, Casey Patel, and Priya Shah/);
const facts = descendants(panel, node => node.className === 'demo-fact');
assert.deepEqual(facts.map(fact => fact.textContent.trim()), [
  'Current pilot 1,200 users', 'Potential rollout 4,500 users', 'Account owner Riley Morgan'
]);
const people = descendants(panel, node => node.className === 'demo-person');
assert.deepEqual(people.map(person => person.textContent.trim()), [
  'Jordan Lee  · Executive sponsor', 'Casey Patel  · Security', 'Priya Shah  · Solutions'
]);
assert.doesNotMatch(panel.textContent,
  /Priority Rationale|Before customer review|presentation|deck|Deal desk|excluded services|Meetings|Recent Communications/i);
const signals = descendants(panel, node => node.className === 'demo-signal');
assert.equal(signals.length, 3);
assert.deepEqual(signals.map(signal => signal.children[0].textContent.trim()),
  ['Granola', 'Slack', 'Salesforce']);
assert.doesNotMatch(signals[2].textContent, /\$420,000/,
  'Source evidence must not repeat the already visible opportunity amount');
const disclosures = descendants(panel, node => node.className === 'demo-activity');
assert.equal(disclosures.length, 1);
assert.equal(disclosures[0].tagName, 'DETAILS');
assert.equal(disclosures[0].attributes.open, undefined,
  'Supporting activity stays collapsed until the user asks for it');
assert.equal(descendants(disclosures[0], node => node.className === 'account-change').length, 3);
"""
        )

    def test_saved_dashboard_goal_selects_one_grounded_focus_without_changing_navigation(
        self,
    ) -> None:
        self.assert_node(
            r"""
for (const [goal, mode] of [
  ['Account priorities and changes (Recommended)', 'priorities'],
  ['Pipeline and forecast risk', 'pipeline'],
  ['Customer meetings and follow-ups', 'meetings']
]) {
  for (const payload of [
    {dashboardGoal: goal}, {preferences: {goal}}, {selectedGoal: goal}, {goal}
  ]) {
    const selectedDashboardGoal = helper('selectedDashboardGoal', {payload, text});
    assert.equal(selectedDashboardGoal(), mode,
      'Existing saved goal fields all choose the same source-grounded focus mode');
  }
}
assert.equal(helper('selectedDashboardGoal', {payload: {}, text})(), '',
  'A seller never receives an invented dashboard goal');
for (const id of ['seller-focus-card', 'seller-focus-heading', 'seller-focus-list']) {
  assert.match(template, new RegExp('id="' + id + '"'));
}
assert.equal((template.match(/role="tab"/g) || []).length, 3,
  'Goal focus complements the existing Home, Accounts, and Pipeline views');
for (const id of ['tab-home', 'tab-accounts', 'tab-pipeline', 'account-search',
                  'account-filter-all', 'priority-sort']) {
  assert.match(template, new RegExp('id="' + id + '"'));
}
"""
        )

    def test_priority_focus_uses_sourced_rationale_changes_and_existing_account_drawer(
        self,
    ) -> None:
        self.assert_node(
            FOCUS_BOOTSTRAP
            + r"""
const verified = {
  account: 'Harbor Health', priorityScore: 92,
  nextAction: 'Confirm security-review owner',
  rationale: ['Customer requested a security review'],
  changes: [{source: 'Salesforce', title: 'Security reviewer confirmed'}]
};
const unsupported = {account: 'Unverified priority', detail: {}};
const focused = inspectFocus('Account priorities and changes', [verified, unsupported]);
assert.equal(focused.mode, 'priorities');
assert.equal(focused.card.hidden, false);
assert.equal(focused.list.children.length, 1);
assert.match(focused.list.textContent, /Harbor Health/);
assert.match(focused.list.textContent, /Confirm security-review owner/,
  'The chosen account-priority focus retains the verified next action');
assert.match(focused.list.textContent, /Security reviewer confirmed/,
  'A verified next action must not hide the selected grounded account change');
assert.doesNotMatch(focused.list.textContent, /Unverified priority|Unavailable|0 accounts/i);
assert.equal(focused.list.children[0].tagName, 'BUTTON');
assert.equal(focused.list.children[0].attributes['aria-controls'], 'account-drawer');
focused.list.children[0].handlers.click();
assert.deepEqual(focused.opened, [verified],
  'The focus card opens the existing account drawer instead of creating another workspace');

const repeated = inspectFocus('Account priorities and changes', [{
  account: 'Same Signal', nextAction: 'Security reviewer confirmed',
  changes: [{source: 'Salesforce', title: 'Security reviewer confirmed'}]
}]);
assert.equal((repeated.list.textContent.match(/Security reviewer confirmed/g) || []).length, 1,
  'Identical verified action and change text is not repeated');
"""
        )

    def test_pipeline_focus_requires_verified_opportunity_and_preserves_sourced_zero(
        self,
    ) -> None:
        self.assert_node(
            FOCUS_BOOTSTRAP
            + r"""
const accountOnly = {account: 'Whole Account Only', accountValue: 250000};
const unknownAmount = {
  account: 'Known Opportunity', stage: 'Security review',
  opportunity: {present: true, amount: null}
};
const sourcedZero = {
  account: 'Grounded Zero Deal', stage: 'Procurement',
  opportunity: {present: true, amount: 0, display: '$0'}
};
const focused = inspectFocus('Pipeline and forecast risk',
  [accountOnly, unknownAmount, sourcedZero]);
assert.equal(focused.mode, 'pipeline');
assert.equal(focused.card.hidden, false);
assert.ok(focused.list.children.every(button => button.tagName === 'BUTTON'),
  'Pipeline focus retains working account-drawer controls');
assert.match(focused.list.textContent, /Known Opportunity/);
assert.match(focused.list.textContent, /Grounded Zero Deal/);
assert.doesNotMatch(focused.list.textContent, /Whole Account Only|Unavailable|\$250,?000/);
assert.equal(focused.list.children.length, 2,
  'Unknown opportunity amounts remain honest while verified $0 remains a real deal');

const empty = inspectFocus('Pipeline and forecast risk', [accountOnly]);
assert.equal(empty.card.hidden, true,
  'An account-level amount cannot fabricate a pipeline, risk, forecast, or zero KPI');
assert.equal(empty.list.children.length, 0);
"""
        )

    def test_meeting_focus_requires_future_events_or_verified_open_followups(self) -> None:
        self.assert_node(
            FOCUS_BOOTSTRAP
            + r"""
const future = {
  account: 'Upcoming Customer',
  meetings: [{source: 'Google Calendar', title: 'Security review', when: 'Tomorrow'}]
};
const followup = {account: 'Verified Follow-up', openItems: 2,
  nextAction: 'Confirm security-review owner'};
const knownZero = {account: 'No Open Follow-ups', openItems: 0};
const unknown = {account: 'No Calendar Evidence', openItems: null};
const focused = inspectFocus('Customer meetings and follow-ups',
  [future, followup, knownZero, unknown]);
assert.equal(focused.mode, 'meetings');
assert.equal(focused.card.hidden, false);
assert.equal(focused.list.children.length, 2);
assert.match(focused.list.textContent, /Upcoming Customer/);
assert.match(focused.list.textContent, /Verified Follow-up/);
assert.doesNotMatch(focused.list.textContent,
  /No Open Follow-ups|No Calendar Evidence|0 meetings|Unavailable/);

for (const [goal, rows] of [
  ['Customer meetings and follow-ups', [knownZero, unknown]],
  ['Account priorities and changes', [unknown]],
  [null, [future, followup]]
]) {
  const empty = inspectFocus(goal, rows);
  assert.equal(empty.card.hidden, true,
    'Absent goal or matching grounded evidence hides the entire focus card');
  assert.equal(empty.list.children.length, 0);
}
"""
        )


if __name__ == "__main__":
    unittest.main()
