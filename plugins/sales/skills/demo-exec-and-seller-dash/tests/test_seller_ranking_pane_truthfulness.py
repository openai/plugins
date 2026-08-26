"""Executable safeguards for the legacy, source-grounded seller ranking pane."""

from __future__ import annotations

import unittest
from pathlib import Path

from sales_test_support import SalesTestCase

PLUGIN = Path(__file__).resolve().parents[2]
TEMPLATE = PLUGIN / "seller-account-dashboard" / "assets" / "account-priority-pane.template.html"
FICTIONAL = PLUGIN / "demo-exec-and-seller-dash" / "references" / "demo-portfolio.json"

NODE_PRELUDE = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync(process.argv[1], 'utf8');
const fictional = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function bodyFor(name) {
  const match = source.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'Expected executable helper ' + name);
  return match[1];
}

class Node {
  constructor(tag, className = '', copy) {
    this.tagName = tag.toUpperCase();
    this.className = className;
    this.children = [];
    this.attributes = {};
    this.handlers = {};
    this.hidden = false;
    this.innerHTML = '';
    this.copy = copy == null ? '' : String(copy);
    this.style = { setProperty() {} };
    this.classList = { toggle() {} };
  }
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { children.forEach(child => this.appendChild(child)); }
  replaceChildren(...children) { this.children = [...children]; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  addEventListener(name, handler) { this.handlers[name] = handler; }
  focus() { this.focused = true; }
  get childElementCount() { return this.children.length; }
  get textContent() {
    return this.copy + this.children.map(child => child.textContent || '').join(' ');
  }
  set textContent(value) { this.copy = String(value); }
}

const element = (tag, className, copy) => new Node(tag, className, copy);
const sourcedText = new Function('value', bodyFor('sourcedText'));
const sourcedRank = new Function('value', bodyFor('sourcedRank'));
const text = (value, fallback = 'Not available') => {
  const normalized = value == null ? '' : String(value).trim();
  return normalized || fallback;
};
const state = { tab: 'workNow', complete: new Set(), selected: null };
const rowKey = (row, index) => new Function(
  'row', 'index', 'state', 'text', 'sourcedRank', bodyFor('rowKey')
)(row, index, state, text, sourcedRank);
const setIcon = node => node;
const makeAccountRow = new Function(
  'row', 'index', 'rowKey', 'element', 'state', 'sourcedRank', 'initials',
  'logoColor', 'text', 'sourcedText', 'setIcon', 'render', 'openDrawer',
  bodyFor('makeAccountRow')
);

function renderRow(row, index = 0) {
  return makeAccountRow(
    row, index, rowKey, element, state, sourcedRank, () => 'HH', () => '#167a55',
    text, sourcedText, setIcon, () => {}, () => {}
  );
}
"""


class SellerRankingPaneTruthfulnessTests(SalesTestCase):
    def run_node(self, assertions: str) -> None:
        self.assert_node_script(NODE_PRELUDE + assertions, str(TEMPLATE), str(FICTIONAL))

    def test_missing_ranks_never_become_positional_priorities(self) -> None:
        self.run_node(
            r"""
for (const rank of [undefined, null, '', 0, -1, 1.5, 'unknown']) {
  assert.equal(sourcedRank(rank), null);
  const row = renderRow({account: 'Harbor Health', rank}, 8);
  assert.equal(row.children[0].textContent, '', 'Unknown rank must stay visually absent');
  assert.equal(row.children[0].attributes['aria-hidden'], 'true');
  assert.doesNotMatch(row.textContent, /\b9\b/,
    'The display must never expose the positional index as a priority');
}

assert.equal(sourcedRank(7), 7);
assert.equal(sourcedRank('3'), 3);
assert.equal(renderRow({account: 'Grounded Account', rank: 7}, 0)
  .children[0].textContent, '7');
assert.notEqual(rowKey({account: 'Duplicate account'}, 0),
  rowKey({account: 'Duplicate account'}, 1),
  'Private UI state retains unique keys without displaying invented rank');
"""
        )

    def test_missing_value_owner_due_action_and_confidence_disappear(self) -> None:
        self.run_node(
            r"""
for (const sentinel of [
  null, undefined, '', 'Value unavailable', 'Unassigned', 'Due not set',
  'No date set', 'Not available', 'Not reported', 'Unknown', '—'
]) assert.equal(sourcedText(sentinel), '', 'Legacy missing marker must not leak: ' + sentinel);

for (const row of [
  {account: 'Harbor Health'},
  {
    account: 'Harbor Health', value: 'Value unavailable', owner: 'Unassigned',
    dueDate: 'No date set', nextAction: 'Not available', confidence: 'Unknown'
  }
]) {
  const rendered = renderRow(row);
  assert.match(rendered.textContent, /Harbor Health/);
  assert.doesNotMatch(rendered.textContent,
    /unavailable|unassigned|not available|not reported|no date|not set|unknown|confidence/i);
  assert.equal(rendered.children[2].children.length, 0,
    'An unknown financial value and rationale leave no fake content');
  assert.equal(rendered.children[3].children.length, 0,
    'An unsupported next action must not create a dead completion button');
  assert.equal(rendered.children[4].children.length, 0,
    'Missing owner and due date must not leave icon-only placeholder rows');
}

const verified = renderRow({
  account: 'Harbor Health', rank: 2, value: '$0', owner: 'Casey Rivera',
  dueDate: 'Friday', motion: 'Expansion', stage: 'Customer review', confidence: 'High',
  whyItMatters: 'Verified customer requested a review.',
  nextAction: 'Review the customer request.'
});
assert.match(verified.textContent,
  /2.*Harbor Health.*Expansion · Customer review.*High confidence.*\$0.*Casey Rivera.*Due Friday/);
assert.equal(verified.children[3].children.length, 2,
  'A genuinely sourced action retains both working action controls');
"""
        )

    def test_drawer_and_source_details_omit_unknown_values(self) -> None:
        self.run_node(
            r"""
const drawer = new Node('aside');
const backdrop = {hidden: true};
const document = {body: {style: {}}, createTextNode: value => new Node('text', '', value)};
const appendSection = new Function(
  'label', 'value', 'emphasize', 'sourcedText', 'element', 'drawer',
  bodyFor('appendDrawerSection')
);
const appendDrawerSection = (label, value, emphasize) => appendSection(
  label, value, emphasize, sourcedText, element, drawer
);
const safeAccountUrl = new Function('value', bodyFor('safeAccountUrl'));
const openDrawer = new Function(
  'row', 'state', 'drawer', 'setIcon', 'element', 'closeDrawer', 'initials',
  'logoColor', 'tabConfig', 'text', 'sourcedText', 'appendDrawerSection',
  'safeAccountUrl', 'document', 'backdrop', bodyFor('openDrawer')
);

function inspect(row) {
  drawer.replaceChildren();
  openDrawer(
    row, state, drawer, setIcon, element, () => {}, () => 'HH', () => '#167a55',
    [{key: 'workNow', label: 'Work now'}], text, sourcedText, appendDrawerSection,
    safeAccountUrl, document, backdrop
  );
  return drawer.textContent;
}

const missing = inspect({account: 'Harbor Health', value: 'Value unavailable'});
assert.match(missing, /Harbor Health/);
assert.doesNotMatch(missing,
  /Opportunity value|Why it matters|Next action|unavailable|not available|confidence|·/i,
  'The drawer omits whole unsupported financial, context, and action sections');

const grounded = inspect({
  account: 'Harbor Health', value: '$0', stage: 'Customer review',
  nextAction: 'Review the verified customer request.'
});
assert.match(grounded, /Opportunity value.*\$0/);
assert.match(grounded, /Customer review/);
assert.match(grounded, /Next action.*verified customer request/);
"""
        )

    def test_source_claims_avatar_and_search_controls_are_truthful_and_accessible(
        self,
    ) -> None:
        self.run_node(
            r"""
assert.match(source,
  /\.search-clear\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;[^}]*flex:\s*0\s+0\s+44px;/,
  'Search clear retains a 44px accessible hit target');
assert.match(source,
  /<span id="avatar" class="avatar" aria-label="Seller initials"><\/span>/,
  'A seller-initials badge is an inert semantic span rather than a dead profile button');
assert.doesNotMatch(source, /<button[^>]*id="avatar"/,
  'The pane cannot expose an unimplemented profile action');
assert.match(source, /<div id="sync-state" class="sync-state"[^>]*hidden>/,
  'Source claims stay hidden until actual verified source identity and status are known');
assert.match(source, /source\?\.verified === true/,
  'A supplied source list requires an actually verified connector');
assert.doesNotMatch(source, /Connected sources used|Value unavailable|Unassigned|Due not set/,
  'Legacy missing-value and fake-connected text must not ship in visible fallback markup');
"""
        )

    def test_existing_fictional_rows_preserve_grounded_ranking_workflow(self) -> None:
        self.run_node(
            r"""
for (const row of fictional.workNow) {
  const rendered = renderRow(row);
  assert.equal(rendered.children[0].textContent, String(row.rank));
  assert.match(rendered.textContent, new RegExp(row.account));
  assert.match(rendered.textContent, new RegExp(row.owner));
  assert.equal(rendered.children[3].children.length, 2);
}
"""
        )


if __name__ == "__main__":
    unittest.main()
