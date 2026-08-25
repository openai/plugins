---
name: canva-resize-for-social-media
description: Resize a Canva design into multiple social media formats (Facebook post, Facebook story, Instagram post, Instagram story, LinkedIn post). Use this skill when users want to resize Canva designs specifically for multiple social media platforms in one operation, rather than resizing to a single format manually.
---

# Canva Resize for Social Media

Automatically resize a single Canva design into multiple social media formats.

## Overview

This skill enables rapid multi-platform content distribution by taking a single Canva design and creating optimized versions for:
- Facebook post
- Facebook story
- Instagram post
- Instagram story
- LinkedIn post

All resized versions are provided with Canva edit links so users can further edit or download them directly from Canva.

## Workflow

### Step 1: Identify the Source Design

Determine which Canva design the user wants to resize. This can be provided in three ways:

1. **Direct design ID**: User provides a design ID (starts with "D")
   - Example: "resize design DABcd1234ef for all social media"
   - Use the design ID directly with `get-design` tool to retrieve design information
   
2. **Direct design URL**: User provides a Canva design link
   - Example: "resize https://www.canva.com/design/DABcd1234ef/... for all social media"
   - Extract the design ID from the URL (the part after `/design/` and before the next `/` or query parameter)
   - Use the extracted design ID with `get-design` tool
   
3. **Search by design name**: Use `search-designs` tool with the design name as the query
   - Example: "resize my Demo Brand Template: Brix&Hart Flyer design for all social media"
   - Use the exact name/phrase the user provides as the search query
   - If multiple matches are found, present options and ask the user to select one
   
4. **Current context**: If the user just created or edited a design in the conversation, use that design ID

**Implementation note**: When searching by name, pass the design name directly to `search-designs` as the query parameter. The tool will find the best match based on the design title.

### Step 2: Retrieve Source Design Information

Use the `get-design` tool with the design ID to:
- Confirm the design exists and is accessible
- Get the design title (for naming resized versions)
- Verify design type compatibility

### Step 3: Ask Which Platforms and Formats

Present the available formats and ask which ones the user wants:

```
Which platforms and formats would you like to resize for?

- Facebook post (1200×630)
- Facebook story (1080×1920)
- Instagram post (1080×1080)
- Instagram story (1080×1920)
- LinkedIn post (1200×627)
```

If the user says "all" or "all social media", use all five. Otherwise, only resize for the ones they select.

### Step 4: Resize to Selected Formats

Execute the resize operations **in parallel** by calling the `resize-design` tool once for each selected format. Use these exact specifications:

**Available formats and dimensions:**

1. **Facebook Post**: 1200 × 630 pixels (custom)
   ```
   design_type: { type: "custom", width: 1200, height: 630 }
   ```

2. **Facebook Story**: 1080 × 1920 pixels (custom)
   ```
   design_type: { type: "custom", width: 1080, height: 1920 }
   ```

3. **Instagram Post**: 1080 × 1080 pixels (custom)
   ```
   design_type: { type: "custom", width: 1080, height: 1080 }
   ```

4. **Instagram Story**: 1080 × 1920 pixels (custom)
   ```
   design_type: { type: "custom", width: 1080, height: 1920 }
   ```

5. **LinkedIn Post**: 1200 × 627 pixels (custom)
   ```
   design_type: { type: "custom", width: 1200, height: 627 }
   ```

**Note**: Facebook Story and Instagram Story have identical dimensions. Create both versions but inform the user they're the same size.

**Error handling**: If a resize operation fails, continue with remaining formats and report which formats succeeded and which failed at the end.

### Step 5: Present Results with Edit Links

**Present comprehensive results to the user:**

Provide the user with a summary including:

1. **Summary**: Confirm which formats were created successfully
2. **Design edit links**: Canva editor URLs for each resized design so users can make further edits or download directly from Canva
3. **Note about duplicates**: Mention that Facebook Story and Instagram Story have identical dimensions

**Presentation format example:**
```
✅ Successfully resized your design for all social media platforms!

Edit Links:

**Facebook Post** (1200×630)
- [Edit in Canva](edit_url)

**Facebook Story** (1080×1920)
- [Edit in Canva](edit_url)

**Instagram Post** (1080×1080)
- [Edit in Canva](edit_url)

**Instagram Story** (1080×1920)
- [Edit in Canva](edit_url)

**LinkedIn Post** (1200×627)
- [Edit in Canva](edit_url)

Note: Facebook Story and Instagram Story use the same dimensions (1080×1920).
```

**Implementation details**:
- Design edit links come from the `resize-design` tool response (use the `urls.edit_url` field from each resized design)
- Present links as clickable URLs, not just plain text
- Organize by platform for easy scanning

## Key Implementation Notes

- **Compatibility**: Check if `resize-design` is available in the current MCP tools. If not, inform the user that this skill requires the Canva MCP resize tool in the current host
- **Parallel execution**: Resize operations should be performed in parallel for efficiency
- **Consistent naming**: Use the source design title with platform suffix for resized designs
- **Error resilience**: If any operation fails, complete the remaining operations and clearly report what succeeded/failed
- **User confirmation**: Do not require user approval between steps - execute the full workflow automatically unless errors occur
- **Format accuracy**: Always use the exact pixel dimensions specified above for each platform
