/**
 * Generates a unique ID compatible with all browsers and contexts
 * Falls back to a polyfill if crypto.randomUUID is not available
 */
export function generateUUID(): string {
  // Use native crypto.randomUUID if available (HTTPS/localhost)
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback for HTTP contexts (like S3 static websites)
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
