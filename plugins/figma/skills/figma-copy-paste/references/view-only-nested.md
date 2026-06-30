# View-only Nested Layer Fallback

Use only when a requested nested layer cannot produce native `figmeta`, but a containing top-level frame can.

1. Record the target's hierarchy path, sibling indexes, name, type, dimensions, metadata counts, variables, and screenshot.
2. Select the nearest complete top-level containing frame and transfer it natively using the normal clipboard procedure.
3. In the editable destination, locate the requested descendant by the recorded hierarchy fingerprint.
4. Clone that descendant within the destination file and append the clone to the page. This is a native same-file clone, not reconstruction.
5. Remove the temporary containing frame.
6. Verify the retained clone directly against the original nested source node.

Abort and undo if the descendant fingerprint is not unique or the temporary top-level frame cannot be transferred natively.
