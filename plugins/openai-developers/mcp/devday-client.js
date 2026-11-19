// A small MCP Apps JSON-RPC client. No browser network requests or runtime SDK.
// Only the embedding parent can initialize it or deliver tool results.
(() => {
  const view = window.DevDayAgenda;
  const attach = document.querySelector('#attach');
  const download = document.querySelector('#download');
  const status = document.querySelector('#connection');
  const pending = new Map();
  let nextId = 0, parentOrigin, initialized = false, closed = false;
  let hostContext = {}, capabilities = {}, restoring = false, localRevision = 0;
  let attachedText = null, attaching = false, initialContext, initialResult = true, contextClears = 0;
  let observer;
  const say = text => { status.hidden = !text; status.textContent = text; };

  function send(message) {
    window.parent.postMessage({ jsonrpc: '2.0', ...message }, parentOrigin && parentOrigin !== 'null' ? parentOrigin : '*');
  }
  function request(method, params) {
    if (closed) return Promise.reject(new Error('View closed.'));
    const id = `devday-${++nextId}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { pending.delete(id); reject(new Error('ChatGPT did not respond.')); }, 15000);
      pending.set(id, { resolve, reject, timer });
      send({ id, method, params });
    });
  }
  function updateControls() {
    const hasPlan = view.getPlan().events.length > 0;
    attach.disabled = !initialized || !capabilities.updateModelContext?.text || !hasPlan || attaching;
    download.hidden = !capabilities.downloadFile;
  }
  function applyContext(context) {
    Object.assign(hostContext, context);
    const variables = context?.styles?.variables;
    for (const key of ['--font-sans', '--font-weight-normal', '--cursor-interaction']) {
      if (typeof variables?.[key] === 'string') document.documentElement.style.setProperty(key, variables[key]);
    }
    // A removed/sent attachment must stay removed. Keep the attendee's newer
    // choices in the view; reattaching always takes another explicit click.
    if (Object.hasOwn(context, 'openai/modelContext') && context['openai/modelContext'] == null) {
      contextClears++;
      const hadAttachment = attachedText !== null || attaching;
      attachedText = null;
      if (hadAttachment) say('Your plan is no longer attached. Your choices are still here.');
    }
  }
  function dispose() {
    closed = true; initialized = false;
    observer?.disconnect();
    for (const entry of pending.values()) { clearTimeout(entry.timer); entry.reject(new Error('View closed.')); }
    pending.clear(); window.removeEventListener('message', receive); updateControls();
  }
  function receive(event) {
    if (event.source !== window.parent || closed) return;
    if (parentOrigin !== undefined && event.origin !== parentOrigin) return;
    const message = event.data;
    if (!message || message.jsonrpc !== '2.0') return;
    const entry = pending.get(message.id);
    if (entry) {
      if (!Object.hasOwn(message, 'result') && !message.error) return;
      parentOrigin ??= event.origin;
      pending.delete(message.id); clearTimeout(entry.timer);
      if (message.error) entry.reject(new Error('ChatGPT could not complete that action.'));
      else entry.resolve(message.result);
      return;
    }
    if (!initialized) return;
    if (message.method === 'ui/notifications/tool-result') {
      if (message.params?.isError) { say('The agenda could not be loaded. Ask me to check the public schedule again.'); return; }
      const agenda = message.params?.structuredContent?.agenda;
      if (agenda) {
        restoring = true;
        view.render(agenda);
        if (initialResult && localRevision === 0 && initialContext) view.restore(initialContext);
        initialResult = false; restoring = false;
        updateControls();
      }
    } else if (message.method === 'ui/notifications/host-context-changed') {
      applyContext(message.params || {});
    } else if (message.method === 'ping') {
      send({ id: message.id, result: {} });
    } else if (message.method === 'ui/resource-teardown') {
      send({ id: message.id, result: {} }); dispose();
    } else if (message.id !== undefined) {
      send({ id: message.id, error: { code: -32601, message: 'Method not supported.' } });
    }
  }
  document.addEventListener('devday:change', () => {
    if (!restoring) localRevision++;
    updateControls();
    if (attachedText && attachedText !== view.planText()) say('Plan changed. Use plan in chat again to update the attachment.');
  });
  attach.addEventListener('click', async () => {
    if (attach.disabled) return;
    const text = view.planText();
    const clearsAtClick = contextClears;
    attaching = true; updateControls();
    try {
      const result = await request('ui/update-model-context', {
        content: [{ type: 'text', text, _meta: { 'openai/title': 'My DevDay plan' } }],
        ...(capabilities.updateModelContext?.structuredContent ? { structuredContent: { devdayPlan: view.getPlan() } } : {}),
      });
      if (result?.isError) throw new Error('Context unavailable.');
      if (clearsAtClick !== contextClears) return;
      attachedText = text;
      say(text === view.planText() ? 'Plan attached. Ask a question in chat when you’re ready.' : 'Plan changed. Use plan in chat again to update the attachment.');
    } catch { say('Could not attach your plan. Try again or describe your choices in chat.'); }
    finally { attaching = false; updateControls(); }
  });
  // Iframe downloads go through the host, never an unrestricted browser link.
  download.addEventListener('click', async event => {
    event.preventDefault(); event.stopImmediatePropagation();
    if (!capabilities.downloadFile) return;
    try {
      await request('ui/download-file', { contents: [{ type: 'resource', resource: {
        uri: 'file:///devday-plan.txt', mimeType: 'text/plain', text: view.planText(),
      } }] });
    } catch { say('The plan could not be downloaded. Your choices are still here.'); }
  }, true);
  document.querySelectorAll('a').forEach(link => link.addEventListener('click', async event => {
    event.preventDefault();
    if (!capabilities.openLinks) { say('Open devday.openai.com in your browser for the official schedule.'); return; }
    try { await request('ui/open-link', { url: link.href }); }
    catch { say('The link could not be opened. Visit devday.openai.com for the official schedule.'); }
  }));

  attach.hidden = false; download.hidden = true;
  document.querySelector('#plan-help').textContent = 'Choose activities, then attach your plan to your next message.';
  if (window.parent === window) { say('Open this agenda through OpenAI Developers in ChatGPT to use it with chat.'); return; }
  window.addEventListener('message', receive);
  window.addEventListener('pagehide', dispose, { once: true });
  request('ui/initialize', {
    protocolVersion: '2026-01-26',
    appInfo: { name: 'OpenAI DevDay', version: '0.1.0' },
    appCapabilities: { availableDisplayModes: ['inline', 'fullscreen'] },
  }).then(async result => {
    if (closed) return;
    if (result?.protocolVersion !== '2026-01-26') throw new Error('Unsupported UI protocol.');
    capabilities = result.hostCapabilities || {};
    initialized = true;
    initialContext = result.hostContext?.['openai/modelContext']?.structuredContent?.devdayPlan;
    applyContext(result.hostContext || {});
    send({ method: 'ui/notifications/initialized', params: {} });
    if (typeof ResizeObserver !== 'undefined') {
      observer = new ResizeObserver(() => {
        if (initialized && hostContext.displayMode === 'inline') send({ method: 'ui/notifications/size-changed', params: { height: document.documentElement.scrollHeight } });
      });
      observer.observe(document.body);
    }
    updateControls();
    if (!capabilities.updateModelContext?.text) say('This host cannot attach a plan to chat. You can still browse and choose activities here.');
    // Request the side panel once, and respect a declined request or a closed panel.
    if (hostContext.displayMode === 'inline' && hostContext.availableDisplayModes?.includes('fullscreen')) {
      try { const display = await request('ui/request-display-mode', { mode: 'fullscreen' }); hostContext.displayMode = display.mode; }
      catch { /* The agenda remains usable inline. */ }
    }
  }).catch(() => say('Could not connect this view to ChatGPT. Reopen the DevDay agenda to try again.'));
})();
