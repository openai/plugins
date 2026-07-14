# FigJam Source

Load the Figma FigJam skill and inspect the exact node with `get_figjam`. FigJam has one implicit page and no Design-style Layers panel.

1. Open the exact `/board/` node deep link.
2. Select the node on the FigJam canvas through its accessible canvas object or a coordinate grounded in a fresh screenshot.
3. Confirm the URL node ID and visible selection bounds before OS-level Copy.
4. Use the normal host pasteboard validation and paste watchdog.

When pasting into a Design file, node types may convert. For image-filled FigJam rectangles, require matching dimensions, image content, crop, corner geometry, and visual metrics rather than the same editor-specific node type. For stickies, shapes, connectors, or widgets, report any conversion explicitly and fail if editability or visible relationships are lost.
