"""Runtime regressions shared by seller and leadership dashboard templates."""

from __future__ import annotations

import unittest
from pathlib import Path

from sales_test_support import SalesTestCase

SKILL_DIRECTORY = Path(__file__).resolve().parent.parent


class DashboardClientRuntimeTests(SalesTestCase):
    def test_pipeline_groups_each_account_once_by_its_actual_next_blocker(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        template = template_path.read_text(encoding="utf-8")

        for phase_id, phase_label in (
            ("pilot", "Pilot & rollout"),
            ("security", "Security review"),
            ("ownership", "Buyer & ownership"),
            ("commercial", "Commercial alignment"),
            ("renewal", "Renewal readiness"),
            ("paused", "On hold"),
        ):
            with self.subTest(phase=phase_id):
                self.assertIn(f'{{ id: "{phase_id}", label: "{phase_label}" }}', template)
        self.assertIn("section.dataset.phase = phase.id", template)
        self.assertIn("button.dataset.account = account.account", template)
        self.assertIn(
            '"motion-badge" + (/renew/i.test(text(account.motion)) ? " renewal" : "")', template
        )

        pipeline_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const portfolio = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n      \\}'
  ));
  assert.ok(match, 'The pipeline phase helper ' + name + ' must exist');
  return match[1];
}

const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const detailFor = row => portfolio.accountDetails[row.account] || {};
const verifiedMeetingEvents = row => (detailFor(row).events || []).filter(
  event => event.source === 'Google Calendar'
);
const phaseFor = new Function('row', 'text', 'detailFor', 'verifiedMeetingEvents',
  bodyFor('pipelinePhase'));
const pipelinePhase = row => phaseFor(row, text, detailFor, verifiedMeetingEvents);
const accounts = [...portfolio.workNow, ...portfolio.watch, ...portfolio.paused];
const northstar = accounts.find(account => account.account === 'Northstar Health');
const atlas = accounts.find(account => account.account === 'Atlas Manufacturing');
const redwood = accounts.find(account => account.account === 'Redwood Retail');
const bluePeak = accounts.find(account => account.account === 'BluePeak Logistics');
const harbor = accounts.find(account => account.account === 'Harbor Technologies');
const ember = accounts.find(account => account.account === 'Ember Energy');
const lattice = accounts.find(account => account.account === 'Lattice Public Sector');

assert.equal(northstar.stage, 'Security review', 'CRM stage must remain source-authored');
assert.equal(pipelinePhase(northstar), 'pilot',
  'Northstar belongs in pilot work because its immediate blocker is the upcoming pilot review');
assert.equal(pipelinePhase(atlas), 'commercial');
assert.equal(pipelinePhase(redwood), 'renewal');
assert.equal(pipelinePhase(bluePeak), 'ownership',
  'A missing rollout owner is not a commercial-alignment blocker');
assert.equal(pipelinePhase(harbor), 'ownership',
  'A missing executive sponsor belongs in the buyer and ownership queue');
assert.equal(pipelinePhase(ember), 'paused',
  'A procurement hold must never be represented as active commercial work');
assert.equal(pipelinePhase(lattice), 'paused',
  'Suppressed outreach must remain on hold until seller ownership is confirmed');

const phases = ['pilot', 'security', 'ownership', 'commercial', 'renewal', 'paused'];
const groups = Object.fromEntries(phases.map(phase => [
  phase, accounts.filter(account => pipelinePhase(account) === phase)
]));
const groupedAccounts = Object.values(groups).flat();
assert.equal(groupedAccounts.length, accounts.length,
  'Every grounded account must appear in exactly one primary blocker queue');
assert.equal(new Set(groupedAccounts.map(account => account.account)).size, accounts.length,
  'Renewal motion, security stage, or account actions must never duplicate an account across queues');
assert.deepEqual(
  phases.filter(phase => groups[phase].some(account => account.account === northstar.account)),
  ['pilot'],
  'Northstar cannot also appear in the security queue merely because its CRM stage is Security review'
);

const actionFor = new Function('row', 'text', bodyFor('suggestedNextAction'));
const suggestedNextAction = row => actionFor(row, text);
const opened = [];
function create(tag, className, content) {
  return {
    tag, className, content, dataset: {}, attributes: {}, handlers: {}, children: [],
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, callback) { this.handlers[name] = callback; },
    append(...children) { this.children.push(...children); }
  };
}
const buildPipelineButton = new Function(
  'account', 'create', 'text', 'suggestedNextAction', 'openAccountDrawer',
  bodyFor('pipelineAccountButton')
);
const button = buildPipelineButton(
  northstar, create, text, suggestedNextAction,
  (account, trigger) => opened.push({account, trigger})
);
function contentOf(node) {
  return [node.content, ...node.children.flatMap(contentOf)].filter(Boolean);
}
const visibleContent = contentOf(button);
assert.ok(visibleContent.includes('Northstar Health · Pilot review upcoming'));
assert.ok(visibleContent.includes('Security review'),
  'The truthful CRM stage remains visible as secondary context in the pilot queue');
assert.ok(visibleContent.includes(
  'Review your pilot scorecard and the uptime concern with Jordan Lee, Casey Patel, and Priya Shah.'),
  'The next action must explain the actual pilot-readiness work instead of showing a generic label');
assert.equal(button.dataset.account, 'Northstar Health');
assert.equal(button.attributes['aria-controls'], 'account-drawer');
button.handlers.click();
assert.deepEqual(opened, [{account: northstar, trigger: button}]);
"""

        self.assert_node_script(
            pipeline_check,
            str(template_path),
            str(SKILL_DIRECTORY / "references" / "demo-portfolio.json"),
        )

    def test_codex_default_theme_and_optional_pet_render_in_both_dashboards(self) -> None:
        templates = (
            SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html",
            SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html",
        )
        for template in templates:
            source = template.read_text(encoding="utf-8")
            with self.subTest(template=template.name):
                self.assertIn("--canvas: #f6f6f6", source)
                self.assertIn("--surface: #ffffff", source)
                self.assertIn("--ink: #171717", source)
                self.assertIn("--muted: #626262", source)
                self.assertIn("--line: #d2d2d2", source)
                self.assertIn('id="codex-pet"', source)

        pet_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');

function functionSource(source, name) {
  const match = source.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n(?:      |        )\\}'
  ));
  assert.ok(match, 'Missing ' + name);
  return match[0];
}

for (const path of process.argv.slice(1)) {
  const source = fs.readFileSync(path, 'utf8');
  const elements = {
    'codex-pet': {
      hidden: true, alt: '', src: '', handlers: {},
      addEventListener(name, callback) { this.handlers[name] = callback; }
    },
    'brand-mark': {hidden: false}
  };
  const get = id => elements[id];
  const text = (value, fallback) => {
    const result = value == null ? '' : String(value).trim();
    return result || fallback || '';
  };
  const document = {getElementById: get};
  const $ = get;
  const run = new Function(
    'source', 'document', '$', 'text',
    functionSource(source, 'suppliedCodexPet') + '\n' +
      functionSource(source, 'renderCodexPet') + '\nrenderCodexPet(source);'
  );

  run({}, document, $, text);
  assert.equal(elements['codex-pet'].hidden, true);
  assert.equal(elements['brand-mark'].hidden, false,
    'No supplied pet must preserve the grounded company mark');

  run({codexPet: {name: 'Codex', imageUrl: 'https://example.com/pet.png'}}, document, $, text);
  assert.equal(elements['codex-pet'].hidden, true,
    'A remote image must not be fetched by a durable local dashboard');

  const imageUrl = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ';
  run({codexPet: {name: 'Codex', imageUrl}}, document, $, text);
  assert.equal(elements['codex-pet'].hidden, false);
  assert.equal(elements['codex-pet'].src, imageUrl);
  assert.equal(elements['codex-pet'].alt, 'Codex · Codex pet');
  assert.equal(elements['brand-mark'].hidden, true);
  elements['codex-pet'].handlers.error();
  assert.equal(elements['codex-pet'].hidden, true);
  assert.equal(elements['brand-mark'].hidden, false,
    'A failed supplied image must fall back to the company mark');
}
"""
        self.assert_node_script(pet_check, *(str(path) for path in templates))

    def test_real_account_data_never_invents_customer_events_or_stakeholders(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "account-priority-workspace.template.html"
        source_guardrail_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const match = template.match(/function detailEvents\(row\) \{([\s\S]*?)\n      \}/);
assert.ok(match, 'The source-grounded account-event function must exist');
const detailEvents = new Function(
  'row', 'detailFor', 'isFictionalDemo', 'text', 'sellerName', match[1]
);
const text = (value, fallback) => value == null || value === '' ? fallback || '' : String(value);
const account = {
  account: 'Actual Customer',
  primaryContact: 'Real Buyer · Executive sponsor',
  stage: 'Evaluation',
  value: '$125,000',
  whyItMatters: 'Buyer requested a verified security review.',
  status: 'Awaiting customer response'
};

assert.deepEqual(
  detailEvents(account, () => ({}), false, text, 'Actual Seller'),
  [],
  'A real account with no verified events must not receive fabricated CRM or email activity'
);
const verifiedDetailEvent = {source: 'Salesforce', title: 'Verified opportunity update'};
assert.deepEqual(
  detailEvents(account, () => ({events: [verifiedDetailEvent]}), false, text, 'Actual Seller'),
  [verifiedDetailEvent],
  'A real account must retain explicitly supplied verified detail events'
);
const verifiedRowEvent = {source: 'Slack', title: 'Verified customer request'};
assert.deepEqual(
  detailEvents({...account, events: [verifiedRowEvent]}, () => ({}), false, text, 'Actual Seller'),
  [verifiedRowEvent],
  'A real account must retain explicitly supplied verified row events'
);
assert.ok(
  detailEvents(account, () => ({}), true, text, 'Demo Seller').length,
  'Illustrative fallback activity is permitted only for the explicitly fictional demo'
);

const peopleMatch = template.match(/function detailPeople\(row\) \{([\s\S]*?)\n      \}/);
assert.ok(peopleMatch, 'The source-grounded account-stakeholder function must exist');
const detailPeople = new Function('row', 'detailFor', 'sellerName', 'text', peopleMatch[1]);
const suppliedStakeholder = {name: 'Verified Technical Buyer', role: 'Security reviewer'};
assert.deepEqual(
  detailPeople(account, () => ({stakeholders: [suppliedStakeholder]}), 'Actual Seller', text),
  [suppliedStakeholder],
  'Explicitly verified stakeholders must be preserved without fictional additions'
);
assert.deepEqual(
  detailPeople({account: 'Actual Customer'}, () => ({}), 'Actual Seller', text),
  [{name: 'Actual Seller', role: 'You · Account owner', status: 'Owner'}],
  'A missing customer contact must not manufacture a fictional buyer or specialist'
);
const groundedPeople = detailPeople(account, () => ({}), 'Actual Seller', text);
assert.deepEqual(groundedPeople.map(person => person.name), ['Real Buyer', 'Actual Seller']);
assert.ok(
  !groundedPeople.some(person => ['Jordan Lee', 'Priya Shah', 'Casey Patel'].includes(person.name)),
  'Demo-only Northstar stakeholders must never leak into a real customer account'
);
"""

        self.assert_node_script(source_guardrail_check, str(template_path))

    def test_forecast_axis_uses_raw_totals_and_shows_shortfall_only_below_target(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        template = template_path.read_text(encoding="utf-8")

        self.assert_contains(
            template,
            "const axisMaximum = Math.max(target ?? 0, componentTotal, 1)",
            "const targetPosition = target === null ? null : target / axisMaximum * 100",
            "const shortfall = gap !== null && gap > 0 ? gap : 0",
            '(shortfall > 0 ? \'<span class="stacked-shortfall"',
            "targetMarker.hidden = target === null",
            "chartTargetLabel.hidden = target === null",
            'targetMarker.style.left = targetPosition + "%"',
            ".stacked-segment, .stacked-shortfall { height: 100%; flex: 0 0 auto;",
        )

        projection_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');
const data = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const match = template.match(/function projectedComponents\(\) \{([\s\S]*?)\n        \}/);
assert.ok(match, 'The executable dashboard projection function must exist');
const project = new Function(
  'data', 'state', 'list', 'fictionalFixture', 'scenarioOptions', 'hasNumber',
  'initialScenario', 'sourcedNumber', match[1]
);
const list = value => Array.isArray(value) ? value : [];
const hasNumber = value => value !== null && value !== undefined && value !== ''
  && Number.isFinite(Number(value));
const sourcedNumber = value => hasNumber(value) ? Number(value) : null;
const fictionalBaseline = data.forecast.scenarios.find(scenario => scenario.key === 'base');
for (const [label, sliders, relationship] of [
  ['below', {commitCloseRate:100,additionalPipelineWinRate:40,dealSizeUplift:0}, -1],
  ['exact', {commitCloseRate:100,additionalPipelineWinRate:50,
    dealSizeUplift:55000 / 1755000 * 100}, 0],
  ['above', {commitCloseRate:100,additionalPipelineWinRate:50,dealSizeUplift:20}, 1]
]) {
  const components = project(
    data, {sliders}, list, true, data.forecast.scenarios, hasNumber, fictionalBaseline,
    sourcedNumber
  );
  const total = components.reduce((sum, component) => sum + component.adjusted, 0);
  const target = data.forecast.target;
  const axisMaximum = Math.max(target, total, 1);
  const marker = target / axisMaximum * 100;
  const shortfall = Math.max(target - total, 0);
  assert.equal(Math.sign(total - target), relationship, label + ' target relationship');
  assert.equal(shortfall > 0, relationship < 0, label + ' phantom shortfall');
  assert.equal(marker < 100, relationship > 0, label + ' target marker location');
  assert.ok(Math.abs((total + shortfall) / axisMaximum - 1) < 1e-9,
    label + ' colored components and real shortfall must fill the target-relative axis');
}

const groundedComponents = project({
  forecast: {components: [
    {key: 'closedWon', label: 'Closed won', value: 250000},
    {key: 'commit', label: 'Unverified commit', value: null},
    {key: 'bestCase', label: 'Verified empty pipeline', value: 0}
  ]}
}, {sliders: {}}, list, false, [], hasNumber, {}, sourcedNumber);
assert.deepEqual(groundedComponents, [
  {key: 'closedWon', label: 'Closed won', value: 250000, adjusted: 250000},
  {key: 'bestCase', label: 'Verified empty pipeline', value: 0, adjusted: 0}
], 'Real forecasts without verified scenarios must preserve sourced zeroes and omit gaps');

const sourcedScenario = {
  key: 'verified-outlook', label: 'Verified outlook', commitCloseRate: 100,
  additionalPipelineWinRate: 25, dealSizeUplift: 20
};
const sourcedComponents = [
  {key: 'closedWon', value: 100}, {key: 'commit', value: 200},
  {key: 'bestCase', value: 50}, {key: 'upside', value: 50}
];
const sliders = {
  commitCloseRate: 100, additionalPipelineWinRate: 25, dealSizeUplift: 20
};
const noBaseScenario = project({
  forecast: {components: sourcedComponents, scenarios: [sourcedScenario]}, topDeals: []
}, {sliders}, list, false, [sourcedScenario], hasNumber, sourcedScenario, sourcedNumber);
assert.equal(noBaseScenario.find(component => component.key === 'bestCase').adjusted, 100,
  'A real forecast without a base entry must use its verified scenario, not an invented 40%');

const zeroPools = project({
  forecast: {
    components: sourcedComponents, scenarios: [sourcedScenario],
    qualifiedPipelineValue: 0, eligibleExpansionValue: 0
  },
  topDeals: [{motion: 'Expansion', stage: 'Active', value: 10000}]
}, {sliders}, list, false, [sourcedScenario], hasNumber, sourcedScenario, sourcedNumber);
assert.equal(zeroPools.find(component => component.key === 'bestCase').adjusted, 0,
  'A verified zero qualified-pipeline amount must not be replaced with an inferred value');
assert.equal(zeroPools.find(component => component.key === 'upside').adjusted, 0,
  'A verified zero expansion pool must not be replaced with customer opportunity amounts');
"""
        self.assert_node_script(
            projection_check,
            str(template_path),
            str(SKILL_DIRECTORY / "references" / "demo-leadership.json"),
        )

    def test_real_leadership_runtime_preserves_verified_zeroes_and_truthful_gaps(self) -> None:
        template_path = SKILL_DIRECTORY / "assets" / "sales-leadership-dashboard.template.html"
        runtime_guardrail_check = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const template = fs.readFileSync(process.argv[1], 'utf8');

function bodyFor(name) {
  const match = template.match(new RegExp(
    'function ' + name + '\\([^)]*\\) \\{([\\s\\S]*?)\\n        \\}'
  ));
  assert.ok(match, 'The source-grounded leadership helper ' + name + ' must exist');
  return match[1];
}

const sourceMatch = template.match(/const sourceIsVerified = \(source\) => ([\s\S]*?);\n/);
assert.ok(sourceMatch, 'Leadership source verification must be explicit');
const sourceIsVerified = new Function('source', 'fictionalFixture', 'return ' + sourceMatch[1]);
assert.equal(sourceIsVerified({name: 'Salesforce', verified: true}, false), true);
for (const unverified of [
  {name: 'Salesforce'},
  {name: 'Salesforce', verified: false},
  {name: 'Salesforce', verified: true, status: 'Disconnected'}
]) {
  assert.equal(sourceIsVerified(unverified, false), false,
    'Real dashboards must never claim unverified or disconnected sources');
}
assert.equal(sourceIsVerified({name: 'Fictional Salesforce'}, true), true,
  'The explicitly fictional connector-free demo retains its sample-source behavior');

const performanceAttainment = new Function('person', bodyFor('performanceAttainment'));
const performanceStatus = new Function('attainment', bodyFor('performanceStatus'));
const growthLabel = new Function('team', bodyFor('growthLabel'));
assert.equal(performanceAttainment({attainment: 0}), 0,
  'An explicitly sourced zero-percent attainment remains meaningful');
assert.equal(performanceAttainment({forecast: 0, target: 1000}), 0);
assert.equal(performanceAttainment({forecast: 1000}), null);
assert.equal(performanceAttainment({target: 1000}), null);
assert.equal(performanceAttainment({forecast: 1000, target: 0}), null);
assert.equal(performanceStatus(null).label, 'Unavailable');
assert.equal(performanceStatus(0).label, 'Behind plan');
assert.equal(growthLabel({}), '', 'Missing manager growth must not be fabricated');
assert.equal(growthLabel({growthRate: 0}), '+0.0% week over week');

const hasNumber = value => value !== null && value !== undefined && value !== ''
  && Number.isFinite(Number(value));
const sourcedNumber = value => hasNumber(value) ? Number(value) : null;
const list = value => Array.isArray(value) ? value : value ? [value] : [];
const money = value => hasNumber(value) ? '$' + Number(value).toLocaleString('en-US')
  : 'Unavailable';
const signedMoney = value => (Number(value) >= 0 ? '+' : '−') + money(Math.abs(value));
const escape = value => String(value ?? '');
const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const renderForecast = new Function(
  'selectedScenario', 'projectedComponents', 'scenarioOptions', 'sourcedNumber', 'data',
  'clamp', '$', 'signedMoney', 'money', 'escape', 'renderScenarioControls', 'state', 'list',
  'accountRecords', 'fictionalFixture', 'hasNumber', bodyFor('renderForecast')
);

function render(payload, components, accounts = []) {
  const elements = new Map();
  const $ = id => {
    if (!elements.has(id)) {
      elements.set(id, {
        dataset: {}, style: {}, attributes: {}, hidden: false, textContent: '', innerHTML: '',
        setAttribute(name, value) { this.attributes[name] = value; },
        querySelectorAll() { return []; }
      });
    }
    return elements.get(id);
  };
  renderForecast(
    () => ({}), () => components, [], sourcedNumber, payload, clamp, $, signedMoney, money,
    escape, () => assert.fail('Unsourced scenario controls must remain hidden'), {}, list,
    () => accounts, false, hasNumber
  );
  return $;
}

const unavailable = render({forecast: {}}, []);
assert.equal(unavailable('forecast-total').textContent, '');
assert.equal(unavailable('forecast-total').hidden, true);
assert.equal(unavailable('weekly-total').textContent, '');
assert.equal(unavailable('weekly-total').hidden, true);
assert.equal(unavailable('weekly-badge').hidden, true);
assert.equal(unavailable('weekly-panel').hidden, true);
assert.equal(unavailable('forecast-context').hidden, true);
assert.equal(unavailable('forecast-panel').hidden, true);
assert.equal(unavailable('forecast-layout').hidden, true);
assert.equal(unavailable('forecast-subheading').hidden, true);
assert.equal(unavailable('scenario-tabs').hidden, true);
assert.equal(unavailable('scenario-studio').hidden, true);
assert.equal(unavailable('target-marker').hidden, true);
assert.equal(unavailable('target-label').hidden, true);
assert.equal(unavailable('stacked-wrap').hidden, true);
assert.equal(unavailable('stacked-bar').dataset.target, undefined);
assert.equal(unavailable('forecast-summary').hidden, true);
assert.equal(unavailable('forecast-summary').innerHTML, '');
assert.equal(unavailable('weekly-implication').hidden, true);
assert.equal(unavailable('weekly-implication').innerHTML, '');
assert.doesNotMatch(unavailable('weekly-implication').innerHTML, /Northstar|pilot/i,
  'An actual dashboard cannot inherit the fictional Northstar pilot sentence');

const sourcedZero = render(
  {forecast: {base: 0, target: 1000, weeklyMovement: 0}},
  [{key: 'closedWon', label: 'Closed won', adjusted: 0}],
  [{name: 'Harbor Health', decisionDate: 'Decision after customer security review'}]
);
assert.equal(sourcedZero('forecast-total').textContent, '$0');
assert.equal(sourcedZero('weekly-total').textContent, '+$0');
assert.equal(sourcedZero('weekly-panel').hidden, false);
assert.equal(sourcedZero('weekly-total').hidden, false);
assert.equal(sourcedZero('weekly-badge').hidden, false);
assert.equal(sourcedZero('weekly-badge').textContent, 'Unchanged');
assert.equal(sourcedZero('target-marker').hidden, false);
assert.equal(sourcedZero('stacked-bar').dataset.target, '1000');
assert.equal(sourcedZero('forecast-summary').hidden, false);
assert.match(sourcedZero('forecast-summary').innerHTML, /0% of plan/);
assert.match(sourcedZero('weekly-implication').innerHTML,
  /Next grounded customer decision: Harbor Health — customer security review/);

const fallbackTeamFocus = new Function(
  'divisionTeams', 'performanceAttainment', 'data', 'list', bodyFor('fallbackTeamFocus')
);
assert.equal(fallbackTeamFocus(
  [{manager: 'Morgan Lee', accountCount: 0, forecast: 0, target: 1000}],
  performanceAttainment, {}, list
)[0].accounts, 0, 'Verified zero-account team rollups must not become unavailable');
"""

        self.assert_node_script(runtime_guardrail_check, str(template_path))


if __name__ == "__main__":
    unittest.main()
