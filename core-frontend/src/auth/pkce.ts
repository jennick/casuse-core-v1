export async function sha256(plain: string) {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return window.crypto.subtle.digest('SHA-256', data);
}

export function base64url(buffer: ArrayBuffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export async function pkcePair() {
  const verifier = [...crypto.getRandomValues(new Uint8Array(32))].map(x => ('0' + x.toString(16)).slice(-2)).join('');
  const challenge = base64url(await sha256(verifier));
  return { verifier, challenge };
}
