import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import vm from 'node:vm';
import { DEVDAY_URI, DEVDAY_TOOL, openDevDay } from '../mcp/devday.mjs';

// Synthetic fixture. Never a bundled or asserted real event schedule.
const agenda = {
  date: '2026-01-10', timezone: 'America/Los_Angeles', location: 'Example venue',
  checked_on: '2026-01-01', source_url: 'https://devday.openai.com/',
  events: [
    { id: 'program', title: 'Example program', start: '2026-01-10T11:00:00-08:00', end: '2026-01-10T15:30:00-08:00', selected: true },
    { id: 'meal', title: 'Example meal', start: '2026-01-10T11:30:00-08:00', end: null },
  ],
};
const plain = value => JSON.parse(JSON.stringify(value));
function rpc(requests) {
  const result = spawnSync(process.execPath, [new URL('../mcp/server.mjs', import.meta.url).pathname], {
    input: requests.map((request, i) => JSON.stringify({ jsonrpc: '2.0', id: i + 1, ...request })).join('\n') + '\n',
    encoding: 'utf8', timeout: 5000,
  });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stderr, '');
  return result.stdout.trim().split('\n').map(JSON.parse);
}

test('real stdio server advertises the entrypoint, serves HTML, and passes verified input without shared state', () => {
  const results = rpc([
    { method: 'initialize', params: { protocolVersion: '2025-11-25' } },
    { method: 'tools/list' }, { method: 'resources/list' },
    { method: 'resources/read', params: { uri: DEVDAY_URI } },
    { method: 'tools/call', params: { name: DEVDAY_TOOL.name, arguments: { agenda } } },
    { method: 'tools/call', params: { name: DEVDAY_TOOL.name, arguments: {} } },
  ]).map(response => response.result);
  assert.deepEqual(results[0].capabilities.resources, {});
  const tool = results[1].tools.find(tool => tool.name === DEVDAY_TOOL.name);
  assert.deepEqual(tool._meta['openai/ui'].entrypoints, [{ type: 'thread' }]);
  assert.equal(tool._meta.ui.resourceUri, results[2].resources[0].uri);
  const resource = results[3].contents[0];
  assert.equal(resource.mimeType, 'text/html;profile=mcp-app');
  assert.equal(resource._meta['openai/ui'].preferredDisplayMode, 'fullscreen');
  assert.match(resource.text, /ui\/initialize/);
  assert.match(resource.text, /Use plan in chat/);
  assert.doesNotMatch(resource.text, /@@[A-Z_]+@@|<script src=|fetch\(|Example venue/);
  assert.deepEqual(results[4].structuredContent.agenda, agenda);
  assert.equal(results[5].structuredContent.agenda, null);
});

test('server rejects invalid or private-shaped inputs while preserving overlaps and unknown ends', () => {
  assert.equal(openDevDay({ agenda }).structuredContent.agenda.events[1].end, null);
  for (const patch of [
    { source_url: 'https://openai.enterprise.slack.com/example' },
    { source_url: 'https://devday.openai.com/?ticket=private' },
    { source_url: 'https://user:secret@devday.openai.com/' },
    { date: '2026-02-30' }, { timezone: 'Invalid/zone' }, { ticket: 'private' },
  ]) assert.throws(() => openDevDay({ agenda: { ...agenda, ...patch } }));
  for (const patch of [
    { start: '2026-01-10T11:00:00' }, { start: '2026-01-10T00:30:00+09:00' },
    { end: '2026-01-10T09:00:00-08:00' }, { selected: 'false' }, { attendeeEmail: 'private@example.com' },
  ]) assert.throws(() => openDevDay({ agenda: { ...agenda, events: [{ ...agenda.events[0], ...patch }] } }));
  assert.throws(() => openDevDay({ agenda: { ...agenda, events: [agenda.events[0], agenda.events[0]] } }));
});

// Exercise the actual bridge against a protocol host, without claiming this is
// ChatGPT. UI layout and host placement need separate host verification.
async function host(options = {}) {
  const outgoing = [], handlers = new Map();
  const nodes = new Map();
  let currentPlan = { date: agenda.date, source_url: agenda.source_url, timezone: agenda.timezone, events: [agenda.events[0]] };
  let rendered = 0, restored = 0;
  function node(key) {
    if (!nodes.has(key)) nodes.set(key, { disabled: false, hidden: false, textContent: '', addEventListener(type, handler) { handlers.set(`${key}:${type}`, handler); } });
    return nodes.get(key);
  }
  const parent = { postMessage(message, origin) { outgoing.push({ ...plain(message), origin }); } };
  const window = {
    parent,
    DevDayAgenda: {
      getPlan: () => currentPlan,
      planText: () => currentPlan.events.map(event => event.title).join('\n'),
      render: () => { rendered++; },
      restore: plan => { restored++; currentPlan = plan; },
    },
    addEventListener: (type, callback) => handlers.set(type, callback),
    removeEventListener: type => handlers.delete(type),
  };
  const document = {
    querySelector: node, querySelectorAll: () => [],
    documentElement: { style: { setProperty() {} } },
    addEventListener: (type, callback) => handlers.set(type, callback),
  };
  vm.runInNewContext(readFileSync(new URL('../mcp/devday-client.js', import.meta.url), 'utf8'), { window, document, setTimeout, clearTimeout });
  const receive = (message, source = parent, origin = 'https://host.example') => handlers.get('message')?.({ source, origin, data: { jsonrpc: '2.0', ...plain(message) } });
  const flush = async () => { await new Promise(resolve => setImmediate(resolve)); };
  const init = outgoing[0];
  assert.equal(init.method, 'ui/initialize');
  receive({ id: init.id, result: {
    protocolVersion: '2026-01-26',
    hostCapabilities: options.capabilities ?? { updateModelContext: { text: {}, structuredContent: {} }, downloadFile: {} },
    hostContext: { displayMode: 'inline', availableDisplayModes: ['inline', 'fullscreen'], ...(options.context ?? {}) },
  } });
  await flush();
  const display = outgoing.find(message => message.method === 'ui/request-display-mode');
  receive({ id: display.id, result: { mode: 'inline' } });
  await flush();
  return { outgoing, nodes, handlers, receive, flush, parent, window,
    counts: () => ({ rendered, restored }),
    change: () => { currentPlan = { ...currentPlan, events: [agenda.events[1]] }; handlers.get('devday:change')(); },
    close: () => receive({ id: 'teardown', method: 'ui/resource-teardown' }),
  };
}

test('host bridge renders the launch result, requests the panel once, and only attaches after a click', async () => {
  const h = await host();
  const result = { method: 'ui/notifications/tool-result', params: openDevDay({ agenda }) };
  h.receive(result, {}); h.receive(result, h.parent, 'https://other.example');
  assert.equal(h.counts().rendered, 0);
  h.receive(result);
  assert.equal(h.counts().rendered, 1);
  assert.equal(h.outgoing.some(message => message.method === 'tools/call'), false);
  assert.equal(h.outgoing.some(message => message.method === 'ui/update-model-context'), false);
  const attaching = h.handlers.get('#attach:click')();
  const context = h.outgoing.at(-1);
  assert.equal(context.method, 'ui/update-model-context');
  assert.equal(context.params.structuredContent.devdayPlan.events[0].id, 'program');
  h.receive({ id: context.id, result: { _meta: { 'openai/modelContext': { updateId: 'accepted' } } } });
  await attaching;
  assert.match(h.nodes.get('#connection').textContent, /Plan attached/);
  h.change();
  assert.match(h.nodes.get('#connection').textContent, /Plan changed/);
  const beforeRemoval = h.outgoing.length;
  h.receive({ method: 'ui/notifications/host-context-changed', params: { 'openai/modelContext': null, displayMode: 'inline' } });
  assert.equal(h.outgoing.length, beforeRemoval);
  assert.equal(h.window.DevDayAgenda.getPlan().events[0].id, 'meal');
  assert.equal(h.outgoing.filter(message => message.method === 'ui/request-display-mode').length, 1);
  assert.equal(h.outgoing.some(message => message.method === 'ui/message'), false);
  h.close();
});

test('initial attached plan restores once, but later context cannot overwrite newer choices', async () => {
  const plan = { date: agenda.date, timezone: agenda.timezone, source_url: agenda.source_url, events: [agenda.events[1]] };
  const h = await host({ context: { 'openai/modelContext': { structuredContent: { devdayPlan: plan } } } });
  h.receive({ method: 'ui/notifications/tool-result', params: openDevDay({ agenda }) });
  assert.equal(h.counts().restored, 1);
  h.change();
  h.receive({ method: 'ui/notifications/host-context-changed', params: { 'openai/modelContext': { structuredContent: { devdayPlan: plan } } } });
  assert.equal(h.counts().restored, 1);
  h.close();
});

test('unsupported context and downloads degrade honestly; download uses the host when supported', async () => {
  const unsupported = await host({ capabilities: {} });
  assert.equal(unsupported.nodes.get('#attach').disabled, true);
  assert.equal(unsupported.nodes.get('#download').hidden, true);
  assert.match(unsupported.nodes.get('#connection').textContent, /cannot attach/);
  unsupported.close();
  const h = await host();
  const downloading = h.handlers.get('#download:click')({ preventDefault() {}, stopImmediatePropagation() {} });
  const request = h.outgoing.at(-1);
  assert.equal(request.method, 'ui/download-file');
  assert.equal(request.params.contents[0].resource.text, 'Example program');
  h.receive({ id: request.id, result: {} }); await downloading;
  h.close();
});
