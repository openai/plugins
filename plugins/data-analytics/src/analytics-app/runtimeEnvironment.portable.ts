function unavailable(): never {
  throw new Error("This operation is unavailable in a portable artifact.");
}

export async function loadArtifactFromApi(): Promise<never> {
  return unavailable();
}

export async function loadHostedPresentation(): Promise<null> {
  return null;
}

export async function saveHostedPresentation(): Promise<never> {
  return unavailable();
}

export async function loadInlineChartWidgetHtml(): Promise<never> {
  return unavailable();
}

export async function loadSourceText(): Promise<null> {
  return null;
}

export async function sendPromptToHost(): Promise<null> {
  return null;
}

export function readPersistedValue(): null {
  return null;
}

export function writePersistedValue(): void {
  // Portable artifacts never persist reader state.
}

export function launchCodexPromptFallback(): false {
  return false;
}

export function sitePublishingInstructions(surface: string): string {
  return `Publishing is unavailable from this read-only ${surface}.`;
}
