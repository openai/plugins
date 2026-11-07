const DISTRIBUTIONS = new Set(["unspecified", "private-local", "public"]);

export function normalizeDistribution(value = "unspecified") {
  if (!DISTRIBUTIONS.has(value)) {
    throw new Error("Invalid distribution. Use unspecified, private-local, or public.");
  }
  return value;
}

export function distributionFlag(value) {
  const distribution = normalizeDistribution(value);
  return distribution === "unspecified" ? "" : ` --distribution ${distribution}`;
}
