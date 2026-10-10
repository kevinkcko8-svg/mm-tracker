# Even_is_Even — Murder Mystery hourly tracker

Uses the official Hypixel API (not scraping 25Karma). Records cumulative statistics once per scheduled run, as well as differences from the preceding sample.

## GitHub setup

1. Create a NEW GitHub repository (a dedicated one is recommended; don't add this to an existing Pages repo unless intended).
2. Upload `track.py`, `requirements.txt`, and the entire `.github/workflows/track.yml` path (keep folders).
3. Create a Hypixel Developer API key via https://developer.hypixel.net/ .
4. In your GitHub repository choose **Settings → Secrets and variables → Actions → New repository secret**. Name it `HYPIXEL_API_KEY` and paste the key as its value. Never commit or screenshot the key.
5. Under **Actions → Hourly Murder Mystery stats → Run workflow**, start the first collection manually.
6. After a successful run, the repository will contain `data/history.csv`, `totals.png`, and `changes.png`. The scheduled workflow runs around minute 17 of every UTC hour, but GitHub schedules may be delayed or occasionally skipped.

## Local run

```bash
pip install -r requirements.txt
# macOS / Linux:
export HYPIXEL_API_KEY='YOUR_KEY'
python track.py
# Windows PowerShell:
# $env:HYPIXEL_API_KEY='YOUR_KEY'; python track.py
```

## Output

- `data/history.csv` – historical observations and changes from previous observations.
- `totals.png` – trend of cumulative values.
- `changes.png` – changes between snapshots, **not guaranteed to represent exactly 60 minutes** if a run is delayed/skipped.
- Missing API fields are blank rather than guessed as zero.

These metrics come from the official Hypixel API's `stats.MurderMystery`. Mode-specific or differently named fields may require adjusting `STAT_KEYS` in `track.py`. History starts on first successful run; older hourly history cannot be reconstructed from a current total. Public repositories expose the tracked statistics, so choose a private repository if desired. GitHub Actions scheduled workflows require repository automation to remain enabled; delays and occasional skipped runs can occur.
