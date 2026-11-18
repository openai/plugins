# Reconstruct a difficult visual system

This page continues [rebuild](rebuild.md) for openmotion-recreate. Read it before authoring a passage that has any of the following: dense multi-shot work split into units for coordinated integration; an unfamiliar visual mechanism, such as camera travel over a surface, a changing silhouette, content flowing inside a fixed boundary, repeated marks or particles, a scene breaking apart or reforming, or localized flashes and distortion; or movement whose rebuilt output still differs from the reference after a repair. Passages that the rebuild steps already reproduce do not need it.

## Plan shot and action units

For a dense multi-shot film, organize reconstruction into locally reviewable units near shot or action boundaries. Keep coupled actions together, and include neighboring reference frames so an entrance or exit can cross a unit boundary. Choose unit lengths from the action and dependencies. A unit can contain several fast cuts or one continuous move.

Keep independent shots with different visual mechanisms as distinct units, including when they will share one final source module. When units outnumber available worker slots, queue the remaining units and reuse workers after their current unit has been inspected. Return the source and local comparison for each unit so the coordinator can resolve its visible differences before assembling a larger passage.

Use separate workers for independent units when the host supports delegation and the task authorizes it. A single Agent follows the same local process sequentially. Keep one coordinator responsible for the root timeline, shared resources and soundtrack. Give each worker disjoint source files. Save integrated changes through the existing revision-protected project workflow.

Make the unit brief concrete enough to execute. Supply the following information in working notes or the worker task.

| Input | What the maker needs |
|---|---|
| Requested result | The user's content, changes, duration and editable deliverable, with any locked decisions |
| Reference interval | Local reference path, fps, dimensions, source start/end frames and neighboring action context |
| Available inputs | Supplied assets, reusable source and known limitations, plus visible discrepancies already established by comparison |
| Ownership | Which objects, text, transient effects and files belong to this unit, and which are shared |
| Integration | Coordinate space, global-to-local time mapping, asset paths, entry points and shared typography |
| Return | Editable source, asset mapping, timed observations, actual local output comparisons and remaining differences |

For each independent visual mechanism, keep a compact entry in the existing unit notes identifying its source observations, defining form and surrounding relationships, chosen material/geometry, current local comparison and next repair. Compare the first usable reconstruction with the reference at a clear pose and a state that challenges that choice, including the surrounding scene. Use the result to decide whether to refine the controls or revise the material, geometry or isolation boundary before extending the mechanism. A changed defining form or removed surrounding structure belongs in that decision even when movement and appearance measurements pass. Keep separate entries when one worker or source module handles several mechanisms. Reread the relevant entry when resuming or switching work and continue its recorded next action. Carry unresolved differences and the compared source/output identities into integration.

Keep reused implementation and newly reconstructed work identifiable. Recheck a reused object at every new appearance, including a different scale, camera, occluder or text state. Respect the supplied-input boundary when the task calls for an independent experiment.

## Turn observations into driving data

For an unfamiliar or inaccurate unit, describe its defining form and action, then follow recognizable features through the reference. Keep a compact record of source frame/time, feature or object, screen position, size, orientation, pose and visibility. Use relative distances and occlusion to distinguish common camera movement, part movement and deformation. Mark uncertain observations, including measurements contaminated by overlapping text or objects.

Cover the features responsible for the passage's motion, including changes inside otherwise stationary objects. Compare internal feature travel with the enclosing boundary at corresponding times. Keep content replacement, scrolling, geometric displacement and brightness variation distinguishable. Retain observed holds and stationary relationships. Resolve ambiguous movement with short consecutive-frame sequences or reliable tracking, and carry occlusion or tracking uncertainty into the model choice.

Fast or repetitive content can match a neighboring repeat across a sparse frame gap and underestimate travel. Begin with adjacent decoded frames, follow recognizable features and check the accumulated path before fitting a longer interval. Keep displacement units, coordinate scale and elapsed time explicit when deriving velocity. Inspect the tracked feature's own region separately from nearby stationary structure.

Use the installation's Node executable for these commands. Complete ZIPs provide `runtime/node/bin/node` on macOS and `runtime/node/node.exe` on Windows. The managed entry works from source, installed bundles and flat Skills using their installation metadata. First use downloads verified platform assets into the installation cache. Complete platform ZIPs include those assets for offline preparation. Repeated use reuses the completed environment. Use `node "<skill directory>/scripts/vision-tools.mjs" prepare` to prepare or retry explicitly. For additional source analysis/material scripts, use the same entry with `python <script.py> [arguments]`. User-installed Python and uv are unnecessary. Vision helpers support macOS 13+ arm64 and Windows 11+ x64. Respect host execution/network permissions and report preparation failures instead of silently claiming measurements.

Measure source travel before assigning velocities for each trackable local region. The optional motion helper accepts a reference alone for observations before authoring. Invoke it through `scripts/vision-tools.mjs`, which prepares the installation-managed, pinned Python, NumPy and headless OpenCV environment. Choose a continuous interval with recognizable features and inspect its samples and point pairs.

```sh
node "<skill directory>/scripts/vision-tools.mjs" measure reference.mp4 --start <seconds> --end <seconds> --roi <x,y,width,height> --out source-motion.json
```

The source-only report has `comparisonPerformed: false` and `output: null`. Fit controls from the observed displacement and elapsed time in the declared coordinate scale. After rendering, supply both videos to compare the same region. Repeat this for the independently moving regions in the inventory, preserving unresolved observations explicitly.

Convert those observations into timed controls the renderer actually reads. Keep the connection from observation to model parameter and source function inspectable. Depending on the passage, the useful record may be landmark coordinates, per-part keyframes, camera matrices, shape states, correspondence fields or per-line text bounds. Record direction/speed changes, extreme poses, fastest travel and settling. Add observations where interpolation remains uncertain.

| Observed change | An editable way to encode it | Output that challenges the model |
|---|---|---|
| Camera travel over a surface | Match stable landmarks across views, fit transforms and interpolate the camera over a spatial material | Motion extremes, perspective, registration residuals and newly revealed areas |
| Parts moving relative to one another | Shared parent/camera transform plus part-local paths and occlusion order | Relative distances and overlap at intermediate times |
| Content flowing inside a stable boundary | Local content coordinates, a clipped material and timed scroll or content-state controls | Boundary position, internal feature travel, update cadence and newly exposed material |
| Changing silhouette or surface | Timed shape states, skeleton or mesh with correspondence between recognizable parts | Intermediate pose, volume, holes and changing visibility |
| Text assembling or leaving | Per-line or per-glyph reveal, travel, spacing, compression, opacity and blur curves | First visibility, readable hold, fastest expansion and final disappearance |
| Streaks, flash or scan distortion | Separate time envelopes with observed direction, extent, affected layers and recovery | Frames immediately before, during and after the event in the complete layer stack |

Match the temporal behavior of content inside a fixed boundary. Continuous scrolling needs local-coordinate motion or aligned field interpolation between observations. Discrete refreshes need their observed update cadence. Check between material samples for artificial holds, jumps or double text.

A changing silhouette needs controls for its internal change. If one spatial sample plus a global transform fits the endpoints but misses an intermediate pose, add a constraint at that time and revise the representation that failed. Connect the same recognizable parts through time. Correct unreliable correspondence around occlusion, repaired text or disappearing features by changing anchors, masks, state grouping or the model. Check estimated motion against the visible travel before limiting it.

For a form made of repeated marks or particles, separate a clean shape or brightness field from the mark renderer. The following construction is useful when the reference exposes a recoverable underlying form.

1. Use distinguishable colour, brightness or edges to derive an occupancy or brightness field for each observed state. Choose observations from the changing form and group continuous states on each side of a cut.
2. Mask independently changing overlays and inspect paired source/cleaned fields. Check whether the mask removed bright subject details, a hole or a thin appendage. Repair the affected region using available observations or revise the mask, keeping uncertain reconstruction visible in the notes.
3. Encode the cleaned fields in common coordinates. For a tonal form, contours at several brightness levels can preserve its interior and holes. A skeleton, control mesh or other shape model may better fit the observed structure. Save the source time with each state and declare coordinate and displacement units.
4. Establish corresponding parts between neighboring states in each continuous group, using reliable landmarks, manual anchors or available tracking/flow methods. Check the correspondence on the cleaned fields, especially at repaired or occluded regions.
5. At query time, select the surrounding states and warp their fields toward that time using the correspondence. Blend aligned values, then sample the resulting field to drive mark placement, area or opacity. Keep material, deterministic variation, text and transient effects separately addressable. Inspect the field and styled output at intermediate times, and add a state or revise correspondence where the form fails.

Calibrate the field-to-mark transfer in the rendered picture. A field sampled from already dim, sparse marks can lose brightness and coverage again when used as mark opacity or area. Compare the cleaned field, isolated marks and complete composite at matched times. Adjust field strength, mark coverage and material separately while preserving thin features, holes and the observed background. Inspect clean held states as well as blur-heavy movement.

Choose state count, extraction method, correspondence and control resolution from the reference and the host's available tools.

When a scene breaks apart or reforms, follow recognizable regions from the intact scene into the transition. Record when each region releases, what texture or shape remains visible, its travel direction and how the intact material disappears. Derive fragments or marks from the participating content and keep their initial coordinates consistent with its last intact state. Choose fragment shape, grouping, velocity and lifetime from consecutive reference frames. When individual marks cannot be tracked reliably, model the evolving spatial density, brightness and directional streaks with timed fields and supported correspondence. Reliable surviving tracks can omit fast, blurred or disappearing features. Check the evolving spatial distribution and streak geometry alongside the tracked trajectories. Compare release, peak spread and decay against the intact-to-transition handoff in the complete composite.

Calibrate transition material at its first visible change before extending the simulation. In a matched crop at delivery scale, compare the typical bright mark, largest coherent hole or fragment, remaining silhouette and edge softness. Keep source-sampling pitch, release-group size and visible fragment size separately controllable. A coarse sampling grid can introduce square holes and large tiles even when later particle travel matches. Choose their scales from the source observations and inspect the earliest altered frames after compositing. Check both residual source structure and released marks through peak spread and decay.

For spatially localized flashes, tearing or distortion, record the affected bounds and layers through each pulse. Fit its onset, peak and recovery from consecutive source frames, including clear intervals between pulses. Give local bands or regions their own displacement, exposure and visibility controls when their behavior differs. Inspect these bounds in the complete composite so an added glow or repeated whole object cannot conceal a mismatched local effect.

For camera movement or surface deformation, prepare enough spatial material to cover the revealed area. Align useful views of the same structure when available. Check overlap for doubled edges and check the sampling boundary for gaps or stretched pixels. If blending imperfectly aligned views produces double structure, select a reliable source for that region and use other views to fill uncovered areas, or adjust seams and visible regions. Recheck intermediate and extreme camera positions. Use a more suitable projection, layers or geometry when one plane cannot preserve the observed relationships. Preserve weakly supported intervals in the review notes.

Fit camera travel from stable scene landmarks at corresponding times. For a textured plane, the bundled registration helper can measure anchor-to-frame homographies. Choose times within one continuous shot and exclude independently changing overlays. Use the managed entry below, with the directory containing this Skill's `SKILL.md`.

```sh
node "<skill directory>/scripts/vision-tools.mjs" register reference.mp4 --anchor <anchor seconds> --times <comma-separated seconds> --out camera-observations.json
```

Optional `--roi x,y,width,height` and repeatable `--exclude x,y,width,height` use original pixels. The report records decoded timestamps, full-frame pixel matrices, inlier point pairs, residuals and spatial support. Inspect that support across the intended plane and compare projected landmarks in intermediate output. Unresolved samples return a failing exit code and carry their reason. Resolve the cut, mask, observation or representation before using those samples. Apply supported matrices to the renderer in the declared coordinates, and verify material coverage throughout the camera path.

## Prepare material in its actual use states

Verify the chosen material and geometry at a clear representative pose at their eventual screen scale. Preserve characteristic edge structure, texture, internal geometry and layering. When a procedural approximation loses those features, choose a supported local material or a more faithful editable representation, then recheck its motion.

Look through the available reference for a clear, unobstructed view of the same object before repairing an occluded one. Compare pose and lighting before using that view. When removing text or overlays, inspect the cleaned shape before stylizing it. Check bright subject details, holes, anti-aliased glyph edges, shadows, underlines and restoration seams. Use the background's structure to choose the repair method.

When isolating an object, preserve the stationary structures crossing or surrounding it. Fit masks to the actual shape and depth ordering. Register other useful views to recover newly exposed material before repairing a large region. Check the reassembled scene at a matched time, including the background, object attachments and overlapping foreground. Correct shifted perspective, erased structure or patch boundaries before extending the animation.

Inspect the material when the covering text or object has left, after requested content changes, and in every reused view. Follow the mask or material back to its source when a ghost moves with the subject. Preserve independently changing elements as separate source controls.

## Validate and repair the local implementation

Use the pinned seekable preview or targeted native captures to iterate on the actual unit source. Compare reference and output at equal scale and corresponding times. Include observed states, intermediate times, extreme poses, the fastest displacement and entry/exit boundaries. Read back feature positions, size ratios, angles, relative distances or visible widths from the output using the same method as the reference. Review the timed sequence to assess acceleration, holds, reversals and recovery.

For each defining change identified above, locate the source control and compare its actual effect in the output. Check both moving features and their stationary anchors. If a changing region was flattened into a fixed crop, recover its missing local control before refining its appearance. If neighboring states overlap as double images, align or deform their corresponding features before blending. Recheck direction, distance, cadence and disappearance through the affected interval.

An animated source parameter can be hidden by an opaque material, a clip, an overlay or a later paint operation. Compare the fully composited output region before accepting that control. For trackable local movement, use the bundled motion helper through the managed entry below. It follows adjacent decoded frames through continuous reference/output intervals. Reuse it for this check before writing another tracker, and inspect its correspondence and uncertainty.

```sh
node "<skill directory>/scripts/vision-tools.mjs" measure reference.mp4 output.mp4 --start <seconds> --end <seconds> --roi <x,y,width,height> --out visible-motion.json
```

Choose a region belonging to the moving feature and measure its stationary anchor separately. Coordinates use each video's original pixels. Supply `--output-roi` when the output needs different coordinates. The report includes decoded times, displacement samples, travel span, retained features and point pairs. A possible-suppression warning flags travel below half the reference span once reference movement exceeds the helper's jitter floor. This warning or unresolved tracking returns a failing exit code. Inspect the actual travel values, tracked features and layer stack before deciding the cause. Small motion, changing content, occlusion and mixed movement can invalidate the comparison. Timing, direction and semantic fidelity require visual review, including when the diagnostic returns successfully.

For the most consequential difference, name the failing feature and interval, locate its source control and repair that mechanism. An early unreadable title may need different opacity, travel and blur durations. A double contour may need corrected correspondence or material alignment. Reinspect the same failed moment and neighboring states after changing it. Keep the measured and visually estimated controls distinguishable.

Calibrate light, density, edges and material on the established motion. For exposure sampling, check preserved brightness and high-frequency marks for repeated copies or comb-like gaps. Adjust temporal sampling or directional integration when needed, and match the observed streak direction, extent and clear hold. Keep frame-specific flash peaks and recovery explicit. Inspect later text and post-processing layers for marks that alter a flash after it is drawn.

Return the working source and actual comparison evidence with the brief's time range, asset identities, shared dependencies and remaining differences. Keep generation scripts consistent with the final corrected source when they are part of the handoff. Use local captures for targeted fixes, then verify the final integrated export as [check and deliver](verify.md) describes.

Check every planned unit against its defining action and brief transient events before marking it ready for integration. When an independent visual reviewer is available and authorized, give them the reference and actual local output with the requested changes. Keep the review focused on visible differences. Feed concrete failed intervals back into the unit's source repair and recheck them in the integrated film.

## Integrate the inspected units

Import shared media once and connect the returned paths. Preserve each unit's global-to-local clock and coordinate transforms. A background ownership boundary can differ from a foreground element's first visible frame. Coordinate overlaps explicitly so an outgoing title and incoming logo can coexist as the reference shows.

Review the integrated project across joins and repeated appearances, including pose, direction, speed, exposure, text and layer ordering. Capture the final composite for short events. Recheck every affected use after replacing a shared asset or renderer, and bind the evidence to that source or export version. Play the integrated sequence at normal speed and check the single soundtrack through the existing delivery workflow.
