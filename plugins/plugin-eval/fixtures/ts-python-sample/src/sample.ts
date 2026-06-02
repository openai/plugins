export function choosePath(items: string[], includeArchived: boolean, preferFast: boolean): string[] {
  const next: string[] = [];
  for (const item of items) {
    if (!item) {
      continue;
    }
    if (includeArchived || !item.startsWith("archived:")) {
      if (preferFast && item.includes("fast")) {
        next.push(item.toUpperCase());
      } else if (!preferFast && item.includes("slow")) {
        next.push(item.toLowerCase());
      } else if (item.length > 3) {
        next.push(item);
      }
    }
  }
  return next;
}
