# README — Extras commands

Gebruik in PR/issue comments (via `.github/workflows/agent-extras-router.yml`):

OpenAPI & clients
- `/agent openapi diff`
- `/agent client regen`
- `/agent contract test`

Database
- `/agent db plan`
- `/agent db shadow-migrate`
- `/agent db index suggest users.email`

Security & privacy
- `/agent sec scan`
- `/agent sec headers`
- `/agent pii lint`

Release
- `/agent release gate v1.3.0`
- `/agent version bump patch|minor|major`
- `/agent changelog synth`

Traefik & routing
- `/agent traefik verify`
- `/agent traefik plan`

Frontend
- `/agent ui audit`
- `/agent ui e2e smoke`

Performance & kosten
- `/agent perf profile`
- `/agent docker diet`
- `/agent ci speedup`

Docs & runbooks
- `/agent docs update`
- `/agent runbook gen auth-timeout`

Ops/stabiliteit
- `/agent chaos lite`
- `/agent rate-limit verify`
- `/agent retry policy`

Alle tasks zijn stubs die veilig slagen met JSON-uitvoer; breid ze naar wens uit.
