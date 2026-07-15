# Backup Verification Procedure

## Document Control

| Field | Value |
|---|---|
| Document ID | DVO-BKP-001 |
| Version | 1.0.0 |
| Status | Approved |
| Classification | Internal — Operations |
| Owner | Developer |
| Last Updated | 2026-07-11 |
| Next Review | 2026-10-11 |
| Review Cycle | Quarterly |
| Approving Authority | Developer |
| Location | `docs/devops/backup-verification-procedure.md` |
| Supporting Documents | `docs/operations/41_DisasterRecovery.md`, `docs/devops/26_Deployment.md` |

---

## 1. Purpose

This document defines the procedure for verifying backups of the Second Brain OS system. A backup that cannot be restored is not a backup. Regular verification ensures that when disaster strikes, recovery procedures work as expected and data loss is minimized.

## 2. Scope

This procedure covers verification of:

| Asset | Backup Method | Verification Required |
|---|---|---|
| PostgreSQL database (Supabase) | Automated daily + pg_dump | Yes — full restore test |
| Environment variables | GPG-encrypted file | Yes — decrypt test |
| Source code | GitHub repository | Yes — clone test |
| AI prompt files | Git-tracked in `prompts/` | Yes — file existence check |
| Application configuration | Git-tracked | Yes — diff check |
| Chat history exports | JSON export | Yes — parse validation |

## 3. What Is Backed Up

### 3.1 Database

- **Method:** `pg_dump` via scheduled script or Supabase automated daily backup
- **Schedule:** Daily (automated Supabase backup) + manual pg_dump weekly
- **Location:** Local `backups/` directory + Supabase cloud retention
- **Retention:** 30 days local, Supabase retention per plan
- **File format:** SQL dump (plain text)
- **Naming:** `sb_YYYYMMDD_HHMMSS.sql`

### 3.2 Environment Variables

- **Method:** GPG encryption (`gpg -c .env.production`)
- **Schedule:** On every change to production environment
- **Location:** `~/.config/secondbrain/.env.production.gpg`
- **Retention:** Permanent (one per version)
- **File format:** GPG-encrypted text

### 3.3 Source Code

- **Method:** `git push` to GitHub
- **Schedule:** Per commit (continuous)
- **Location:** GitHub `main` branch + local clones
- **Retention:** Unlimited (GitHub)

### 3.4 Prompt Files

- **Method:** Git-tracked in `prompts/`
- **Schedule:** Per commit
- **Location:** GitHub repository
- **Retention:** Unlimited (GitHub history)

### 3.5 Chat History

- **Method:** JSON export script
- **Schedule:** Weekly
- **Location:** `backups/chat/`
- **Retention:** 90 days

## 4. Backup Schedule

| Backup | Frequency | Time | Method | Automated |
|---|---|---|---|---|
| Supabase automated backup | Daily | 02:00 UTC | Supabase internal | Yes |
| pg_dump (local) | Weekly | Sunday 03:00 UTC | `scripts/backup_db.py` | Yes (cron) |
| Environment variables | Per change | — | GPG encrypt manually | No |
| Source code | Per commit | — | `git push` | Manual |
| Prompt files | Per commit | — | `git push` | Manual |
| Chat history export | Weekly | Sunday 04:00 UTC | JSON export script | Yes (cron) |
| Backup integrity check | Weekly | Sunday 03:30 UTC | This procedure | Semi-automated |

## 5. Verification Procedure

### 5.1 Weekly Backup Verification (Every Sunday)

Perform the following steps every Sunday after the weekly pg_dump completes:

```
Step 1: Check Last Backup Timestamp
  ├── Action: List backup files with timestamps
  │   ls -lt backups/sb_*.sql | head -10
  ├── Expected: Most recent file is from today or yesterday
  ├── Pass: Most recent backup is < 48 hours old
  └── Fail: If no backup in 48+ hours, investigate cron job

Step 2: Verify Backup Integrity
  ├── Action: Check file size
  │   ls -lh backups/sb_latest.sql
  ├── Expected: File size > 1 MB (for a production database)
  ├── Pass: File size > 1 MB
  └── Fail: If file < 1 MB, backup may be incomplete

  ├── Action: Validate SQL syntax
  │   head -50 backups/sb_latest.sql
  ├── Expected: Starts with valid PostgreSQL commands (CREATE, COPY, etc.)
  ├── Pass: Valid SQL header detected
  └── Fail: Empty file or garbage content → regenerate backup

  ├── Action: Check file line count
  │   wc -l backups/sb_latest.sql
  ├── Expected: At least 1000+ lines for active database
  └── Note: Compare with previous week's count to detect anomalies

Step 3: Verify Checksum
  ├── Action: Compute and record checksum
  │   Get-FileHash backups/sb_latest.sql -Algorithm SHA256
  ├── Expected: Consistent with recorded checksum (if available)
  └── Pass: Checksum matches or no previous checksum to compare

  └── Action: Store checksum for next week
      Get-FileHash backups/sb_latest.sql -Algorithm SHA256 > backups/checksums.txt
```

### 5.2 Monthly Full Restore Test (First Sunday of Month)

```
Step 1: Set Up Test Environment
  ├── Action: Clone database to local PostgreSQL instance
  │   createdb secondbrain_test
  │   psql -d secondbrain_test < backups/sb_latest.sql
  ├── Expected: Restore completes without errors
  ├── Pass: Zero errors in restore output
  └── Fail: Record error count and type

Step 2: Run Smoke Tests
  ├── Action: Check critical tables exist
  │   psql -d secondbrain_test -c "\dt"
  ├── Expected: All production tables present (tasks, habits, goals, etc.)
  └── Fail: Missing tables indicate backup truncation

  ├── Action: Verify row counts
  │   psql -d secondbrain_test -c "
  │     SELECT 'tasks' as t, count(*) FROM tasks
  │     UNION SELECT 'habits', count(*) FROM habits
  │     UNION SELECT 'goals', count(*) FROM goals
  │     UNION SELECT 'habit_logs', count(*) FROM habit_logs;"
  ├── Expected: Row counts are non-zero and reasonable
  └── Fail: Zero rows in critical tables → backup is empty

Step 3: Verify Data Integrity
  ├── Action: Check foreign key relationships
  │   psql -d secondbrain_test -c "
  │     SELECT 'orphan_tasks' as check, count(*) FROM tasks t
  │     LEFT JOIN auth.users u ON t.user_id = u.id
  │     WHERE u.id IS NULL;"
  ├── Expected: Zero orphaned records
  └── Fail: Orphans indicate backup taken during inconsistent state

  ├── Action: Check date ranges
  │   psql -d secondbrain_test -c "
  │     SELECT MIN(created_at) as oldest, MAX(created_at) as newest FROM tasks;"
  ├── Expected: Date range covers expected period
  └── Fail: Unexpected date gap suggests data loss

Step 4: Clean Up
  └── Action: Drop test database
      dropdb secondbrain_test
```

### 5.3 Environment Variables Verification (Monthly)

```
Step 1: Verify encrypted file exists
  ├── Action: Check file existence
  │   test -f ~/.config/secondbrain/.env.production.gpg
  ├── Expected: File exists and is non-empty
  └── Fail: Missing file → create new encrypted backup

Step 2: Test decryption
  ├── Action: Decrypt to stdout
  │   gpg -d ~/.config/secondbrain/.env.production.gpg 2>/dev/null
  ├── Expected: Valid KEY=VALUE pairs output
  └── Fail: Decryption fails → GPG key may be corrupted or missing

Step 3: Verify critical variables present
  ├── Action: Check for required keys
  │   gpg -d ~/.config/secondbrain/.env.production.gpg 2>/dev/null | grep -E "^(SUPABASE_URL|SUPABASE_SERVICE_KEY|CLAUDE_API_KEY|JWT_SECRET)="
  ├── Expected: All 4 critical keys present
  └── Fail: Missing keys → update encrypted backup
```

### 5.4 Source Code Verification (Per Commit)

```
Step 1: Verify remote is accessible
  ├── Action: Test GitHub connectivity
  │   git ls-remote origin HEAD
  ├── Expected: Returns HEAD commit hash
  └── Fail: Network issue or access revoked

Step 2: Verify local clone is up to date
  ├── Action: Check divergence
  │   git fetch origin
  │   git status
  ├── Expected: "Your branch is up to date with 'origin/main'"
  └── Fail: Local and remote diverged → investigate

Step 3: Verify prompt files exist
  ├── Action: List prompt files
  │   ls prompts/agents/*.md prompts/system/*.md prompts/templates/*.md
  ├── Expected: 22 files total (18 agents + 2 system + 2 templates)
  └── Fail: Missing files → restore from git or recent backup
```

## 6. Restoration Step-by-Step

### 6.1 Database Restoration

```bash
# Step 1: Identify the correct backup
ls -lt backups/sb_*.sql | head -5

# Step 2: Verify backup file integrity
wc -l backups/sb_target.sql
head -5 backups/sb_target.sql  # Should show SQL header

# Step 3: Restore to Supabase
psql "$SUPABASE_DB_URL" < backups/sb_target.sql

# Step 4: Verify restoration
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM tasks;"
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM auth.users;"
```

### 6.2 Environment Variables Restoration

```bash
# Step 1: Decrypt the backup
gpg -d ~/.config/secondbrain/.env.production.gpg > .env.production

# Step 2: Verify decryption succeeded
head -5 .env.production

# Step 3: Update platform variables
#   Vercel: Dashboard → Settings → Environment Variables
#   Railway: Dashboard → Variables

# Step 4: Secure cleanup
rm .env.production  # After confirming platform variables are set
```

### 6.3 Source Code Restoration

```bash
# Step 1: Clone from GitHub
git clone https://github.com/org/second-brain-os.git
cd second-brain-os

# Step 2: Restore prompt files
git checkout origin/main -- prompts/

# Step 3: Verify restoration
ls prompts/agents/*.md | wc -l  # Expected: 18
```

## 7. Verification Checklist

Use this checklist for every backup verification cycle:

### Weekly Verification

- [ ] Most recent backup file is < 48 hours old
- [ ] Backup file size > 1 MB
- [ ] SQL header is valid (starts with CREATE/COPY)
- [ ] Line count is reasonable (compare to previous week)
- [ ] SHA256 checksum recorded
- [ ] Encrypted `.env` file exists and is non-empty
- [ ] GitHub remote is accessible
- [ ] Local clone is up to date with `origin/main`
- [ ] All 22 prompt files present

### Monthly Verification (in addition to weekly)

- [ ] Full database restore completed without errors
- [ ] All critical tables present after restore
- [ ] Row counts are non-zero and reasonable
- [ ] Zero orphaned records
- [ ] Date ranges cover expected period
- [ ] GPG decryption of `.env` succeeds
- [ ] All 4 critical env vars present in encrypted file
- [ ] Test database cleaned up after verification

### Quarterly Verification (in addition to monthly)

- [ ] Full DR drill completed (see `docs/operations/41_DisasterRecovery.md` Section 11)
- [ ] Backup to offsite location tested
- [ ] Recovery time measured and recorded
- [ ] RTO/RPO targets reviewed and updated if needed
- [ ] Backup scripts reviewed for needed updates
- [ ] GPG keys checked for expiry

## 8. Troubleshooting Backup Failures

| Symptom | Likely Cause | Solution |
|---|---|---|
| pg_dump fails with "connection refused" | Supabase connection string wrong | Verify `SUPABASE_DB_URL` in environment |
| pg_dump produces empty file | Network timeout or auth failure | Retry with longer timeout: `PGOPTIONS='-c statement_timeout=300000' pg_dump ...` |
| Backup file size is 0 bytes | Script error or disk full | Check disk space, check script logs |
| Restore fails with "relation already exists" | Restoring over existing data | Drop and recreate: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` |
| Restore fails with "permission denied" | Insufficient Supabase privileges | Use service role key (not anon key) |
| GPG decryption fails | Key expired or wrong key | Check `gpg --list-keys` for expiry. Re-encrypt with current key |
| Backup too large (> 1 GB) | Database growth | Split backup: `pg_dump ... | gzip > backup.sql.gz` |
| Missing recent data in backup | Backup taken during active write | Schedule backup during low-activity window |
| Orphaned records in restored data | Backup taken mid-transaction | Use `pg_dump --no-blocks` for consistency |

## 9. Notification Procedure for Failed Backups

### 9.1 Automated Alerts

For scheduled backup jobs (cron), configure the following alert thresholds:

| Condition | Severity | Action |
|---|---|---|
| No backup file in 48 hours | P2 | Manual investigation, trigger immediate backup |
| Backup file size < 1 MB | P2 | Check script, re-run, verify output |
| Backup file size 50% smaller than previous | P3 | Investigate possible data loss or schema change |
| Restore test fails | P1 | Diagnose root cause, attempt second backup |
| GPG decryption fails | P1 | Check GPG key, re-encrypt |

### 9.2 Manual Notification Steps

```
Step 1: Identify failure
  ├── Check backup logs: tail -100 backups/backup.log
  └── Check cron logs: tail -100 /var/log/cron

Step 2: Trigger immediate retry
  ├── Run backup script manually:
  │   python scripts/backup_db.py
  └── Monitor output for errors

Step 3: If retry fails:
  ├── Create GitHub Issue with type: ops, priority: P2
  ├── Document error message and logs
  └── Escalate to next available window for manual recovery

Step 4: After resolution:
  ├── Verify next scheduled backup succeeds
  └── Update backup script if recurring issue
```

## 10. Quarterly Full DR Test Procedure

Execute this procedure on the first Saturday of every quarter.

### 10.1 Pre-Test Preparation

```
 1. Review this document for any needed updates
 2. Verify all backup files exist and are recent
 3. Ensure sufficient free disk space for test restore
 4. Block 2-4 hours of uninterrupted time
 5. Open the DR plan (docs/operations/41_DisasterRecovery.md)
 6. Prepare the DR drill report template (DR plan Section 12)
```

### 10.2 Test Execution

```
Phase 1: Database Backup Verification (30 min)
  ├── Run weekly verification checklist
  ├── Perform full restore to test database
  ├── Run smoke tests and data integrity checks
  └── Record results

Phase 2: Environment Variables Verification (15 min)
  ├── Test GPG decryption
  ├── Verify all critical variables present
  └── Record results

Phase 3: Source Code Verification (15 min)
  ├── Verify remote connectivity
  ├── Verify local clone integrity
  ├── Verify prompt file inventory
  └── Record results

Phase 4: Full DR Simulation (60-120 min)
  ├── See DR plan Section 11.2 for full procedure
  ├── Simulate: database failure, AI failure, or full outage
  ├── Time the recovery
  └── Record results

Phase 5: Documentation (30 min)
  ├── Complete DR drill report
  ├── Log action items
  ├── Update this document if procedures changed
  └── Update docs/operations/drill_log.md
```

### 10.3 Post-Test Actions

```
 1. Review DR drill report for improvement areas
 2. Create GitHub Issues for any action items
 3. Update backup scripts if needed
 4. Schedule next quarterly drill
 5. Celebrate a successful (or educational) drill
```

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-07-11 | Developer | Initial backup verification procedure — covers database, env vars, source code, and prompt files. Weekly/monthly/quarterly verification cycles with checklists. Restoration step-by-step for all asset types. Troubleshooting guide for common backup failures. Full DR test procedure for quarterly execution. |
