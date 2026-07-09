/**
 * cleanupOrphans
 *
 * Finds and removes all Figma nodes (pages, frames, components, variables,
 * and variable collections) that were tagged with the given `dsb_run_id`
 * by a previous build run. This is safe cleanup: it uses plugin data tags,
 * never name-prefix matching, so it cannot accidentally delete user-owned nodes.
 *
 * Use this when a build run fails mid-way and you need to reset to a clean
 * slate before retrying. The function traverses the entire document looking
 * for `dsb_run_id` plugin data matching `runId`.
 *
 * Variables and variable collections are handled separately (they are not
 * scene nodes and cannot be discovered via node traversal).
 *
 * @param {string} runId - The dsb_run_id value to match (e.g. "ds-build-2024-001").
 * @returns {Promise<{
 *   removedCount: number,
 *   removedIds: string[]
 * }>}
 */
async function cleanupOrphans(runId) {
  if (!runId) {
    throw new Error('cleanupOrphans: runId is required.')
  }

  const removedIds = []
  const originalPage = figma.currentPage

  // --- Remove tagged scene nodes (pages, frames, components, etc.) ---
  // Collect pages to remove (can't remove during iteration)
  const pagesToRemove = []

  for (const page of figma.root.children) {
    if (page.getPluginData('dsb_run_id') === runId) {
      pagesToRemove.push(page)
      continue
    }

    // Traverse all nodes on this page
    await figma.setCurrentPageAsync(page)

    // Use the pluginData index to find candidates, then keep only those whose
    // run_id matches. Much faster than findAll + getPluginData on every node.
    const candidates = page.findAllWithCriteria({
      pluginData: { keys: ['dsb_run_id'] },
    })
    const tagged = candidates.filter((node) => node.getPluginData('dsb_run_id') === runId)
    // Drop descendants of already-collected nodes (removing the parent removes
    // its children, so we only need the topmost match in each chain).
    const taggedSet = new Set(tagged)
    const nodesToRemove = tagged.filter((node) => {
      let p = node.parent
      while (p) {
        if (taggedSet.has(p)) return false
        p = p.parent
      }
      return true
    })

    // Remove deepest nodes first (children before parents) to avoid
    // "parent no longer exists" errors
    const sorted = nodesToRemove.sort((a, b) => {
      // Sort by depth descending: deeper nodes first
      return getDepth(b) - getDepth(a)
    })

    for (const node of sorted) {
      if (node && node.parent) {
        removedIds.push(node.id)
        node.remove()
      }
    }
  }

  // Remove tagged pages last
  for (const page of pagesToRemove) {
    // Cannot remove the last page in the document
    if (figma.root.children.length <= 1) {
      break
    }
    removedIds.push(page.id)
    page.remove()
  }

  // --- Remove tagged variables ---
  const allVariables = await figma.variables.getLocalVariablesAsync()
  for (const variable of allVariables) {
    if (variable.getPluginData('dsb_run_id') === runId) {
      removedIds.push(variable.id)
      variable.remove()
    }
  }

  // --- Remove tagged variable collections ---
  // Must be done after variables are removed
  const allCollections = await figma.variables.getLocalVariableCollectionsAsync()
  for (const collection of allCollections) {
    if (collection.getPluginData('dsb_run_id') === runId) {
      removedIds.push(collection.id)
      collection.remove()
    }
  }

  // Restore original page (if it still exists)
  try {
    await figma.setCurrentPageAsync(originalPage)
  } catch (_) {
    // Original page was removed — switch to first available page
    if (figma.root.children.length > 0) {
      await figma.setCurrentPageAsync(figma.root.children[0])
    }
  }

  return {
    removedCount: removedIds.length,
    removedIds,
  }
}

/**
 * Returns the depth of a node in the document tree.
 * Root children (pages) have depth 1; their children have depth 2; etc.
 *
 * @param {BaseNode} node
 * @returns {number}
 */
function getDepth(node) {
  let depth = 0
  let current = node
  while (current.parent) {
    depth++
    current = current.parent
  }
  return depth
}
