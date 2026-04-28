# HeyGen Video Agent — Official Prompt Guide (Complete)
Source: https://www.notion.so/heygen/Video-Agent-Prompt-Guide-2e6449792c69801d9353c885aad92c9e

## Core Philosophy
"Video Agent isn't magic; it's a production partner that executes your creative direction."
"The more specific you are about content, style, media types, and scene structure, the closer you'll get to exactly what you envision."

## Three UI Controls
1. **Avatar** — select specific avatar, Auto mode, or "no avatar" for voice-over only (MUST explicitly say "no avatar" in prompt)
2. **Duration** — 30s, 1min, 2min, or Auto (agent follows prompt/script for length, not forced)
3. **Aspect Ratio** — Portrait or Landscape, or Auto

## Prompting Hierarchy (Basic → Advanced)

### Level 1: Basic Prompt
Describe the content you want delivered:
- "Introduce HeyGen to knowledge workers, talk about its Talking Avatar models"
- "Make a compliance training video and explain phishing in detail"

### Level 2: Script-Driven (STRONGLY RECOMMENDED)
Paste a full video script. Agent follows scene-by-scene while improving flow, timing, and visuals.
This is "the single biggest upgrade most people miss."

### Level 3: Scene-by-Scene (Maximum Control)
```
Scene 1: [Scene Type]
  Visual: [Describe exact visual]
  VO/Script: "[What the avatar says]"
  Duration: [Approximate length]
```

## Attachments
- Images, videos, product screenshots, diagrams
- PDFs, documents (agent extracts key info)
- Upload own photo → agent uses as talking avatar
- ALWAYS add context: "Use the attached screenshots as B-roll when discussing features"

## The "Catchall" Style Block (Personal Favorite of HeyGen Team)
```
Use minimal, clean styled visuals. Blue, black, and white as main colors.
Leverage motion graphics as B-rolls and A-roll overlays. Use AI videos when necessary.
When real-world footage is needed, use Stock Media.
Include an intro sequence, outro sequence, and chapter breaks using Motion Graphics.
```

## Style Descriptor Presets
| Style | Best For | Prompt Addition |
|-------|----------|-----------------|
| Minimalistic | Corporate, Tech, SaaS | "Use minimalistic, clean visuals with lots of white space" |
| Cartoon/Animated | Education, Kids content | "Use cartoon-style illustrated visuals" |
| Bold & Vibrant | Marketing, Social | "Use bold, vibrant colors and dynamic visuals" |
| Cinematic | Brand films, High-end | "Use cinematic quality visuals with dramatic lighting" |
| Flat Design | Modern, App demos | "Use flat design style with geometric shapes" |
| Gradient Modern | Tech, Startup | "Use modern gradient backgrounds and sleek transitions" |
| Retro/Vintage | Nostalgia, Creative | "Use retro-inspired visuals with warm tones" |

## Color Specification
- Exact hex codes: "Use #1E40AF as primary blue, #F8FAFC as background white, #0F172A for text"
- Brand colors: "Stick to our brand colors: coral (#FF6B6B), navy (#2C3E50), cream (#FFF5E6)"
- Font families: "Use Inter font family throughout"
- WHY: Without defined style, visuals look inconsistent scene-to-scene

## Media Types

### Motion Graphics
Animated text, icons, charts, shapes, transitions.
- A-roll overlays: lower thirds, bullet points, animated callouts
- B-roll scenes: animated explanations, data viz, process flows
- Chapter cards: section breaks, intros, outros
- Information display: statistics, comparisons, timelines

### AI-Generated Images & Videos
- Conceptual illustrations, abstract concepts
- Custom scenarios stock can't cover
- Stylized visuals in particular artistic style
- Product mockups in various contexts

### Stock Media
Real-world footage from stock libraries.
- Authentic scenes (offices, cities, people)
- Industry-specific (medical, manufacturing, retail)
- Emotional moments, human connection
- Establishing shots, locations

### Media Type Decision Matrix
| Content Type | Motion Graphics | AI Generated | Stock Media |
|---|---|---|---|
| Data/Statistics | ✅ Best | ❌ | ❌ |
| Abstract Concepts | ✅ Good | ✅ Best | ❌ |
| Real Environments | ❌ | ⚠️ Can work | ✅ Best |
| Brand Elements | ✅ Best | ❌ | ❌ |
| Human Emotions | ❌ | ⚠️ Uncanny | ✅ Best |
| Custom Scenarios | ⚠️ Limited | ✅ Best | ⚠️ May not exist |
| Technical Diagrams | ✅ Best | ❌ | ❌ |

## Example Prompts (Steal These)

### Compliance Training
"Use a professional female avatar. Make a compliance training video explaining phishing in detail. Use examples and list top watch-outs. Leverage motion graphics as A-roll overlay and B-roll to help explain core concepts."

### Educational Explainer (Voice-Over Only)
"Create a 1-minute video about camera aperture. Use minimal science diagrams and visualizations. No avatar needed, only voice-over. Cool neutrals (navy, cyan), thin-line diagrams, and slow elegant motion. B-roll is abstract scientific illustrations. Sequencing: definition → diagram expansion → conceptual layering, with fade-through transitions."

### Brand Story (Animated)
"Make a video telling the story of how Twitch got started. Use cartoon-style animations and overlays. I want Twitch's iconic colors and fonts. Use motion graphics overlays and AI-generated B-roll."

## Community Pro Tips

### Stack style instructions at the end
Put content/script first, then add all style directives (colors, motion graphics preferences, media type guidance) as a block at the bottom. Keeps creative intent clean and technical specs organized.

### Save your catchall as a template
If you find a style combo that works, reuse it across all videos. Consistency builds brand recognition.

### Iterate in conversation
Video Agent remembers context within a session. After first render: "make the intro shorter" or "swap the B-roll in scene 3 for stock footage" without re-prompting everything.
