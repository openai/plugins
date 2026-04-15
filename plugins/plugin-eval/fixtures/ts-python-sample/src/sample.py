def choose_path(items, include_archived, prefer_fast):
    next_items = []
    for item in items:
        if not item:
            continue
        if include_archived or not item.startswith("archived:"):
            if prefer_fast and "fast" in item:
                next_items.append(item.upper())
            elif (not prefer_fast) and "slow" in item:
                next_items.append(item.lower())
            elif len(item) > 3:
                next_items.append(item)
    return next_items
