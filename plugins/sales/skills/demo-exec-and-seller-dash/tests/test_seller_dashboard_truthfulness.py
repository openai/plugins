"""Executable regressions for source-grounded seller dashboard review feedback."""

from __future__ import annotations

import unittest
from pathlib import Path

from sales_test_support import SalesTestCase

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
PORTFOLIO_PATH = SKILL_DIRECTORY / "references" / "demo-portfolio.json"

NODE_BOOTSTRAP = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const portfolio = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const text = (value, fallback) => value == null || String(value).trim() === ''
  ? fallback || '' : String(value).trim();

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'The source-grounded seller helper ' + name + ' must exist');
  return match[1];
}
"""


class SellerDashboardTruthfulnessTests(SalesTestCase):
    def assert_node_regression(self, script: str) -> None:
        self.assert_node_script(NODE_BOOTSTRAP + script, str(TEMPLATE_PATH), str(PORTFOLIO_PATH))

    def test_book_totals_distinguish_known_unknown_and_legitimate_zero_values(
        self,
    ) -> None:
        self.assert_node_regression(
            r"""
const accountValue = new Function('value', 'text', bodyFor('sourcedAccountValue'));
const sourcedAccountValue = value => accountValue(value, text);
const compactMoney = amount => amount >= 1e6
  ? '$' + (amount / 1e6).toFixed(2).replace(/0$/, '') + 'M'
  : '$' + Math.round(amount / 1000) + 'K';
const caption = new Function(
  'rows', 'sourcedAccountValue', 'compactMoney', 'isFictionalDemo',
  bodyFor('bookValueCaption')
);

for (const unavailable of [null, undefined, '', 'Value unavailable', 'Not reported']) {
  assert.equal(sourcedAccountValue(unavailable), null,
    'Missing and nonnumeric account values must remain unknown');
}
assert.equal(sourcedAccountValue(0), 0);
assert.equal(sourcedAccountValue('$0'), 0);
assert.equal(sourcedAccountValue('$250,000'), 250000);
assert.equal(sourcedAccountValue('$250K'), 250000);

assert.equal(
  caption([{value: '$250,000'}, {value: 'Value unavailable'}],
    sourcedAccountValue, compactMoney, false),
  '$250K across known accounts',
  'A partial sourced total remains useful without exposing missing-data process copy'
);
assert.equal(
  caption([{accountValue: '$250,000', opportunityValue: '$45,000'},
    {accountValue: '$90,000'}], sourcedAccountValue, compactMoney, false),
  '$340K across your book',
  'Book totals use whole-account values rather than distinct opportunity amounts'
);
assert.equal(
  caption([{value: null}, {value: 'Not reported'}],
    sourcedAccountValue, compactMoney, false),
  '',
  'An unsupported book value disappears instead of becoming a prominent warning'
);
assert.equal(caption([], sourcedAccountValue, compactMoney, false), '',
  'An empty account universe must not fabricate a verified zero-value book');
assert.equal(
  caption([{value: 0}, {value: '$250,000'}],
    sourcedAccountValue, compactMoney, false),
  '$250K across your book',
  'A verified zero remains a known value and does not make a complete book partial'
);
const fictionalRows = [...portfolio.workNow, ...portfolio.watch, ...portfolio.paused];
assert.equal(
  caption(fictionalRows, sourcedAccountValue, compactMoney, true),
  '$3.37M across your book',
  'The fully grounded fictional demonstration retains its existing complete total'
);
assert.doesNotMatch(template, /Book total unavailable|across known accounts · total unavailable/);
"""
        )

    def test_calendar_events_require_future_evidence_and_past_meetings_remain_history(
        self,
    ) -> None:
        self.assert_node_regression(
            r"""
const timing = new Function('event', 'now', 'text', 'isFictionalDemo', bodyFor('meetingTiming'));
const now = new Date('2026-08-07T12:00:00Z');
const future = {source: 'Google Calendar', when: '2026-08-08T14:00:00Z'};
const past = {source: 'Outlook Calendar', when: '2026-08-06T14:00:00Z'};
const unparseable = {source: 'Google Calendar', when: 'Timing to confirm'};
const realTiming = event => timing(event, now, text, false);
assert.equal(realTiming(future), 'upcoming');
assert.equal(realTiming(past), 'past');
assert.equal(realTiming(unparseable), 'unknown',
  'An unparseable calendar value cannot silently invent an upcoming meeting');
assert.equal(realTiming({...unparseable, classification: 'upcoming'}), 'upcoming',
  'Explicitly supplied future classification remains valid evidence');
assert.equal(realTiming({...unparseable, classification: 'completed'}), 'past');
assert.equal(realTiming({source: 'Slack', when: future.when}), 'not-calendar');
assert.equal(timing(unparseable, now, text, true), 'upcoming',
  'Fictional rolling demo invitations retain their existing presentation');

const verifiedAccountEvents = row => row.events || [];
const collectMeetings = new Function(
  'row', 'verifiedAccountEvents', 'meetingTiming', bodyFor('verifiedMeetingEvents')
);
const mixed = {account: 'Harbor Health', events: [past, future, unparseable]};
assert.deepEqual(collectMeetings(mixed, verifiedAccountEvents, realTiming), [future]);

const recentAccountActivity = new Function(
  'rows', 'verifiedAccountEvents', 'text', 'isFictionalDemo', 'meetingTiming',
  bodyFor('recentAccountActivity')
);
const rows = [
  {account: 'Completed meeting', events: [past]},
  {account: 'Future meeting', events: [future]},
  {account: 'Unknown meeting', events: [unparseable]},
  {account: 'Customer message', events: [
    {source: 'Slack', when: '2026-08-07T09:00:00Z'}
  ]}
];
const historical = recentAccountActivity(rows, verifiedAccountEvents, text, false, realTiming);
assert.deepEqual(historical.map(item => item.row.account),
  ['Customer message', 'Completed meeting']);
const fictional = recentAccountActivity(rows, verifiedAccountEvents, text, true, realTiming);
assert.deepEqual(fictional.map(item => item.row.account), ['Customer message'],
  'The connector-free fictional demo continues to exclude calendar entries from history');
"""
        )

    def test_meeting_counts_require_verified_calendar_coverage_and_preserve_zero(self) -> None:
        self.assert_node_regression(
            r"""
const countMeetings = new Function(
  'events', 'payload', 'sources', 'isFictionalDemo', 'text',
  bodyFor('sourcedUpcomingMeetingCount')
);
const calendar = [{name: 'Google Calendar'}];
assert.equal(countMeetings([], {}, [], false, text), null,
  'A missing calendar cannot be presented as zero upcoming meetings');
assert.equal(countMeetings([], {}, calendar, false, text), null,
  'A connected calendar alone does not prove an exhaustive zero-meeting result');
assert.equal(countMeetings([], {upcomingMeetingCount: 0}, [], false, text), null,
  'A declared count without a verified calendar source is not grounded');
assert.equal(countMeetings([], {upcomingMeetingCount: 0}, calendar, false, text), 0,
  'An explicitly sourced zero meeting count remains visible');
assert.equal(countMeetings([{title: 'Verified review'}], {}, calendar, false, text), 1);
assert.equal(countMeetings([], {}, [], true, text), 0,
  'The intentionally complete fictional fixture retains its existing presentation');
"""
        )

    def test_missing_optional_account_evidence_never_creates_visible_fallback_copy(self) -> None:
        self.assert_node_regression(
            r"""
for (const warning of [
  'Book total unavailable',
  'total unavailable',
  'No verified upcoming meetings were provided.',
  'No verified recent customer communications were provided.',
  'No verified account follow-ups need attention.',
  'No upcoming meeting context was provided.',
  'No verified recent account activity was provided.',
  'No verified commercial opportunities were provided.'
]) assert.ok(!template.includes(warning), warning + ' must not be rendered');

assert.match(template,
  /if \(upcomingMeetings\.length\) \{\s*const meetingSection = appendSection\(overview, "Meetings"\)/,
  'Account meeting sections are created only when real upcoming meetings exist');
assert.match(template,
  /if \(recentMessages\.length\) \{\s*const communications = appendSection\(overview, "Recent Communications"\)/,
  'Account communication sections are created only when customer messages exist');
assert.match(template,
  /if \(sourcedOpportunity\.amount !== null\) opportunity\.appendChild/,
  'Unknown opportunity values never become visible account-cell disclaimers');
assert.match(template,
  /if \(sourcedAccountValue\(accountValue\) !== null\) top\.appendChild/,
  'Unknown opportunity values never become account-drawer amount disclaimers');
assert.match(template, /\[hidden\]\s*\{\s*display:\s*none\s*!important/,
  'Unsupported grid cards and layout containers must actually collapse');
assert.match(template, /homeLayout\.hidden = !hasAttention && !hasSupportingCards/,
  'The entire home grid disappears when none of its cards has real content');
assert.match(template, /attentionCount\.hidden = !hasFollowUpCount/,
  'Suggested work must not invent a zero-open follow-up badge');
"""
        )

    def test_empty_pipeline_disappears_while_verified_zero_value_remains(self) -> None:
        self.assert_node_regression(
            r"""
const parseValue = new Function('value', 'text', bodyFor('sourcedAccountValue'));
const sourcedAccountValue = value => parseValue(value, text);
function opportunities(fictional) {
  const inspect = new Function(
    'row', 'isFictionalDemo', 'sourcedAccountValue', 'text', 'detailFor',
    bodyFor('verifiedOpportunity')
  );
  return row => inspect(row, fictional, sourcedAccountValue, text, row => row.detail || {});
}
const compactMoney = amount => '$' + Math.round(amount / 1000) + 'K';
function create(tag, className, content) {
  return {
    tag, className, textContent: content || '', dataset: {}, children: [],
    append(...children) { this.children.push(...children); },
    appendChild(child) { this.children.push(child); }
  };
}
function pipeline(rows, fictional = false) {
  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, {
        hidden: false, textContent: '', children: [],
        replaceChildren() { this.children = []; },
        appendChild(child) { this.children.push(child); }
      });
      return elements.get(id);
    }
  };
  const render = new Function(
    'allRows', 'verifiedOpportunity', 'pipelinePhase', 'document', 'sortedAccounts',
    'create', 'compactMoney', 'pipelineAccountButton', bodyFor('renderPipeline')
  );
  render(rows, opportunities(fictional), () => 'commercial', document, () => rows,
    create, compactMoney, row => create('button', 'pipeline-row', row.account));
  return id => elements.get(id);
}

const missing = pipeline([{account: 'Harbor Health', accountValue: '$250,000'}]);
assert.equal(missing('tab-pipeline').hidden, true);
assert.equal(missing('pipeline-card').hidden, true);
assert.equal(missing('opportunities-count').textContent, '');
assert.deepEqual(missing('opportunity-list').children, [],
  'No fabricated empty-state widget remains when commercial records are unsupported');

const zero = pipeline([{account: 'Cedar Energy', accountValue: '$250,000',
  opportunityValue: 0}]);
assert.equal(zero('tab-pipeline').hidden, false);
assert.equal(zero('pipeline-card').hidden, false);
assert.equal(zero('opportunities-count').textContent, '1 active');
assert.equal(zero('opportunity-list').children.length, 1,
  'A verified zero-value opportunity remains actionable');
const zeroPhase = zero('opportunity-list').children[0];
assert.equal(zeroPhase.children[0].children[1].textContent, '1 account · $0K');

const mixed = pipeline([
  {account: 'Harbor Health', accountValue: '$250,000', opportunityValue: '$45,000'},
  {account: 'Cedar Energy', accountValue: '$90,000'},
  {account: 'Stage-only customer', accountValue: '$20,000', hasOpportunity: true}
]);
assert.equal(mixed('opportunities-count').textContent, '2 active');
const mixedPhase = mixed('opportunity-list').children[0];
assert.equal(mixedPhase.children[0].children[1].textContent, '2 accounts · $45K',
  'Only verified opportunity values contribute to the pipeline total');
assert.deepEqual(mixedPhase.children.slice(1).map(row => row.textContent),
  ['Harbor Health', 'Stage-only customer'],
  'Account-only records never become opportunities, while sourced amountless stages remain');

const amountless = pipeline([{account: 'Stage-only customer', hasOpportunity: true}]);
assert.equal(amountless('opportunity-list').children[0].children[0].children[1].textContent,
  '1 account', 'An amountless sourced opportunity does not invent a zero-dollar total');

const fictional = pipeline([{account: 'Fictional account', value: '$250,000'}], true);
assert.equal(fictional('opportunities-count').textContent, '1 active',
  'Intentional fictional demonstrations retain their legacy row.value opportunity');
"""
        )

    def test_followups_require_explicit_tasks_or_verified_unresolved_communications(
        self,
    ) -> None:
        self.assert_node_regression(
            r"""
const workNow = {
  account: 'Harbor Health', nextAction: 'Review verified account context', events: []
};
const explicit = {account: 'Cedar Energy', openItems: ['Confirm buyer', 'Review request']};
const groups = {workNow: [workNow], watch: [explicit], paused: []};
const detailFor = row => row.detail || {};
const verifiedAccountEvents = row => row.events || [];
const communicationStatus = event => event.replyStatus === 'Unresolved'
  ? 'Unresolved' : 'Update';
const countOpenItems = new Function(
  'row', 'detailFor', 'verifiedAccountEvents', 'communicationStatus', 'groups', 'text',
  'isFictionalDemo', bodyFor('openItemsFor')
);
const count = (row, fictional = false) => countOpenItems(
  row, detailFor, verifiedAccountEvents, communicationStatus, groups, text, fictional
);

assert.equal(count(workNow), null,
  'A work-now bucket and suggested action cannot turn unknown task evidence into zero');
assert.equal(count(workNow, true), 1,
  'The fictional demo retains its existing illustrative work-now fallback');
assert.equal(count(explicit), 2);
assert.equal(count({openItems: []}), 0, 'An explicitly empty sourced task list remains zero');
assert.equal(count({openTaskCount: 0}), 0, 'An explicitly sourced zero task count remains zero');
assert.equal(count({detail: {checklist: ['First', 'Second', 'Third']}}), 3);
assert.equal(count({events: [{source: 'Gmail', replyStatus: 'Unresolved'}]}), 1);
assert.equal(count({events: [{source: 'Slack', replyStatus: 'Replied'}]}), null);
assert.equal(count({events: [{source: 'Salesforce', replyStatus: 'Unresolved'}]}), null,
  'Only verified customer communication providers can create unanswered-message counts');

assert.match(template, /if \(openItems !== null\) items\.append/,
  'Unknown account tasks must not render an invented zero-open badge');
assert.match(template, /if \(nextAction\) \{\s*const action = create\("div", "action-card"\)/,
  'A customer action card exists only for a verified next action');
assert.match(template, /if \(groundedReasons\.length\) \{\s*const rationale = appendSection/,
  'Missing priority evidence cannot create an empty rationale section');
assert.match(template, /stageDetails\.join\(" · "\)/,
  'Missing stage and timing fields cannot leave dangling account separators');

const header = new Function(
  'payload', 'seller', 'sellerName', 'sellerFirstName', 'allRows', 'groups', 'sources',
  'isFictionalDemo', 'text', 'initials', 'bookValueCaption', 'openItemsFor', 'document',
  bodyFor('renderHeader')
);
function renderHeader(fictional) {
  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, {textContent: '', hidden: false, title: ''});
      return elements.get(id);
    },
    querySelector() { return {classList: {toggle() {}}}; }
  };
  header(
    {company: {name: 'Summit'}, scope: {}, generatedAt: '2026-08-07'},
    {team: 'Enterprise'}, 'Casey Rivera', 'Casey', [workNow, explicit], groups,
    [], fictional, text, () => 'S', () => 'Total unavailable', row => count(row, fictional),
    document
  );
  return elements.get('renewal-value-metric').textContent;
}
assert.equal(renderHeader(false), '2',
  'Real follow-up summary aggregates only verified tasks across the complete account book');
assert.equal(renderHeader(true), '1',
  'The fictional demo preserves its existing work-now account count');
"""
        )

    def test_mobile_account_layout_prevents_clipping_and_preserves_touch_targets(self) -> None:
        self.assert_node_regression(
            r"""
assert.match(template, /\.work-item\s*\{[^}]*min-width:\s*0;/,
  'Meeting-card grid items must be allowed to shrink within narrow mobile and tablet cards');
assert.match(template, /\.sort-button\s*\{[^}]*min-height:\s*44px;/,
  'Account sorting must retain a minimum 44-pixel touch target');
assert.match(template, /\.drawer-close\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;/,
  'Account drawer Close must meet the recommended 44-by-44-pixel touch target');
assert.match(template,
  /@media \(max-width: 720px\)\s*\{[\s\S]*?\.account-row \.status-cell, \.account-row \.open-items-cell\s*\{\s*display:\s*none;/,
  'Specific mobile selectors must hide desktop-only cells after generic table-cell rules');
assert.match(template,
  /@media \(max-width: 720px\)\s*\{[\s\S]*?\.sort-button\s*\{[^}]*max-width:\s*100%;[^}]*white-space:\s*normal;/,
  'The mobile priority-sort label must wrap inside its visible account-table column');
assert.match(template,
  /@media \(max-width: 720px\)\s*\{[\s\S]*?\.opportunity-value\s*\{[^}]*white-space:\s*normal;[^}]*overflow-wrap:\s*anywhere;/,
  'Missing real opportunity values must remain visibly unavailable rather than clipped');
assert.match(template,
  /@media \(max-width: 410px\)\s*\{[\s\S]*?\.account-table thead tr, \.account-row\s*\{[^}]*minmax\(82px, \.56fr\)/,
  'The narrowest seller accounts view must reserve sufficient width for its sort control');
assert.match(template, /\.account-drawer\s*\{[^}]*animation:\s*drawer-backdrop-in/,
  'The account drawer backdrop must enter with an accessible polished animation');
assert.match(template,
  /\.account-drawer-panel\s*\{[^}]*animation:\s*drawer-slide-in[^}]*transition:\s*transform[^}]*opacity/,
  'Account details should animate smoothly with performant transform and opacity');
assert.match(template,
  /@keyframes\s+drawer-slide-in\s*\{[\s\S]*?translateX[\s\S]*?opacity/,
  'The account drawer must actually slide and fade instead of appearing abruptly');
assert.match(template,
  /\.account-drawer\[data-state="closing"\][\s\S]*?drawer-backdrop-out/,
  'The account drawer backdrop remains visible throughout its dismissal animation');
assert.match(template,
  /\.account-drawer\[data-state="closing"\] \.account-drawer-panel[\s\S]*?drawer-slide-out/,
  'The account drawer panel slides and fades out before it is hidden');
assert.match(template,
  /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{[\s\S]*?\.account-drawer,\s*\.account-drawer-panel\s*\{[^}]*animation:\s*none\s*!important;[^}]*transition:\s*none\s*!important;/,
  'Reduced-motion users must retain an immediate, accessible account detail view');
"""
        )

    def test_drawer_dismissal_animates_restores_focus_and_honors_reduced_motion(
        self,
    ) -> None:
        self.assert_node_regression(
            r"""
const closeAccountDrawer = new Function(
  'state', 'document', 'window', 'renderAccounts', bodyFor('closeAccountDrawer')
);
const beginDrawerOpening = new Function(
  'state', 'document', 'window', bodyFor('beginDrawerOpening')
);

function harness(reducedMotion = false, previousConnected = true) {
  let listener;
  let removedListener;
  let timeoutCleared = false;
  let unlocked = false;
  let restored = '';
  const panel = {
    addEventListener(name, callback) {
      assert.equal(name, 'animationend');
      listener = callback;
    },
    removeEventListener(name, callback) { removedListener = callback; }
  };
  const drawer = {
    hidden: false,
    dataset: {},
    querySelector(selector) {
      return selector === '.account-drawer-panel' ? panel : null;
    }
  };
  const previous = {
    isConnected: previousConnected,
    getClientRects() { return previousConnected ? [1] : []; },
    focus() { restored = 'previous'; }
  };
  const selected = {
    dataset: {account: 'Harbor Health'},
    focus() { restored = 'selected'; }
  };
  const close = {focus() {}};
  const detail = {scrollTop: 8};
  const state = {
    drawerOpen: true,
    drawerCloseTimer: null,
    drawerCloseListener: null,
    returnFocus: previous,
    returnAccount: 'Harbor Health'
  };
  const document = {
    body: {classList: {
      add() {},
      remove() { unlocked = true; }
    }},
    getElementById(id) {
      return {
        'account-drawer': drawer,
        'account-drawer-close': close,
        'detail-panel': detail
      }[id];
    },
    querySelectorAll(selector) {
      return selector === '.account-row' ? [selected] : [];
    }
  };
  const window = {
    matchMedia(query) {
      assert.equal(query, '(prefers-reduced-motion: reduce)');
      return {matches: reducedMotion};
    },
    setTimeout(callback, delay) {
      assert.equal(delay, 320);
      return 31;
    },
    clearTimeout(timer) {
      assert.equal(timer, 31);
      timeoutCleared = true;
    }
  };
  return {
    state, document, window, drawer,
    listener() { return listener; },
    removedListener() { return removedListener; },
    restored() { return restored; },
    unlocked() { return unlocked; },
    timeoutCleared() { return timeoutCleared; }
  };
}

for (const dismissal of ['Escape', 'close button', 'backdrop']) {
  const animated = harness();
  closeAccountDrawer(animated.state, animated.document, animated.window, () => {});
  assert.equal(animated.drawer.hidden, false,
    dismissal + ' keeps the drawer mounted during its exit animation');
  assert.equal(animated.drawer.dataset.state, 'closing');
  assert.equal(animated.state.drawerCloseTimer, 31);
  assert.equal(animated.restored(), '', 'Focus must remain inside until closing finishes');
  animated.listener()();
  assert.equal(animated.drawer.hidden, true);
  assert.equal(animated.drawer.dataset.state, undefined);
  assert.equal(animated.state.drawerCloseTimer, null);
  assert.equal(animated.restored(), 'previous');
  assert.equal(animated.unlocked(), true);
}

const disconnected = harness(false, false);
closeAccountDrawer(disconnected.state, disconnected.document, disconnected.window, () => {});
disconnected.listener()();
assert.equal(disconnected.restored(), 'selected',
  'A replaced source row restores focus to its current grounded account row');

const reduced = harness(true);
closeAccountDrawer(reduced.state, reduced.document, reduced.window, () => {});
assert.equal(reduced.drawer.hidden, true, 'Reduced-motion dismissal is immediate');
assert.equal(reduced.state.drawerCloseTimer, null);
assert.equal(reduced.restored(), 'previous');

const reopened = harness();
closeAccountDrawer(reopened.state, reopened.document, reopened.window, () => {});
const staleFinish = reopened.listener();
reopened.state.drawerOpen = true;
beginDrawerOpening(reopened.state, reopened.document, reopened.window);
assert.equal(reopened.drawer.hidden, false);
assert.equal(reopened.drawer.dataset.state, undefined);
assert.equal(reopened.state.drawerCloseTimer, null);
assert.equal(reopened.timeoutCleared(), true);
assert.equal(reopened.removedListener(), staleFinish);
staleFinish();
assert.equal(reopened.drawer.hidden, false,
  'A late close callback must never hide a rapidly reopened drawer');

assert.match(template, /addEventListener\("click", closeAccountDrawer\)/,
  'The visible close button uses the animated dismissal path');
assert.match(template, /if \(event\.target === drawer\) closeAccountDrawer\(\)/,
  'Backdrop clicks use the same animated dismissal path');
assert.match(template,
  /if \(event\.key === "Escape"\) \{ event\.preventDefault\(\); closeAccountDrawer\(\)/,
  'Escape uses the same animated dismissal path');
"""
        )


if __name__ == "__main__":
    unittest.main()
