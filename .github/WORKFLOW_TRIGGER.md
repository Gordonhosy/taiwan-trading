# Reliable Data Update Trigger (Recommended)

GitHub's built-in `schedule:` cron is best-effort only and can be delayed or missed by hours (as you experienced).

The reliable way is to trigger this workflow via the GitHub API from an external cron service.

## Setup (cron-job.org - free)

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - "Generate new token (classic)"
   - Name: `taifex-data-updater`
   - Expiration: 90 days or longer
   - Scopes required: `repo` + `workflow`
   - Generate and copy the token (`ghp_...`)

2. Go to https://cron-job.org and create a free account.

3. Create a new Cron Job with these settings:

    **URL:**
    ```
    https://api.github.com/repos/Gordonhosy/taiwan-trading/actions/workflows/update-taifex-data.yml/dispatches
    ```

   **Method:** POST

    **Schedule:** 
    - Every weekday at 15:30 Taiwan time (recommended: give TAIFEX data ~20-30 min buffer after market close)
    - Set the cron service to **Asia/Taipei** timezone if possible.
    - Example cron (UTC): `30 7 * * 1-5` (15:30 TW)

   **Headers (add all three):**
   ```
   Accept: application/vnd.github+json
   Authorization: Bearer ghp_YOUR_TOKEN_HERE
   X-GitHub-Api-Version: 2022-11-28
   ```

   **Body (raw, type: JSON):**
   ```json
   {
     "ref": "main",
     "inputs": {
       "days": "7"
     }
   }
   ```

4. Save the job.

5. Test it manually from the cron service.

## How it works

- The external service calls GitHub at the exact time you configured.
- This triggers the "Update TAIFEX Data" workflow (same one used by schedule + manual).
- The script runs on GitHub's ubuntu runner and pushes the updated `data/taifex.db` + `data/last_update.txt`.
- Timing is reliable (unlike native GitHub schedule).

## Manual trigger (always available)

You can still go to the Actions tab → "Update TAIFEX Data" → "Run workflow".

## Local alternative (if you prefer)

If you want to run the updater on your own machine with Windows Task Scheduler (very precise), tell me and I'll create a small PowerShell script + setup instructions.

## Notes

- The token needs `workflow` scope so it can start workflows.
- Never commit the token anywhere.
- You can rotate the token anytime.
- The workflow still has the old schedule as a weak fallback.
