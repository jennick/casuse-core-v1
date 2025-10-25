# Restore runbook (Postgres)

## Scenario A: Restore in dezelfde container (one-shot)
1) Plaats het backupbestand (bv. `backups/pgdump-casuse_core-YYYY-mm-dd_hhMMss.sql.gz`) op de host.
2) Stop app-services zodat er geen writes gebeuren:
   ```bash
   docker compose stop core-backend core-frontend
