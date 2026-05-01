---
name: build-zoom-video-sdk-app
description: Use when using Video SDK.
---

# Build Zoom Video SDK App

Use this skill when the user needs a custom video session rather than a real Zoom meeting. If the user needs meeting numbers, waiting rooms, hosts, or normal Zoom meeting controls, route to Meeting SDK.

## Workflow

1. Confirm product fit: Video SDK is for custom sessions with app-owned UX and lifecycle.
2. Choose the target platform: web, Android, iOS, macOS, Windows, Linux, Flutter, React Native, Unity, or UI Toolkit.
3. Validate auth: generate Video SDK session tokens server-side and keep SDK credentials out of client code.
4. Implement join, media permissions, audio/video publish-subscribe, screen share, chat, and leave before advanced media features.
5. Add custom layouts, raw media, recording, live transcription, or storage integrations only after the session lifecycle is stable.
6. Debug by isolating token generation, SDK version, browser isolation, platform permissions, media device behavior, and entitlement limits.

## References

- Full preserved guide: [references/full-guide.md](references/full-guide.md)
- Web: [web/SKILL.md](web/SKILL.md)
- Android: [android/SKILL.md](android/SKILL.md)
- iOS: [ios/SKILL.md](ios/SKILL.md)
- Windows: [windows/SKILL.md](windows/SKILL.md)
- Linux: [linux/SKILL.md](linux/SKILL.md)
- UI Toolkit: [../ui-toolkit/SKILL.md](../ui-toolkit/SKILL.md)
- Session lifecycle: [references/session-lifecycle.md](references/session-lifecycle.md)
