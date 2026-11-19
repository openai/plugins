import path from "node:path";

export function additionalContextFlags(paths = []) {
  if (!Array.isArray(paths)) throw new Error("additionalContextPaths must be an array.");
  return paths.map((value) => {
    const absolute = path.resolve(value);
    const quoted = process.platform === "win32"
      ? `'${absolute.replaceAll("'", "''")}'`
      : `'${absolute.replaceAll("'", "'\\''")}'`;
    return ` --additional-context ${quoted}`;
  }).join("");
}
