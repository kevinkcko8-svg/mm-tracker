# Murder Mystery Rival Tracker

Player: **Even_is_Even**. Rivals: **Anatellia**, **Sam**, **cinnmn**.

## What is tracked?
- Your cumulative Hypixel Murder Mystery wins, kills, deaths, games and coins every hour (UTC HH:17, subject to GitHub Actions scheduling delays).
- Rival snapshots every six hours (UTC 00:17, 06:17, 12:17, 18:17); manual runs also sample rivals.
- CSV history: `data/history.csv` and `data/rivals.csv`; **existing history is preserved**.
- Interactive dashboard: `index.html`, showing totals / growth and the latest 24-hour wins delta.
- GitHub Issue notifications **only when a rival switches from not leading to leading** in comparable 24-hour wins deltas. A baseline is established before any crossover alert is raised.

## Setup
1. Keep existing repository secret `HYPIXEL_API_KEY` in Settings → Secrets and variables → Actions. Do not paste the key publicly.
2. Under Actions → Hourly Murder Mystery stats → Run workflow, start one manual run to collect all rivals.
3. Under **Settings → Pages**, choose **Deploy from a branch**, branch **main**, folder **/(root)**, then Save. Once published, the dashboard URL should be:
   https://kevinkcko8-svg.github.io/mm-tracker/
4. To receive emails, enable notifications for Issues in GitHub notification settings. The workflow creates Issues, but GitHub may not automatically email you unless your settings allow it.

## How the comparison works
For each player, compare recorded win totals approximately 24 hours apart (within a 2-hour sampling tolerance). A missing history or stale rival snapshot is **not counted as zero**. Rivals need about 24 hours of samples before full comparisons work. A rival's 24-hour gain must become **strictly greater** than yours to create a crossover Issue; ties do not qualify. Scheduled workflows may run late or be skipped. The delta is an approximation to a 24-hour window, not a guaranteed continuous real-time rate.

The program uses the official Hypixel API, not 25Karma scraping. Opponent accounts with missing API data are skipped with a warning. It requires Issues to be enabled and Actions write permissions to create notification Issues.
