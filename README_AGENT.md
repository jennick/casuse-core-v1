# Casuse-Core AI Agent — All-in-One

Dit pakket bevat **alles** om de agent direct te gebruiken:
- Kernworkflows: PR-checks, audit, commands, implement (feature-scaffold).
- “Continue until green”: kleine auto-fixes + her-run.
- Auto-merge op label `agent:auto-merge` (met branch protection).
- Extras-router met veel extra commands (OpenAPI/db/security/ui/perf/docs/ops).
- Policies, templates, tasks, issue-template en CI compose.

## Installatie
1. Pak uit in de **root** van je `casuse-core` repo.
2. Commit & push een branch → open een PR.
3. Gebruik comments in een PR/issue:
   - **/agent implement** + YAML-spec (zie issue template)
   - **/agent continue**
   - **/agent audit** · **/agent smoke** · **/agent fix**
   - Plus alle **extras** commands uit `README_AGENT_EXTRAS.md`.

## Voorwaarden
- Backend: `GET /healthz` (200), `/token` (POST; GET=405).
- Poorten: backend 9000, frontend 8200 (aanpasbaar in `agent/policies/ports.yml`).
- GitHub Actions aan; `GITHUB_TOKEN` is voldoende.

— gegenereerd 2025-10-26T05:52:06.770419Z
