import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

PLAYER = os.getenv('MC_PLAYER', 'Even_is_Even')
KEY = os.getenv('HYPIXEL_API_KEY')
ROOT = Path(__file__).parent
CSV_PATH = ROOT / 'data' / 'history.csv'
FIELDS = ['timestamp_utc', 'wins', 'kills', 'deaths', 'games_played', 'coins', 'wins_delta', 'kills_delta', 'deaths_delta', 'games_played_delta', 'coins_delta']
METRICS = ['wins', 'kills', 'deaths', 'games_played', 'coins']
STAT_KEYS = {
    'wins': ['wins'],
    'kills': ['kills'],
    'deaths': ['deaths'],
    'games_played': ['games', 'games_played'],
    'coins': ['coins'],
}

def fetch_stats():
    if not KEY:
        raise RuntimeError('Missing HYPIXEL_API_KEY (configure a GitHub Actions secret).')
    r = requests.get(f'https://api.minecraftservices.com/minecraft/profile/lookup/name/{PLAYER}', timeout=25)
    r.raise_for_status()
    uid = r.json()['id']
    r = requests.get('https://api.hypixel.net/v2/player', params={'uuid': uid}, headers={'API-Key': KEY}, timeout=30)
    r.raise_for_status()
    payload = r.json()
    if not payload.get('success') or not payload.get('player'):
        raise RuntimeError(f'Unexpected Hypixel response: {payload.get("cause", "missing player")}')
    stats = (payload['player'].get('stats') or {}).get('MurderMystery')
    if stats is None:
        raise RuntimeError('No MurderMystery data found; not recording fake zeroes.')
    values = {}
    for metric, alternatives in STAT_KEYS.items():
        match = next((stats[key] for key in alternatives if isinstance(stats.get(key), (int, float)) and not isinstance(stats.get(key), bool)), None)
        values[metric] = int(match) if match is not None else ''
    if all(v == '' for v in values.values()):
        raise RuntimeError('No recognized stat fields; inspect API response field names.')
    return values

def main():
    snapshot = fetch_stats()
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if CSV_PATH.exists():
        with CSV_PATH.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    result = {'timestamp_utc': now, **snapshot}
    prev = rows[-1] if rows else None
    for key in METRICS:
        new = result[key]
        old = prev.get(key, '') if prev else ''
        result[key + '_delta'] = (int(new) - int(old)) if str(new) != '' and str(old) != '' else ''
    rows.append(result)
    with CSV_PATH.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f'Recorded {PLAYER} at {now}: {json.dumps(snapshot)}')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter
        dates = [datetime.fromisoformat(row['timestamp_utc']) for row in rows]
        labels = {'wins': 'Wins', 'kills': 'Kills', 'deaths': 'Deaths', 'games_played': 'Games played', 'coins': 'Coins'}
        for suffix, title in [('', 'Cumulative totals'), ('_delta', 'Change since previous snapshot')]:
            fig, ax = plt.subplots(figsize=(12, 5))
            plotted = 0
            for key in METRICS:
                values = [float(row[key + suffix]) if str(row.get(key + suffix, '')) != '' else float('nan') for row in rows]
                if any(v == v for v in values):
                    ax.plot(dates, values, marker='o', markersize=3, label=labels[key])
                    plotted += 1
            ax.set_title(f'{PLAYER} · Murder Mystery · {title}')
            ax.set_xlabel('Time (UTC)')
            ax.set_ylabel('Count')
            ax.grid(alpha=0.25)
            if plotted:
                ax.legend()
            ax.xaxis.set_major_formatter(DateFormatter('%m-%d %H:%M', tz=timezone.utc))
            fig.autofmt_xdate()
            fig.tight_layout()
            fig.savefig(ROOT / ('totals.png' if not suffix else 'changes.png'), dpi=160)
            plt.close(fig)
    except ImportError:
        print('matplotlib not installed; CSV still saved')

if __name__ == '__main__':
    main()
