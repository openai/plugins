"""Executable regression coverage for grounded leadership dashboard presentation."""

from __future__ import annotations

import unittest
from pathlib import Path

from sales_test_support import SalesTestCase

TEMPLATE = (
    Path(__file__).resolve().parent.parent / "assets" / "sales-leadership-dashboard.template.html"
)

NODE_PRELUDE = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n        \\}'
  ));
  assert.ok(match, 'The executable leadership helper ' + name + ' must exist');
  return match[1];
}

const hasNumber = value => value !== null && value !== undefined && value !== ''
  && Number.isFinite(Number(value));
const sourcedNumber = value => hasNumber(value) ? Number(value) : null;
const list = value => Array.isArray(value) ? value.filter(Boolean) : value ? [value] : [];
const money = value => hasNumber(value) ? '$' + Number(value).toLocaleString('en-US')
  : 'Unavailable';
const signedMoney = value => (Number(value) >= 0 ? '+' : '−') + money(Math.abs(value));
const escape = value => String(value ?? '');
const clamp = (value, minimum, maximum) => Math.min(Math.max(value, minimum), maximum);

function fakeElements() {
  const elements = new Map();
  return id => {
    if (!elements.has(id)) {
      elements.set(id, {
        dataset: {}, style: {}, hidden: false, textContent: '', innerHTML: '',
        setAttribute() {},
        querySelectorAll() { return []; }
      });
    }
    return elements.get(id);
  };
}

function forecastElements(forecast, fictionalFixture = false, scenario = {}, options = {}) {
  const $ = fakeElements();
  const components = options.components || [];
  const scenarios = options.scenarios || [];
  const renderForecast = new Function(
    'selectedScenario', 'projectedComponents', 'scenarioOptions', 'sourcedNumber', 'data',
    'clamp', '$', 'signedMoney', 'money', 'escape', 'renderScenarioControls', 'state', 'list',
    'accountRecords', 'fictionalFixture', 'hasNumber', bodyFor('renderForecast')
  );
  renderForecast(
    () => scenario, () => components, scenarios, sourcedNumber, {forecast}, clamp, $, signedMoney, money,
    escape, () => {}, {}, list, () => [], fictionalFixture, hasNumber
  );
  return $;
}
"""


class LeadershipDashboardTruthfulnessTests(SalesTestCase):
    def run_node(self, assertions: str) -> None:
        self.assert_node_script(NODE_PRELUDE + assertions, str(TEMPLATE))

    def test_account_row_ids_and_drawer_details_preserve_the_exact_opportunity(self) -> None:
        self.run_node(
            r"""
const accountRecords = new Function(
  'data', 'topDeals', 'decisionForAccount', 'list', 'priorityOrder', 'fictionalFixture',
  'hasNumber', bodyFor('accountRecords')
);
const deals = [
  {account: 'A B', value: 100, risk: 'First account'},
  {account: 'A-B', value: 200, risk: 'Second account'},
  {account: 'Same customer', opportunityId: 'opp-1', value: 300, risk: 'First opportunity'},
  {account: 'Same customer', opportunityId: 'opp-2', value: 400, risk: 'Second opportunity'}
];
const recordsFor = (payload, sourceDeals = deals) => accountRecords(
  payload, sourceDeals, () => ({}), list, {}, false, hasNumber
);
const records = recordsFor({});
assert.equal(new Set(records.map(row => row.id)).size, records.length);
assert.equal(records.find(row => row.id === records[1].id).value, 200);
assert.equal(records[2].id, 'opp-1');
assert.equal(records[3].id, 'opp-2');
assert.equal(recordsFor({}, [...deals].reverse()).find(row => row.value === 400).id, 'opp-2');
const supplied = recordsFor({accountOverview: [
  {id: 'same', name: 'One'}, {id: 'same', name: 'Two'},
  {id: 'same--2', name: 'Three'}, {name: 'Four'}, {id: 0, name: 'Five'}
]});
assert.equal(new Set(supplied.map(row => row.id)).size, supplied.length);
assert.equal(supplied[2].id, 'same--2', 'Do not steal a supplied source ID for a generated suffix');
assert.equal(supplied[4].id, '0');

const renderAccountDetail = new Function(
  'account', 'decisionForAccount', 'list', 'topDeals', 'executiveAttention',
  'fictionalFixture', '$', 'escape', 'money', 'listMarkup', bodyFor('renderAccountDetail')
);
function selectedDetails(account) {
  let observed;
  renderAccountDetail(account, () => ({}), list, deals,
    (_account, _decision, details) => { observed = details; return {context: '', label: ''}; },
    false, fakeElements(), escape, money, () => '');
  return observed;
}
assert.strictEqual(selectedDetails(records[3]), deals[3]);
assert.strictEqual(selectedDetails({name: 'Same customer', opportunityId: 'opp-2'}), deals[3]);
assert.deepEqual(selectedDetails({name: 'Same customer'}), {},
  'An account-level row must not select an arbitrary same-account opportunity');
"""
        )

    def test_tablet_metadata_wraps_and_interactive_controls_have_44px_touch_targets(
        self,
    ) -> None:
        self.run_node(
            r"""
assert.match(template,
  /@media \(max-width: 980px\)\s*\{[\s\S]*?\.report-meta\s*\{[^}]*min-width:\s*0;[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/,
  'Tablet reporting metadata must shrink instead of pushing the masthead past the viewport');
assert.match(template,
  /\.report-meta\s+\.meta-value\s*\{[^}]*white-space:\s*normal;[^}]*overflow-wrap:\s*anywhere;/,
  'Long reporting snapshots wrap within their tablet column');
assert.match(template,
  /\.scenario-tabs\s+button\s*\{[^}]*min-height:\s*44px;/,
  'Every forecast scenario remains easy to touch');
assert.match(template,
  /\.slider-info\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;[^}]*flex:\s*0\s+0\s+44px;/,
  'Compact visual help icons retain a 44px accessible hit target');
assert.match(template,
  /\.slider-info::before\s*\{[^}]*width:\s*18px;[^}]*height:\s*18px;/,
  'The visible help indicator stays visually compact inside its larger target');
assert.match(template,
  /input\[type="range"\]\s*\{[^}]*height:\s*44px;/,
  'Forecast assumption sliders remain usable by touch and keyboard');
assert.match(template,
  /\.drawer-close\s*\{[^}]*width:\s*44px;[^}]*height:\s*44px;/,
  'The account drawer has an accessible dismissal target');
assert.match(template,
  /\.account-drawer\[data-state="closing"\][\s\S]*?drawer-backdrop-out/,
  'The drawer backdrop remains visible during its exit transition');
assert.match(template,
  /\.account-drawer\[data-state="closing"\] \.account-drawer-panel[\s\S]*?drawer-slide-out/,
  'The drawer panel animates smoothly when dismissed');
assert.match(template,
  /prefers-reduced-motion:\s*reduce[\s\S]*?\.account-drawer,\s*\.account-drawer-panel\s*\{[^}]*animation:\s*none/,
  'People requesting reduced motion never receive a drawer animation');
assert.match(template,
  /\.slider-definition\s*\{[^}]*opacity:\s*0;[^}]*transform:\s*translateY\(4px\);[^}]*transition:\s*opacity\s+160ms\s+ease,\s*transform\s+180ms/,
  'Existing scenario-help popovers open and close with a restrained motion transition');
assert.match(template,
  /event\.key === "Escape" && document\.activeElement\?\.classList\.contains\("slider-info"\)/,
  'Focused forecast-help popovers can be dismissed with Escape');
"""
        )

    def test_real_account_priority_and_rank_require_grounded_evidence(self) -> None:
        self.run_node(
            r"""
const accountRecords = new Function(
  'data', 'topDeals', 'decisionForAccount', 'list', 'priorityOrder', 'fictionalFixture',
  'hasNumber', bodyFor('accountRecords')
);
function accounts(payload, fictionalFixture = false) {
  return accountRecords(
    payload, payload.topDeals || [], () => ({}), list,
    {High: 0, Action: 1, Watch: 2, Paused: 3}, fictionalFixture, hasNumber
  );
}

const unrankedDeals = Array.from({length: 10}, (_, index) => ({
  account: 'Grounded Customer ' + (index + 1), owner: 'Casey Rivera', value: 250000
}));
const realDeals = accounts({topDeals: unrankedDeals});
assert.deepEqual(realDeals.map(account => account.priority), Array(10).fill(null));
assert.deepEqual(realDeals.map(account => account.priorityRank), Array(10).fill(null));
assert.deepEqual(realDeals.map(account => account.name),
  unrankedDeals.map(deal => deal.account), 'Unknown priorities retain source ordering');

const directOverview = accounts({accountOverview: [
  {id: 'unknown', name: 'Unknown Priority', seller: 'Casey Rivera', value: 100000},
  {id: 'grounded', name: 'Grounded Priority', priority: 'Action', priorityRank: 4, value: 150000}
]});
assert.deepEqual(directOverview.map(account => [account.name, account.priority, account.priorityRank]),
  [['Grounded Priority', 'Action', 4], ['Unknown Priority', null, null]]);

const explicitUnavailable = accounts({accountOverview: [
  {id: 'literal', name: 'Literal unavailable', priority: 'Unavailable'}
]});
assert.equal(explicitUnavailable[0].priority, null,
  'An upstream missing-value label must never become a visible priority category');

const explicitDeal = accounts({topDeals: [{
  account: 'Actual Priority', priority: 'High', priorityRank: 7, value: 150000
}]})[0];
assert.equal(explicitDeal.priority, 'High');
assert.equal(explicitDeal.priorityRank, 7);

const fictionalDeals = accounts({topDeals: unrankedDeals}, true);
assert.deepEqual(fictionalDeals.map(account => account.priority),
  ['High', 'High', 'High', 'Action', 'Action', 'Watch', 'Watch', 'Watch', 'Paused', 'Paused']);
assert.deepEqual(fictionalDeals.map(account => account.priorityRank),
  Array.from({length: 10}, (_, index) => index + 1));

const renderAccountBriefing = new Function(
  'records', 'fictionalFixture', '$', 'money', 'escape', 'hasNumber',
  bodyFor('renderAccountBriefing')
);
const unsupportedElements = fakeElements();
renderAccountBriefing(realDeals, false, unsupportedElements, money, escape, hasNumber);
assert.equal(unsupportedElements('accountBriefing').hidden, true,
  'The entire unsourced priority briefing disappears');
assert.equal(unsupportedElements('account-briefing-copy').innerHTML, '');
assert.equal(unsupportedElements('account-evidence-count').hidden, true);
assert.equal(unsupportedElements('account-evidence-count').textContent, '');

const groundedWithoutRank = [{
  id: 'named', name: 'Named Priority', priority: 'High', priorityRank: null, value: 250000
}];
const groundedElements = fakeElements();
renderAccountBriefing(groundedWithoutRank, false, groundedElements, money, escape, hasNumber);
assert.equal(groundedElements('accountBriefing').hidden, false);
assert.doesNotMatch(groundedElements('account-briefing-copy').innerHTML, /ranks first/);
assert.doesNotMatch(groundedElements('account-briefing-copy').innerHTML,
  /customer context|Customer decision requires leadership support/);

const sourcedContext = [{
  ...groundedWithoutRank[0], briefing: 'Verified customer security review needs a named owner.'
}];
const sourcedElements = fakeElements();
renderAccountBriefing(sourcedContext, false, sourcedElements, money, escape, hasNumber);
assert.match(sourcedElements('account-briefing-copy').innerHTML,
  /customer context.*Verified customer security review needs a named owner/);

const fictionalElements = fakeElements();
renderAccountBriefing(fictionalDeals, true, fictionalElements, money, escape, hasNumber);
assert.match(fictionalElements('account-briefing-copy').innerHTML, /ranks first/);
assert.equal(fictionalElements('account-evidence-count').textContent, '10 prioritized accounts');

const renderAccountFocus = new Function(
  'accountRecords', 'state', 'renderAccountBriefing', '$', 'escape', 'money',
  'renderAccountDetail', 'openAccountDrawer', 'fictionalFixture', bodyFor('renderAccountFocus')
);
const focusElements = fakeElements();
renderAccountFocus(
  () => realDeals, {selectedAccount: '', drawerOpen: false}, () => {}, focusElements,
  escape, money, () => {}, () => {}, false
);
assert.equal(focusElements('account-priority-heading').hidden, true);
assert.equal(focusElements('account-list-root').dataset.priority, 'false');
assert.equal(focusElements('account-list-root').hidden, false);
assert.match(focusElements('accountFocusList').innerHTML, /Grounded Customer 1/);
assert.doesNotMatch(focusElements('accountFocusList').innerHTML,
  /account-priority|Unavailable|>High<|>Watch<|>Action</,
  'Unsupported priority cells disappear while grounded customer rows remain');

const explicitPriority = fakeElements();
renderAccountFocus(
  () => directOverview, {selectedAccount: '', drawerOpen: false}, () => {}, explicitPriority,
  escape, money, () => {}, () => {}, false
);
assert.equal(explicitPriority('account-priority-heading').hidden, false);
assert.equal(explicitPriority('account-list-root').dataset.priority, 'true');
assert.match(explicitPriority('accountFocusList').innerHTML, />Action<\/span>/);
assert.doesNotMatch(explicitPriority('accountFocusList').innerHTML, /Unavailable/);
"""
        )

    def test_grounded_account_search_filters_resets_and_never_invents_rows(self) -> None:
        self.run_node(
            r"""
assert.match(template, /id="account-focus-search"[^>]*type="search"/);
assert.match(template, /aria-label="Search verified accounts"/);
assert.match(template, /aria-controls="accountFocusList"/);
assert.match(template, /id="account-focus-search-clear"[^>]*type="button"/);
const renderAccountFocus = new Function(
  'accountRecords', 'state', 'renderAccountBriefing', '$', 'escape', 'money',
  'renderAccountDetail', 'openAccountDrawer', 'fictionalFixture', bodyFor('renderAccountFocus')
);
const grounded = [
  {id: 'harbor', name: 'Harbor Health', seller: 'Real Seller', value: 125000},
  {id: 'cedar', name: 'Cedar Energy', seller: 'Real Seller', value: 90000}
];
const state = {selectedAccount: '', drawerOpen: false, accountQuery: 'harbor'};
const elements = fakeElements();
const render = records => renderAccountFocus(
  () => records, state, () => {}, elements, escape, money, () => {}, () => {}, false
);
render(grounded);
assert.match(elements('accountFocusList').innerHTML, /Harbor Health/);
assert.doesNotMatch(elements('accountFocusList').innerHTML, /Cedar Energy/);
assert.equal(elements('account-focus-search-wrap').hidden, false);
assert.equal(elements('account-focus-search-clear').hidden, false);

state.accountQuery = 'not a real customer';
render(grounded);
assert.match(elements('accountFocusList').innerHTML, /No verified accounts match/);
assert.doesNotMatch(elements('accountFocusList').innerHTML, /Harbor Health|Cedar Energy/);
assert.equal(elements('account-list-root').hidden, false);

state.accountQuery = '';
render(grounded);
assert.match(elements('accountFocusList').innerHTML, /Harbor Health/);
assert.match(elements('accountFocusList').innerHTML, /Cedar Energy/);
assert.equal(elements('account-focus-search-clear').hidden, true);

render([]);
assert.equal(elements('account-focus-search-wrap').hidden, true);
assert.equal(elements('account-list-root').hidden, true);
assert.doesNotMatch(elements('accountFocusList').innerHTML, /Harbor Health|Cedar Energy/);
"""
        )

    def test_priority_briefings_sum_only_known_opportunities_and_keep_verified_zero(
        self,
    ) -> None:
        self.run_node(
            r"""
const renderAccountBriefing = new Function(
  'records', 'fictionalFixture', '$', 'money', 'escape', 'hasNumber',
  bodyFor('renderAccountBriefing')
);
const renderMetrics = new Function(
  'list', 'data', '$', 'escape', 'sourcedNumber', 'accountRecords', 'money',
  'accountSignals', 'connectedSources', bodyFor('renderMetrics')
);

function briefing(records) {
  const $ = fakeElements();
  renderAccountBriefing(records, false, $, money, escape, hasNumber);
  renderMetrics(list, {
    company: {divisionLead: {name: 'Priya Desai'}}, forecast: {}, metrics: []
  }, $, escape, sourcedNumber, () => records, money, [], () => []);
  return {
    account: $('account-briefing-copy').innerHTML,
    forecast: $('forecast-briefing-copy').innerHTML
  };
}

for (const missing of [
  [{name: 'Unknown high', priority: 'High'}],
  [{name: 'Unavailable high', priority: 'High', value: 'Value unavailable'}],
  [{name: 'Invalid high', priority: 'High', value: Number.NaN}],
  [{name: 'Action only', priority: 'Action', value: 45000}]
]) {
  const result = briefing(missing);
  assert.doesNotMatch(result.account,
    /highest-priority opportunities total|\$0|across known opportunities/,
    'An unknown or nonexistent High opportunity cannot become a fabricated zero total');
  assert.doesNotMatch(result.forecast,
    /represents? \$0|near-term opportunity|across known opportunities/,
    'The forecast briefing omits unsupported High-opportunity finance');
}

const partial = briefing([
  {name: 'Known high', priority: 'High', value: 45000},
  {name: 'Unknown high', priority: 'High'}
]);
assert.match(partial.account, /\$45,000 across known opportunities/);
assert.match(partial.forecast, /\$45,000 across known opportunities/);

const zero = briefing([{name: 'Verified zero', priority: 'High', value: 0}]);
assert.match(zero.account, /highest-priority opportunities total \$0/);
assert.match(zero.forecast, /represents \$0 in near-term opportunity/);
assert.doesNotMatch(zero.account + zero.forecast, /across known opportunities/,
  'A verified complete zero remains complete, not partial');

const complete = briefing([
  {name: 'First high', priority: 'High', value: 45000},
  {name: 'Second high', priority: 'High', value: 5000}
]);
assert.match(complete.account, /\$50,000/);
assert.match(complete.forecast, /\$50,000 in near-term opportunity/);
assert.doesNotMatch(complete.account + complete.forecast, /across known opportunities/);
"""
        )

    def test_real_account_drawer_omits_unsourced_customer_decisions_and_actions(
        self,
    ) -> None:
        self.run_node(
            r"""
const executiveAttention = new Function(
  'account', 'decision', 'details', 'list', 'fictionalFixture', bodyFor('executiveAttention')
);
const listMarkup = new Function('values', 'fallback', 'list', 'escape', bodyFor('listMarkup'));
const renderAccountDetail = new Function(
  'account', 'decisionForAccount', 'list', 'topDeals', 'executiveAttention',
  'fictionalFixture', '$', 'escape', 'money', 'listMarkup', bodyFor('renderAccountDetail')
);

function accountDetail(account, fictionalFixture = false, decision = {}) {
  const $ = fakeElements();
  renderAccountDetail(
    account, () => decision, list,
    [{account: account.name, owner: account.seller, stage: account.stage}],
    (item, currentDecision, details) => executiveAttention(
      item, currentDecision, details, list, fictionalFixture
    ),
    fictionalFixture, $, escape, money,
    (values, fallback) => listMarkup(values, fallback, list, escape)
  );
  return $('accountFocusDetail').innerHTML;
}

const minimal = {
  id: 'harbor', name: 'Harbor Health', seller: 'Casey Rivera', stage: 'Open',
  value: 0, priority: null
};
const grounded = accountDetail(minimal);
assert.match(grounded, /Harbor Health/);
assert.match(grounded, /\$0/);
assert.doesNotMatch(grounded,
  /buyer decision|accountable owner|customer blocker|leadership attention|Recommended executive action|Priority Rationale|What to monitor|Seller’s next step/i,
  'Unreported account actions, decisions, and entire empty detail blocks must disappear');
assert.doesNotMatch(grounded, /Priority account/,
  'An unranked account must not be described as a priority account');
assert.doesNotMatch(grounded, /Unavailable|under review|to confirm/i,
  'Unsupported priority, timing, and stage placeholders are omitted');

assert.doesNotMatch(accountDetail({...minimal, priority: 'Unavailable'}), /Unavailable/i,
  'Literal missing-value priority input cannot leak into account details');

const sourced = accountDetail({
  ...minimal,
  priority: 'High',
  briefing: 'Customer reported a security-review ownership gap.',
  monitor: ['Security owner is not yet confirmed.'],
  nextStep: 'Ask Casey to validate the customer security owner.'
});
assert.match(sourced, /Customer reported a security-review ownership gap/);
assert.match(sourced, /Ask Casey to validate the customer security owner/);
assert.match(sourced, /Priority Rationale|What to monitor|Seller’s next step/);

const fictional = accountDetail({...minimal, priority: 'High'}, true);
assert.match(fictional, /Review the current buyer decision and accountable owner/);
assert.match(fictional, /Confirm the accountable owner and the customer blocker/);
assert.match(fictional, /Track the customer decision/);
assert.match(fictional, /Confirm the customer owner and document the next reviewed milestone/);
"""
        )

    def test_real_team_rows_and_drawers_require_sourced_titles_targets_and_actions(
        self,
    ) -> None:
        self.run_node(
            r"""
const performanceAttainment = new Function('person', bodyFor('performanceAttainment'));
const performanceStatus = new Function('attainment', bodyFor('performanceStatus'));
const growthLabel = new Function('team', bodyFor('growthLabel'));
const listMarkup = new Function('values', 'fallback', 'list', 'escape', bodyFor('listMarkup'));
const performanceRow = new Function(
  'person', 'kind', 'performanceAttainment', 'performanceStatus', 'fictionalFixture',
  'escape', 'money', 'hasNumber', 'growthLabel', bodyFor('performanceRow')
);
const renderPerformanceDetail = new Function(
  'person', 'kind', 'performanceAttainment', 'performanceStatus', 'fictionalFixture',
  'list', 'growthLabel', 'escape', 'hasNumber', 'money', 'listMarkup', '$',
  bodyFor('renderPerformanceDetail')
);
const fallbackTeamFocus = new Function(
  'divisionTeams', 'performanceAttainment', 'data', 'list', bodyFor('fallbackTeamFocus')
);

function row(person, kind, fictionalFixture = false) {
  return performanceRow(
    person, kind, performanceAttainment, performanceStatus, fictionalFixture,
    escape, money, hasNumber, growthLabel
  );
}

function details(person, kind, fictionalFixture = false) {
  const $ = fakeElements();
  renderPerformanceDetail(
    person, kind, performanceAttainment, performanceStatus, fictionalFixture,
    list, growthLabel, escape, hasNumber, money,
    (values, fallback) => listMarkup(values, fallback, list, escape), $
  );
  return $('accountFocusDetail').innerHTML;
}

const manager = {
  name: 'Morgan Lee', region: 'Enterprise Revenue', forecast: 0, target: 200000,
  accountCount: 1
};
const seller = {name: 'Casey Rivera', manager: 'Morgan Lee', forecast: 0, accountCount: 1};
const managerMarkup = row(manager, 'manager');
assert.match(managerMarkup, /Morgan Lee/);
assert.match(managerMarkup, /\$0/);
assert.match(managerMarkup, /of \$200,000/);
assert.match(managerMarkup, />1<\/td>/,
  'The verified accountCount alias remains visible in manager rows');
assert.doesNotMatch(managerMarkup, /Regional Sales Manager|performance-growth/,
  'Unsourced titles and growth widgets must disappear');

const sellerMarkup = row(seller, 'seller');
assert.match(sellerMarkup, /Casey Rivera/);
assert.match(sellerMarkup, /\$0/);
assert.match(sellerMarkup, />1<\/td>/,
  'The verified accountCount alias remains visible in seller rows');
assert.doesNotMatch(sellerMarkup,
  /Account Executive|of Unavailable|performance-status|>Unavailable</,
  'Unsourced roles, targets, attainment, and performance-status widgets must disappear');

const zeroAccounts = row({...seller, accountCount: 0}, 'seller');
assert.match(zeroAccounts, />0<\/td>/,
  'A verified zero account count must not become unavailable');

const namedRole = row({...seller, role: 'Enterprise Renewal Specialist', target: 0}, 'seller');
assert.match(namedRole, /Enterprise Renewal Specialist/);
assert.match(namedRole, /of \$0/,
  'A verified zero target remains visible without inventing attainment');

const managerDetail = details(manager, 'manager');
assert.match(managerDetail, /Forecast.*\$0/);
assert.match(managerDetail, /Target.*\$200,000/);
assert.match(managerDetail, /Accounts.*1/);
assert.doesNotMatch(managerDetail,
  /Regional Sales Manager|Weekly growth|Needs attention|highest-priority customer blocker/,
  'Manager drawer omits unsupported titles, movement, and customer intervention claims');

const sellerDetail = details(seller, 'seller');
assert.match(sellerDetail, /Forecast.*\$0/);
assert.match(sellerDetail, /Accounts.*1/);
assert.doesNotMatch(sellerDetail,
  /Account executive|Target|Attainment|Unavailable|Needs attention|highest-priority customer blocker/i,
  'Seller drawer omits unsupported titles, targets, attainment, and coaching sections');

const team = {manager: 'Morgan Lee', accountCount: 0, forecast: 0, target: 1000};
const actualTeam = fallbackTeamFocus([team], performanceAttainment, {sellerOverview: []}, list)[0];
assert.equal(actualTeam.role, '');
assert.deepEqual(actualTeam.attention, []);
assert.equal(actualTeam.accounts, 0);

const sourcedTeam = fallbackTeamFocus(
  [{...team, role: 'Enterprise Sales Director', attention: ['Verified customer renewal review.']}],
  performanceAttainment, {sellerOverview: []}, list
)[0];
assert.equal(sourcedTeam.role, 'Enterprise Sales Director');
assert.deepEqual(sourcedTeam.attention, ['Verified customer renewal review.']);

const fictionalTeam = fallbackTeamFocus(
  [team], performanceAttainment, {sellerOverview: [], disclosure: {isFictional: true}}, list
)[0];
assert.equal(fictionalTeam.role, 'Regional Sales Manager');
assert.deepEqual(fictionalTeam.attention,
  ['Review current customer blockers with the accountable seller.']);
assert.match(row(seller, 'seller', true), /Account Executive/,
  'The canonical fictional seller row preserves its existing presentation');
assert.match(details(seller, 'seller', true),
  /Confirm ownership of the highest-priority customer blocker/,
  'The fictional performance drawer preserves its demonstration fallback');
"""
        )

    def test_real_performance_tables_omit_entire_unsupported_columns(self) -> None:
        self.run_node(
            r"""
const performanceAttainment = new Function('person', bodyFor('performanceAttainment'));
const growthLabel = new Function('team', bodyFor('growthLabel'));
const applyPerformanceColumns = new Function(
  'container', 'people', 'kind', 'fictionalFixture', 'hasNumber',
  'performanceAttainment', 'growthLabel', bodyFor('applyPerformanceColumns')
);

function renderedColumns(people, kind, fictionalFixture = false) {
  const labels = kind === 'manager'
    ? ['Manager', 'Region', 'Forecast / Target', 'Attainment', 'Weekly growth', 'Accounts', 'Status']
    : ['Seller', 'Region', 'Manager', 'Forecast / Target', 'Attainment', 'Accounts', 'Status'];
  const headers = labels.map(label => ({hidden: false, textContent: label}));
  const rows = people.map(() => ({children: labels.map(() => ({hidden: false}))}));
  const table = {
    dataset: {}, style: {},
    querySelectorAll(selector) { return selector === 'thead th' ? headers : []; }
  };
  const container = {
    closest(selector) { return selector === 'table' ? table : null; },
    querySelectorAll(selector) { return selector === 'tr' ? rows : []; }
  };
  applyPerformanceColumns(
    container, people, kind, fictionalFixture, hasNumber, performanceAttainment, growthLabel
  );
  return {headers, rows, table, visible: headers.filter(header => !header.hidden)
    .map(header => header.textContent)};
}

const sparseManager = renderedColumns([
  {name: 'Morgan Lee', forecast: 0, accountCount: 0}
], 'manager');
assert.deepEqual(sparseManager.visible, ['Manager', 'Forecast', 'Accounts'],
  'Missing region, target, attainment, weekly growth, and status columns disappear');
assert.equal(sparseManager.table.dataset.visibleColumns, '3');
assert.equal(sparseManager.table.style.minWidth, '0');
assert.deepEqual(sparseManager.rows[0].children.map(cell => cell.hidden),
  [false, true, false, true, true, false, true]);

const sparseSeller = renderedColumns([
  {name: 'Casey Rivera', manager: 'Morgan Lee', forecast: 0, accountCount: 0}
], 'seller');
assert.deepEqual(sparseSeller.visible, ['Seller', 'Manager', 'Forecast', 'Accounts'],
  'Verified zero forecast/account counts remain visible without invented seller metrics');

const completeManager = renderedColumns([
  {name: 'Morgan Lee', forecast: 0, target: 200000, accountCount: 1}
], 'manager');
assert.deepEqual(completeManager.visible,
  ['Manager', 'Forecast / Target', 'Attainment', 'Accounts', 'Status'],
  'Sourced targets and derived zero-percent attainment remain visible');

const fictional = renderedColumns([{name: 'Morgan Lee'}], 'manager', true);
assert.equal(fictional.visible.length, 7,
  'The canonical fictional demonstration retains its existing complete table');
"""
        )

    def test_drawer_dismissal_animates_restores_focus_and_honors_reduced_motion(
        self,
    ) -> None:
        self.run_node(
            r"""
const closeAccountDrawer = new Function(
  'state', '$', 'document', 'window', 'renderAccountFocus', bodyFor('closeAccountDrawer')
);
const beginDrawerOpening = new Function(
  'state', '$', 'document', 'window', bodyFor('beginDrawerOpening')
);

function harness(reducedMotion = false, options = {}) {
  let listener;
  let removedListener;
  let removedBodyLock = false;
  let restoredFocus = false;
  let timeoutCleared = false;
  const panel = {
    addEventListener(name, callback) { listener = callback; },
    removeEventListener(name, callback) { removedListener = callback; }
  };
  const drawer = {
    hidden: false, dataset: {},
    querySelector(selector) { return selector === '.account-drawer-panel' ? panel : null; },
    querySelectorAll() { return []; }
  };
  const previousFocus = {
    isConnected: options.previousConnected !== false,
    focus() { restoredFocus = 'previous'; }
  };
  const selectedAccount = {
    dataset: {accountId: options.accountId || ''},
    focus() { restoredFocus = 'account'; }
  };
  const closeButton = {focus() {}};
  const detail = {scrollTop: 4};
  const title = {textContent: ''};
  const listRoot = {
    querySelectorAll() { return options.includeSelected ? [selectedAccount] : []; }
  };
  const elements = {
    'account-drawer': drawer,
    'account-drawer-close': closeButton,
    'accountFocusDetail': detail,
    'account-drawer-title': title,
    'accountFocusList': listRoot
  };
  const state = {
    drawerOpen: true, drawerCloseTimer: null, drawerCloseListener: null,
    returnFocus: previousFocus, returnAccount: options.accountId || ''
  };
  const document = {
    body: {classList: {
      add() {},
      remove() { removedBodyLock = true; }
    }},
    querySelectorAll() { return []; }
  };
  const window = {
    matchMedia() { return {matches: reducedMotion}; },
    setTimeout() { return 17; },
    clearTimeout() { timeoutCleared = true; }
  };
  const $ = id => elements[id];
  return {state, $, document, window, drawer, panel,
    finish() { assert.ok(listener); listener(); },
    restored() { return Boolean(restoredFocus); },
    restoredKind() { return restoredFocus; },
    unlocked() { return removedBodyLock; },
    removed() { return removedListener; },
    timeoutCleared() { return timeoutCleared; }};
}

const animated = harness();
closeAccountDrawer(animated.state, animated.$, animated.document, animated.window, () => {});
assert.equal(animated.drawer.hidden, false,
  'The drawer stays mounted throughout its exit animation');
assert.equal(animated.drawer.dataset.state, 'closing');
assert.equal(animated.state.drawerCloseTimer, 17);
assert.equal(animated.restored(), false);
animated.finish();
assert.equal(animated.drawer.hidden, true);
assert.equal(animated.drawer.dataset.state, undefined);
assert.equal(animated.state.drawerCloseTimer, null);
assert.equal(animated.restored(), true, 'Focus returns to the originating control');
assert.equal(animated.unlocked(), true, 'Body scrolling resumes after dismissal');

const reduced = harness(true);
closeAccountDrawer(reduced.state, reduced.$, reduced.document, reduced.window, () => {});
assert.equal(reduced.drawer.hidden, true,
  'Reduced-motion dismissal is immediate without an asynchronous transition');
assert.equal(reduced.state.drawerCloseTimer, null);
assert.equal(reduced.restored(), true);

const reopened = harness();
closeAccountDrawer(reopened.state, reopened.$, reopened.document, reopened.window, () => {});
reopened.state.drawerOpen = true;
beginDrawerOpening(reopened.state, reopened.$, reopened.document, reopened.window);
assert.equal(reopened.drawer.hidden, false);
assert.equal(reopened.drawer.dataset.state, undefined);
assert.equal(reopened.state.drawerCloseTimer, null);
assert.ok(reopened.removed(), 'A stale completion listener is removed when reopening');
assert.equal(reopened.timeoutCleared(), true);

const teamOpener = harness(false, {accountId: 'stale-account', includeSelected: true});
closeAccountDrawer(teamOpener.state, teamOpener.$, teamOpener.document,
  teamOpener.window, () => {});
teamOpener.finish();
assert.equal(teamOpener.restoredKind(), 'previous',
  'A connected team-row opener wins over an unrelated previously selected account');

const rerenderedAccount = harness(false, {
  accountId: 'refreshed-account', includeSelected: true, previousConnected: false
});
closeAccountDrawer(rerenderedAccount.state, rerenderedAccount.$,
  rerenderedAccount.document, rerenderedAccount.window, () => {});
rerenderedAccount.finish();
assert.equal(rerenderedAccount.restoredKind(), 'account',
  'A rerendered account opener restores focus to the replacement account row');
"""
        )

    def test_forecast_recovery_requires_positive_shortfall_and_is_capped(self) -> None:
        self.run_node(
            r"""
function implication(forecast, fictional = false) {
  return forecastElements(forecast, fictional)('weekly-implication').innerHTML;
}

assert.match(implication({base: 900000, target: 1000000, weeklyMovement: 50000}),
  /33% of the previous forecast gap was recovered this week/);
assert.match(implication({base: 1100000, target: 1000000, weeklyMovement: 200000}),
  /100% of the previous forecast gap was recovered this week/);

for (const alreadyAbove of [
  {base: 1100000, target: 1000000, weeklyMovement: 50000},
  {base: 1050000, target: 1000000, weeklyMovement: 50000},
  {base: 900000, target: 1000000, weeklyMovement: -200000}
]) {
  const message = implication(alreadyAbove);
  assert.match(message, /prior forecast was already at or above target/);
  assert.doesNotMatch(message, /\d+%.*recovered/);
}

const declining = implication({base: 850000, target: 1000000, weeklyMovement: -50000});
assert.match(declining, /forecast declined.*previous shortfall increased/);
assert.doesNotMatch(declining, /-\d+%|−\d+%|recovered this week/);

const unchanged = implication({base: 900000, target: 1000000, weeklyMovement: 0});
assert.match(unchanged, /forecast was unchanged/);
assert.doesNotMatch(unchanged, /\d+%.*recovered/);

const noMovement = forecastElements({base: 900000, target: 1000000});
assert.equal(noMovement('weekly-implication').innerHTML, '');
assert.equal(noMovement('weekly-implication').hidden, true);
assert.equal(noMovement('weekly-panel').hidden, true,
  'Missing weekly comparisons remove the entire movement card');
assert.match(implication({base: 13520000, target: 14000000, weeklyMovement: 440000}, true),
  /48% of the previous forecast gap was recovered this week/,
  'The canonical fictional leadership demo keeps its existing sourced copy');
"""
        )

    def test_real_forecast_confidence_preserves_exact_sourced_percentages(self) -> None:
        self.run_node(
            r"""
function confidenceMarkup(value, fictional = false, scenario = {}) {
  const $ = forecastElements({base: 900000, target: 1000000, confidence: value}, fictional, scenario);
  return $('forecast-summary').innerHTML;
}

for (const confidence of [0, 10, 25, 81, 98, 100]) {
  assert.match(confidenceMarkup(confidence), new RegExp('>' + confidence + '%</div>'),
    'Real sourced confidence must display exactly as supplied');
}
assert.match(confidenceMarkup(81, false, {confidence: 0}), />0%<\/div>/,
  'A sourced scenario confidence of zero overrides forecast confidence without clamping');
assert.match(confidenceMarkup(81, false, {confidence: 100}), />100%<\/div>/);
assert.match(confidenceMarkup(0, true), />25%<\/div>/,
  'The fictional demonstration keeps its existing presentation range');
assert.match(confidenceMarkup(100, true), />98%<\/div>/);
"""
        )

    def test_unsourced_optional_forecast_blocks_disappear_without_layout_gaps(
        self,
    ) -> None:
        self.run_node(
            r"""
assert.match(template, /\[hidden\]\s*\{[^}]*display:\s*none\s*!important/,
  'Explicit hidden CSS must override forecast grid and weekly-card flex declarations');
assert.match(template,
  /\.forecast-layout\[data-panel-count="1"\]\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/,
  'A supported forecast expands across the layout after the unsupported weekly panel disappears');

const missing = forecastElements({});
for (const id of [
  'forecast-subheading', 'forecast-layout', 'forecast-panel', 'weekly-panel', 'forecast-header',
  'forecast-total', 'forecast-position', 'forecast-summary', 'forecast-context', 'scenario-tabs',
  'scenario-studio', 'stacked-wrap', 'weekly-total', 'weekly-badge', 'bar-chart',
  'weekly-implication'
]) {
  assert.equal(missing(id).hidden, true, id + ' must disappear without sourced data');
}
assert.equal(missing('forecast-layout').dataset.panelCount, '0');
assert.equal(missing('forecast-summary').innerHTML, '');
assert.equal(missing('weekly-implication').innerHTML, '');
assert.doesNotMatch(missing('forecast-summary').innerHTML,
  /Gap to plan|Modeled confidence|Attainment path|Unavailable/);

const grounded = forecastElements({base: 125000}, false, {}, {
  components: [{key: 'closedWon', label: 'Closed won', adjusted: 125000}]
});
assert.equal(grounded('forecast-layout').hidden, false);
assert.equal(grounded('forecast-layout').dataset.panelCount, '1');
assert.equal(grounded('forecast-panel').hidden, false);
assert.equal(grounded('forecast-total').textContent, '$125,000');
assert.equal(grounded('weekly-panel').hidden, true);
assert.equal(grounded('forecast-position').hidden, true);
assert.equal(grounded('forecast-summary').hidden, true);
assert.equal(grounded('forecast-eyebrow').hidden, true,
  'An unsupported scenario planner must not leave its heading visible');
assert.equal(grounded('forecast-heading').textContent, 'Quarter-end forecast');
assert.equal(grounded('stacked-wrap').hidden, false);
assert.match(grounded('stacked-legend').innerHTML, /Closed won/,
  'A verified closed-won revenue component remains visible without a sourced target');
assert.equal(grounded('target-marker').hidden, true);
assert.equal(grounded('target-label').hidden, true);
"""
        )

    def test_forecast_summary_only_renders_supported_metrics_and_preserves_verified_zeroes(
        self,
    ) -> None:
        self.run_node(
            r"""
const confidenceOnly = forecastElements({base: 0, confidence: 0});
assert.equal(confidenceOnly('forecast-total').textContent, '$0');
assert.equal(confidenceOnly('forecast-total').hidden, false);
assert.equal(confidenceOnly('forecast-summary').hidden, false);
assert.equal(confidenceOnly('forecast-summary').dataset.metricCount, '1');
assert.match(confidenceOnly('forecast-summary').innerHTML, /Modeled confidence/);
assert.match(confidenceOnly('forecast-summary').innerHTML, />0%<\/div>/);
assert.doesNotMatch(confidenceOnly('forecast-summary').innerHTML,
  /Gap to|Attainment path|Unavailable/);

const gapAndAttainment = forecastElements({base: 0, target: 1000});
assert.equal(gapAndAttainment('forecast-summary').dataset.metricCount, '2');
assert.match(gapAndAttainment('forecast-summary').innerHTML, /Gap to \$1,000 plan/);
assert.match(gapAndAttainment('forecast-summary').innerHTML, />0% of plan<\/div>/);
assert.doesNotMatch(gapAndAttainment('forecast-summary').innerHTML, /Modeled confidence/);
assert.equal(gapAndAttainment('stacked-wrap').hidden, true);
assert.equal(gapAndAttainment('target-marker').hidden, true,
  'A sourced target must not leave an orphan marker when there is no component chart');
assert.equal(gapAndAttainment('target-label').hidden, true);

const exactlyOnPlan = forecastElements({base: 1000, target: 1000, confidence: 0});
assert.equal(exactlyOnPlan('forecast-summary').dataset.metricCount, '3');
assert.match(exactlyOnPlan('forecast-summary').innerHTML, />\$0<\/div>/,
  'A verified zero gap is displayed, not mistaken for missing data');
assert.match(exactlyOnPlan('forecast-summary').innerHTML, />0%<\/div>/,
  'Verified zero confidence is displayed without inventing a benchmark');
assert.match(exactlyOnPlan('forecast-summary').innerHTML, />100% of plan<\/div>/);
assert.equal(exactlyOnPlan('forecast-position').hidden, false);
"""
        )

    def test_forecast_movement_reconciles_same_basis_snapshots_across_visible_surfaces(
        self,
    ) -> None:
        self.run_node(
            r"""
const renderMetrics = new Function(
  'list', 'data', '$', 'escape', 'sourcedNumber', 'accountRecords', 'money',
  'accountSignals', 'connectedSources', bodyFor('renderMetrics')
);
function metricMarkup(forecast, delta = '−$150K since Jul 31 history snapshot') {
  const $ = fakeElements();
  renderMetrics(list, {
    company: {divisionLead: {name: 'Verified Sales Leader'}},
    forecast,
    metrics: [{key: 'forecast', label: 'Probability-weighted forecast',
      display: '$8,648,750', delta}]
  }, $, escape, sourcedNumber, () => [], money, [], () => []);
  return $('kpi-strip').innerHTML;
}

const weighted = {base: 8648750, weeklyMovement: -150000, weekly: [
  {short: 'Jul 31', value: 8776250}, {short: 'Aug 7', value: 8648750}
]};
const corrected = forecastElements(weighted);
assert.equal(corrected('weekly-total').textContent, '−$127.5K');
assert.match(corrected('forecast-context').innerHTML, /−\$127\.5K/);
assert.match(corrected('weekly-implication').innerHTML, /\$127\.5K/);
assert.doesNotMatch(corrected('weekly-total').textContent, /150,000/);
assert.match(metricMarkup(weighted), /−\$127\.5K since Jul 31 history snapshot/);
assert.doesNotMatch(metricMarkup(weighted), /150K|150,000/);

const consistent = {base: 10175000, weeklyMovement: -150000, weekly: [
  {short: 'Previous', value: 10325000}, {short: 'Current', value: 10175000}
]};
assert.equal(forecastElements(consistent)('weekly-total').textContent, '−$150,000');
assert.match(metricMarkup(consistent), /−\$150,000 since Jul 31 history snapshot/);

const zero = {base: 8648750, weeklyMovement: 0, weekly: [
  {short: 'Previous', value: 8648750}, {short: 'Current', value: 8648750}
]};
assert.equal(forecastElements(zero)('weekly-total').textContent, '+$0');
assert.match(metricMarkup(zero, '+$0 since verified snapshot'), /\+\$0 since verified snapshot/);

const missing = {base: 8648750, weekly: weighted.weekly};
assert.equal(forecastElements(missing)('weekly-total').hidden, true,
  'Historical snapshots alone must not invent a movement claim');

const mismatched = {...weighted, base: 8648700};
const unsafe = forecastElements(mismatched);
assert.equal(unsafe('weekly-total').hidden, true,
  'A current forecast on a different basis cannot support a movement KPI');
assert.equal(unsafe('forecast-context').hidden, true);
assert.doesNotMatch(metricMarkup(mismatched), /metric-delta|150K|127,500/,
  'An unreconciled weighted KPI delta must disappear rather than inventing evidence');

const incomplete = {...weighted, weekly: [weighted.weekly[0], {short: 'Current'}]};
assert.equal(forecastElements(incomplete)('weekly-total').hidden, true);
assert.doesNotMatch(metricMarkup(incomplete), /metric-delta|150K/);

const one = {...weighted, weekly: [weighted.weekly[1]]};
assert.equal(forecastElements(one)('weekly-total').textContent, '−$150,000',
  'One snapshot must preserve an independently sourced movement without fabricating history');
assert.match(metricMarkup(one), /−\$150K since Jul 31 history snapshot/);
"""
        )

    def test_weekly_panels_require_verified_history_or_movement_and_keep_zeroes(
        self,
    ) -> None:
        self.run_node(
            r"""
const noComparison = forecastElements({base: 900000, weekly: [{short: 'Now', value: 900000}]});
assert.equal(noComparison('weekly-panel').hidden, true,
  'One snapshot without a sourced change does not support a weekly comparison');
assert.equal(noComparison('forecast-context').hidden, true);
assert.equal(noComparison('weekly-implication').hidden, true);

const historyOnly = forecastElements({base: 900000, weekly: [
  {short: 'Last week', value: 0}, {short: 'Now', value: 900000}
]});
assert.equal(historyOnly('weekly-panel').hidden, false);
assert.equal(historyOnly('weekly-heading').textContent, 'Forecast history');
assert.equal(historyOnly('bar-chart').hidden, false);
assert.match(historyOnly('bar-chart').innerHTML, /\$0/,
  'A sourced zero-valued historical snapshot remains visible');
assert.equal(historyOnly('weekly-total').hidden, true);
assert.equal(historyOnly('weekly-badge').hidden, true);
assert.equal(historyOnly('forecast-context').hidden, true);
assert.equal(historyOnly('weekly-implication').hidden, true);

const unchanged = forecastElements({base: 0, weeklyMovement: 0});
assert.equal(unchanged('weekly-panel').hidden, false);
assert.equal(unchanged('weekly-panel').dataset.hasHistory, 'false');
assert.equal(unchanged('bar-chart').hidden, true,
  'A sourced change without history must not reserve an empty chart');
assert.equal(unchanged('weekly-total').hidden, false);
assert.equal(unchanged('weekly-total').textContent, '+$0');
assert.equal(unchanged('weekly-badge').hidden, false);
assert.equal(unchanged('weekly-badge').textContent, 'Unchanged');
assert.equal(unchanged('weekly-implication').hidden, false);
assert.match(unchanged('weekly-implication').innerHTML, /unchanged this week/);
assert.doesNotMatch(unchanged('weekly-implication').innerHTML, /unavailable|missing/i);

const singleSnapshot = forecastElements({base: 900000, weeklyMovement: 5000, weekly: [
  {short: 'Now', value: 900000}
]});
assert.equal(singleSnapshot('weekly-panel').hidden, false,
  'Explicit sourced movement supports the card without a comparable history');
assert.equal(singleSnapshot('weekly-panel').dataset.hasHistory, 'false');
assert.equal(singleSnapshot('bar-chart').hidden, true,
  'One snapshot must not create a tall, misleading comparison chart');
assert.equal(singleSnapshot('bar-chart').innerHTML, '');
"""
        )

    def test_supported_kpis_remain_visible_while_unsourced_cards_and_fields_disappear(
        self,
    ) -> None:
        self.run_node(
            r"""
const renderMetrics = new Function(
  'list', 'data', '$', 'escape', 'sourcedNumber', 'accountRecords', 'money',
  'accountSignals', 'connectedSources', bodyFor('renderMetrics')
);
const sourceBacked = {
  company: {divisionLead: {name: 'Priya Desai'}},
  forecast: {base: 0},
  metrics: [
    {
      key: 'forecast', label: 'Current revenue', display: '$0', value: 0,
      benchmark: '—', delta: 'No data available'
    },
    {key: 'confidence', label: 'Forecast confidence', display: 'N/A'},
    {key: 'coverage', label: 'Pipeline coverage', display: '0×', value: 0},
    {key: 'pipelineCreated', label: 'Pipeline created', display: 'Not connected'},
    {key: 'closedWon', label: 'Closed-won ARR', display: '$250,000', value: 250000},
    {key: 'revenue', label: 'Booked revenue', display: '$125,000', value: 125000}
  ]
};
const visible = fakeElements();
renderMetrics(list, sourceBacked, visible, escape, sourcedNumber, () => [], money, [], () => []);
const markup = visible('kpi-strip').innerHTML;
assert.equal(visible('kpi-strip').hidden, false);
for (const supported of ['Current revenue', '$0', 'Pipeline coverage', '0×', 'Closed-won ARR'])
  assert.ok(markup.includes(supported), supported + ' should remain visible');
assert.doesNotMatch(markup, /Forecast confidence|Unavailable|metric-benchmark|metric-delta/,
  'Unsourced whole cards and unsupported per-card benchmark or movement fields disappear');

const missing = fakeElements();
renderMetrics(list, {...sourceBacked, metrics: []}, missing, escape, sourcedNumber,
  () => [], money, [], () => []);
assert.equal(missing('kpi-strip').hidden, true,
  'An empty KPI grid must not reserve a blank row above the briefing');
assert.equal(missing('kpi-strip').innerHTML, '');

assert.doesNotMatch(visible('forecast-briefing-copy').innerHTML,
  /target unavailable|forecast target|missing quota/i,
  'A verified revenue readout must not invent absent quota commentary');
assert.equal(visible('forecast-evidence-count').hidden, true,
  'An unsupported evidence-count badge must disappear');

const setupHeader = new Function(
  'document', 'data', 'companyName', '$', 'fictionalFixture', 'hasNumber', 'divisionTeams',
  'sourcedNumber', 'accountRecords', 'escape', 'money', bodyFor('setupHeader')
);
const header = fakeElements();
setupHeader({title: ''}, {
  company: {name: 'Summit Analytics', division: 'Enterprise', divisionLead: {name: 'Priya Desai'}},
  forecast: {base: 0}
}, 'Summit Analytics', header, false, hasNumber, [], sourcedNumber, () => [], escape, money);
assert.match(header('overview-summary').innerHTML, /Forecast \$0/);
assert.doesNotMatch(header('overview-summary').innerHTML, /target unavailable|quota|missing/i,
  'The executive overview omits an unsupported quota while preserving sourced zero revenue');
"""
        )

    def test_complete_fictional_demo_keeps_all_supported_interactive_forecast_sections(
        self,
    ) -> None:
        self.run_node(
            r"""
const path = require('node:path');
const fixture = JSON.parse(fs.readFileSync(path.join(
  path.dirname(process.argv[1]), '..', 'references', 'demo-leadership.json'
), 'utf8'));
const scenario = fixture.forecast.scenarios.find(item => item.key === 'base');
const components = fixture.forecast.components.map(component => ({
  ...component, adjusted: Number(component.value)
}));
const demo = forecastElements(fixture.forecast, true, scenario, {
  components, scenarios: fixture.forecast.scenarios
});
for (const id of [
  'forecast-subheading', 'forecast-layout', 'forecast-panel', 'forecast-eyebrow',
  'forecast-context', 'forecast-total', 'forecast-position', 'forecast-summary',
  'scenario-tabs', 'scenario-studio', 'stacked-wrap', 'weekly-panel', 'weekly-total',
  'weekly-badge', 'bar-chart', 'weekly-implication'
]) {
  assert.equal(demo(id).hidden, false, id + ' remains visible in the fully sourced demo');
}
assert.equal(demo('forecast-layout').dataset.panelCount, '2');
assert.equal(demo('forecast-summary').dataset.metricCount, '3');
assert.match(demo('forecast-summary').innerHTML, /Gap to.*Modeled confidence.*Attainment path/);
assert.equal(demo('forecast-heading').textContent,
  'What changes the quarter-end forecast');
"""
        )


if __name__ == "__main__":
    unittest.main()
