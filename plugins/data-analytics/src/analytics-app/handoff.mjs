export function canonicalPublishedSiteUrl(href) {
  try {
    const url = new URL(href);
    return `${url.origin}${url.pathname}`;
  } catch {
    return String(href).split(/[?#]/, 1)[0];
  }
}

export function workModeWebPromptUrl(prompt) {
  const url = new URL("https://chatgpt.com/");
  const workModePrompt = `Select Work Mode, then send this request:\n\n${prompt}`;
  url.hash = new URLSearchParams({
    q: workModePrompt,
    disable_auto_send: "1",
  }).toString();
  return url.toString();
}
