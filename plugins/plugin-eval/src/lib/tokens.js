export function estimateTokenCount(text) {
  if (!text) {
    return 0;
  }
  return Math.ceil(text.length / 4);
}

export function sumTokenCounts(items) {
  return items.reduce((total, item) => total + item.tokens, 0);
}
