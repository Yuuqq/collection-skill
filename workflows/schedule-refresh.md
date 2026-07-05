# Workflow: Schedule Periodic Refresh

<required_prerequisites>
Requires:
- `scripts/discover_repos.py` working (test once manually first).
- `scripts/build_catalog_md.py` working.
- GitHub auth available non-interactively: either `gh auth status` is logged in for the same user that the scheduler will run as, OR `GITHUB_TOKEN` is set in the scheduled environment.
</required_prerequisites>

<process>
## Step 1: Confirm Schedule with the User

Ask using AskUserQuestion (one round):
- **Frequency** — daily / weekly (default) / monthly
- **Day/time** — e.g., every Monday 03:00 local
- **Scope** — all categories (default) or a subset
- **Operating mode** — this is Windows (Task Scheduler) per environment

Default if user just says "yes schedule it": **weekly, Sunday 03:00, all categories**.

## Step 2: Generate the Refresh Script

Create `scripts/run_scheduled_refresh.sh` (Git Bash compatible) — or verify it already exists. It must:
1. `cd` to the skill root.
2. Set `GITHUB_TOKEN` if not already set (read from `gh auth token`).
3. Run `discover_repos.py` then `build_catalog_md.py`.
4. Append to `discovery-log.md` with `triggered by: scheduled`.
5. Exit non-zero on failure (so Task Scheduler can detect it).
6. **Not** require any interactive input.

See `templates/run_scheduled_refresh.sh.template` for the canonical version.

## Step 3: Install the OS-Level Trigger

**Windows Task Scheduler** (this environment is win32):

Generate the schtasks command. Example (weekly Sun 03:00):

```bash
schtasks /Create /TN "CollectionSkillRefresh" \
  /TR "\"C:\\Program Files\\Git\\bin\\bash.exe\" -lc 'cd /e/Research/collection-skill && bash scripts/run_scheduled_refresh.sh'" \
  /SC WEEKLY /D SUN /ST 03:00 /F
```

Notes for Windows:
- Use Git Bash's `bash.exe` to run the `.sh` script.
- The `/F` flag forces overwrite if a task with that name exists.
- Run under the current user (no password prompt); elevate only if needed.

**If on Linux/macOS instead** — write a crontab line:
```
0 3 * * 0  cd /path/to/collection-skill && bash scripts/run_scheduled_refresh.sh >> /tmp/collection-skill.cron.log 2>&1
```

## Step 4: Verify the Trigger

- Windows: `schtasks /Query /TN "CollectionSkillRefresh" /V /FO LIST` — confirm Next Run Time is set.
- Do NOT wait for the trigger to fire. Instead, do a one-shot manual run of `run_scheduled_refresh.sh` to confirm it works end-to-end in non-interactive mode.

## Step 5: Record and Report

Append a note to `references/discovery-log.md` under a `## Schedule` section:
```
- Installed: YYYY-MM-DD
- Frequency: weekly SUN 03:00
- Scope: all categories
- OS: Windows Task Scheduler (task name: CollectionSkillRefresh)
- To remove: schtasks /Delete /TN "CollectionSkillRefresh" /F
```

Report to the user:
- Schedule installed + next run time.
- How to check status (`schtasks /Query /TN CollectionSkillRefresh`).
- How to remove.
- Reminder: GitHub token must stay valid; if `gh auth` expires, refresh will fail silently (logged in discovery-log).
</process>

<success_criteria>
- A non-interactive refresh script exists and runs cleanly when invoked manually.
- An OS-level trigger (Task Scheduler / cron) is installed and shows a correct next-run time.
- The schedule is documented in `discovery-log.md` with removal instructions.
- A one-shot dry run completed without prompting for input.
</success_criteria>
