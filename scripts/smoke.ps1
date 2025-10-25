param(
  [string]$BaseUrl = "https://core.127.0.0.1.nip.io:10443"
)

function Test-Endpoint {
  param([string]$Url, [int]$Expect = 200)
  Write-Host "-> GET $Url"
  try {
    $resp = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -SkipCertificateCheck
    if ($resp.StatusCode -ne $Expect) { throw "Expected $Expect, got $($resp.StatusCode)" }
  } catch {
    Write-Error "FAIL: $Url ($_)"
    exit 1
  }
}

Write-Host "=== Smoke test against $BaseUrl ==="
Test-Endpoint "$BaseUrl/" 200
try { Test-Endpoint "$BaseUrl/healthz" 200 } catch { 
  try { Test-Endpoint "$BaseUrl/api/healthz" 200 } catch {}
}
try { Test-Endpoint "$BaseUrl/docs" 200 } catch {}

Write-Host "OK: smoke tests passed."
