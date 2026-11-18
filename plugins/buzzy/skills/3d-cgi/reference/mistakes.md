# 3D CGI — Common Mistakes & Fixes

写完词用本表自检，改完再打印。

1. **Vague camera** — "dynamic camera" → "Slow orbital rotation at 45°/sec, constant distance, ease-in/out."
2. **Impossible detail** — "every atom" → "Hyperdetailed grain, wear, microscopic texture. Do not claim atomic resolution."
3. **Contradictory light** — "bright shadows with no source" → name key + fill ratio.
4. **Broken material physics** — "velvet with mirror reflections" → velvet is diffuse; pick a real finish.
5. **Vague particles** — "lots of cool particles" → color, density, path, fade time.
6. **No duration** — always use `VIDEO_DURATION` and say how much of the move completes.
7. **Unsplit hybrid style** — "photoreal in a fantasy world" → "Product photoreal. Environment stylized."
8. **Unclear composition** — "mysterious but show the product" → what is sharp, what is bokeh.
9. **Platform fantasy** — "4K 60fps infinite bitrate" → inherit Session resolution; no codec / fps promises.
10. **Weak hook** — standing-and-looking → first frame must arrest (glow, shatter, scale snap).
11. **No scale** — "a large crystal" → "fist-sized crystal, camera 3 feet away."
12. **Overlong prompt for a 2s shot** — 8 focused lines beat 30 rambling ones.
13. **Higgsfield leftovers** — `@material[name]` / "paste into Seedance on Higgsfield" = 本步失败。改 `<<<image_n>>>`。
14. **BGM in the clip prompt** — orchestral swell / scored music → delete; end with `no background music`.
