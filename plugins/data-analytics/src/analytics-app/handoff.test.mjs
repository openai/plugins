import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { canonicalPublishedSiteUrl, workModeWebPromptUrl } from "./handoff.mjs";

describe("published Site handoff URLs", () => {
  it("removes all query and hash state from the published Site URL", () => {
    assert.equal(
      canonicalPublishedSiteUrl("https://report.openai.chatgpt.site/path/?token=secret#section"),
      "https://report.openai.chatgpt.site/path/",
    );
  });

  it("prefills ChatGPT without auto-sending", () => {
    const prompt = "Refresh this dashboard from the published Site.";
    const url = new URL(workModeWebPromptUrl(prompt));
    const hash = new URLSearchParams(url.hash.slice(1));

    assert.equal(url.origin, "https://chatgpt.com");
    assert.equal(url.pathname, "/");
    assert.equal(url.search, "");
    assert.equal(hash.get("q"), `Select Work Mode, then send this request:\n\n${prompt}`);
    assert.equal(hash.get("disable_auto_send"), "1");
  });
});
