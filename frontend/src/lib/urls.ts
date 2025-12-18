export function normalizeUrl(input: string): string {
  const trimmed = input.trim();
  if (!trimmed) return trimmed;

  // If user typed "example.com", add https://
  const hasScheme = /^https?:\/\//i.test(trimmed);
  const candidate = hasScheme ? trimmed : `https://${trimmed}`;

  // Validate via URL parser
  // This also rejects spaces, invalid chars, etc.
  const u = new URL(candidate);

  // Basic host check
  if (!u.hostname || u.hostname.includes(" ")) {
    throw new Error("Invalid URL");
  }

  return u.toString();
}

export function isProbablyUrl(input: string): boolean {
  try {
    normalizeUrl(input);
    return true;
  } catch {
    return false;
  }
}