const AUTH_BASE = '/auth';

export async function authorize(clientId: string, redirectUri: string, codeChallenge: string, state: string) {
  const qs = new URLSearchParams({
    response_type: 'code',
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: 'openid profile email',
    state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256'
  });
  window.location.href = `${AUTH_BASE}/authorize?${qs.toString()}`;
}

export async function exchangeCode(clientId: string, code: string, verifier: string, redirectUri: string) {
  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    code,
    redirect_uri: redirectUri,
    client_id: clientId,
    code_verifier: verifier
  });
  const res = await fetch('/auth/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
  if (!res.ok) throw new Error('token_exchange_failed');
  return res.json();
}

export async function refreshToken(clientId: string, refreshToken: string) {
  const body = new URLSearchParams({ grant_type: 'refresh_token', client_id: clientId, refresh_token: refreshToken });
  const res = await fetch('/auth/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
  if (!res.ok) throw new Error('refresh_failed');
  return res.json();
}
