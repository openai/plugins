# Routing Implementation

This reference provides a compact implementation model for routing a complex developer query from `zoom-general` to specialized skills.

```ts
export type SkillId =
  | 'zoom-general'
  | 'zoom-rest-api'
  | 'zoom-webhooks'
  | 'zoom-websockets'
  | 'zoom-meeting-sdk'
  | 'zoom-meeting-sdk-web'
  | 'zoom-meeting-sdk-web-component-view'
  | 'zoom-video-sdk'
  | 'zoom-video-sdk-web'
  | 'zoom-apps-sdk'
  | 'zoom-rtms'
  | 'zoom-team-chat'
  | 'contact-center'
  | 'virtual-agent'
  | 'phone'
  | 'rivet-sdk'
  | 'probe-sdk'
  | 'zoom-ui-toolkit'
  | 'zoom-cobrowse-sdk'
  | 'zoom-oauth';

interface Signals {
  meetingEmbed: boolean;
  meetingCustomUi: boolean;
  customVideo: boolean;
  restApi: boolean;
  webhooks: boolean;
  websockets: boolean;
  zoomApps: boolean;
  oauth: boolean;
  rtms: boolean;
  teamChat: boolean;
  contactCenter: boolean;
  virtualAgent: boolean;
  phone: boolean;
  rivet: boolean;
  preflight: boolean;
  uiToolkit: boolean;
  cobrowse: boolean;
}

const hasAny = (q: string, words: string[]) => words.some((word) => q.includes(word));

export function detectSignals(rawQuery: string): Signals {
  const q = rawQuery.toLowerCase();
  return {
    meetingEmbed: hasAny(q, ['meeting sdk', 'embed meeting', 'join meeting ui', 'client view', 'component view']),
    meetingCustomUi: hasAny(q, ['custom meeting ui', 'zoommtgembedded', 'zoomapproot', 'embeddable meeting ui']),
    customVideo: hasAny(q, ['video sdk', 'custom video', 'attachvideo', 'peer-video-state-change']),
    restApi: hasAny(q, ['rest api', 'api create meeting', 'api list meetings', '/v2/', 'list users', 'meeting endpoint']),
    webhooks: hasAny(q, ['webhook', 'x-zm-signature', 'event subscription', 'crc']),
    websockets: hasAny(q, ['websocket', 'real-time events', 'persistent connection']),
    zoomApps: hasAny(q, ['zoom apps sdk', 'in-client app', 'layers api', 'collaborate mode']),
    oauth: hasAny(q, ['oauth', 'pkce', 'authorization code', 'token refresh']),
    rtms: hasAny(q, ['rtms', 'real-time media streams', 'live transcript stream', 'audio stream']),
    teamChat: hasAny(q, ['team chat', 'chatbot', 'chat card', 'chat message']),
    contactCenter: hasAny(q, ['contact center', 'engagement context', 'zcc']),
    virtualAgent: hasAny(q, ['virtual agent', 'zva', 'knowledge base sync']),
    phone: hasAny(q, ['zoom phone', 'phone smart embed', 'phone api', 'click to dial']),
    rivet: hasAny(q, ['rivet', 'zoom rivet']),
    preflight: hasAny(q, ['probe sdk', 'preflight', 'diagnostics', 'network readiness']),
    uiToolkit: hasAny(q, ['ui toolkit', 'prebuilt video ui']),
    cobrowse: hasAny(q, ['cobrowse', 'co-browse', 'shared browsing']),
  };
}

export function pickPrimarySkill(s: Signals): SkillId {
  if (s.meetingCustomUi) return 'zoom-meeting-sdk-web-component-view';
  if (s.meetingEmbed && !s.customVideo) return 'zoom-meeting-sdk-web';
  if (s.meetingEmbed) return 'zoom-meeting-sdk';
  if (s.customVideo && !s.meetingEmbed) return 'zoom-video-sdk-web';
  if (s.customVideo) return 'zoom-video-sdk';
  if (s.virtualAgent) return 'virtual-agent';
  if (s.contactCenter) return 'contact-center';
  if (s.zoomApps) return 'zoom-apps-sdk';
  if (s.rtms) return 'zoom-rtms';
  if (s.teamChat) return 'zoom-team-chat';
  if (s.phone) return 'phone';
  if (s.cobrowse) return 'zoom-cobrowse-sdk';
  if (s.uiToolkit) return 'zoom-ui-toolkit';
  if (s.preflight) return 'probe-sdk';
  if (s.websockets) return 'zoom-websockets';
  if (s.webhooks) return 'zoom-webhooks';
  if (s.restApi) return 'zoom-rest-api';
  if (s.oauth) return 'zoom-oauth';
  return 'zoom-general';
}
```

Use this only as a routing aid. The selected skill remains responsible for implementation details and verification.
