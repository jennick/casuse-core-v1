param(
  [string]$CertDir = "$(Resolve-Path ../traefik/certs)",
  [string]$CommonName = "core.127.0.0.1.nip.io"
)

Write-Host "=> Cert dir: $CertDir"
New-Item -ItemType Directory -Force -Path $CertDir | Out-Null

$crt = Join-Path $CertDir "core.local.crt"
$key = Join-Path $CertDir "core.local.key"

# Vereist openssl in PATH (Git for Windows levert dit vaak mee)
$conf = @"
[req]
default_bits = 2048
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
C = BE
ST = Oost-Vlaanderen
L = LocalDev
O = Casuse
CN = $CommonName

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $CommonName
DNS.2 = localhost
IP.1 = 127.0.0.1
"@

$confPath = Join-Path $CertDir "openssl.cnf"
$conf | Out-File -Encoding ascii $confPath

Write-Host "=> Generating self-signed certificate for $CommonName"
& openssl req -x509 -nodes -days 825 -newkey rsa:2048 `
  -keyout $key -out $crt -config $confPath

Write-Host "=> Done:"
Write-Host "   CRT: $crt"
Write-Host "   KEY: $key"
