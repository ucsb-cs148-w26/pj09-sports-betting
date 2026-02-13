from util import _load_wp_model, calculate
import joblib
import requests
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from scipy.interpolate import make_interp_spline
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("model", type=str, default="lr")
args = parser.parse_args()
model_name = args.model

# Match feature order/names the models were trained on (no raw lists -> no sklearn warning)
FEATURE_COLS = [
    "SECONDS_REMAINING", "HOME_SCORE", "AWAY_SCORE",
    "HOME_WINS", "HOME_LOSSES", "AWAY_WINS", "AWAY_LOSSES",
    "HOME_L10_WINS", "AWAY_L10_WINS",
]

_SEC_PER_QUARTER = 720

def parse_clock_to_seconds(clock: str | None) -> int:
    """Parse NBA clock like 'PT12M00.00S' to seconds left in the current period."""
    if not clock:
        return 0
    s = str(clock).strip()
    if s.startswith("PT") and s.endswith("S"):
        s = s[2:-1]
        minutes = 0
        seconds = 0
        if "M" in s:
            mins, rest = s.split("M", 1)
            minutes = int(mins) if mins.isdigit() else 0
            s = rest
        if s:
            try:
                seconds = int(float(s))
            except ValueError:
                seconds = 0
        return minutes * 60 + seconds
    return 0


def total_seconds_remaining_in_game(period: int, clock_sec: int) -> int:
    """Total seconds left in the game. Start of game = 2880 (4 * 720)."""
    if period <= 4:
        return (4 - period) * _SEC_PER_QUARTER + clock_sec
    return clock_sec  # OT: just seconds left in current OT period


def action_to_status(period: int, clock_sec: int) -> str:
    """Build status string for calculate(), e.g. '12:00 - 1st' or '5:00 - 4th'."""
    period_str = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}.get(period)
    if period_str is None:
        period_str = "OT" if period == 5 else f"{period - 4}OT"
    mins, secs = clock_sec // 60, clock_sec % 60
    return f"{mins}:{secs:02d} - {period_str}"

# warriors vs spurs tn 2/11
seconds_remaining = 2880
home_score = 0
away_score = 0
home_wins = 29
home_losses = 25
away_wins = 37
away_losses = 16
home_l10_wins = 4
away_l10_wins = 7

model_map = {
    "lr": "Logistic Regression",
    "xgboost": "XGBoost",
    "xgboost_calibrated": "XGBoost Calibrated",
    "random_forest_v1": "Random Forest",
    "nn": "Neural Network"
}

# pistons pacers oct 23 2024
url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0022500788.json"
data = requests.get(url).json()
pbp = data["game"]["actions"]
model = joblib.load(f"../ml/{model_name}.joblib")

REGULATION_SEC = 4 * _SEC_PER_QUARTER
times_sec = []
home_wps = []
prev_elapsed = -1
for action in pbp:
    clock_sec = parse_clock_to_seconds(action.get("clock"))
    period = int(action.get("period", 1))
    seconds_remaining = total_seconds_remaining_in_game(period, clock_sec)
    if period <= 4:
        elapsed = REGULATION_SEC - seconds_remaining
    else:
        elapsed = REGULATION_SEC + (period - 4) * 300 - clock_sec

    # skip same time actions for testing purposes
    if elapsed == prev_elapsed:
        continue

    home_score = int(action.get("scoreHome", 0) or 0)
    away_score = int(action.get("scoreAway", 0) or 0)
    home_wins = 0
    home_losses = 0
    away_wins = 0
    away_losses = 0
    home_l10_wins = 0
    away_l10_wins = 0
    X = pd.DataFrame(
        [[seconds_remaining, home_score, away_score, home_wins, home_losses, away_wins, away_losses, home_l10_wins, away_l10_wins]],
        columns=FEATURE_COLS,
    )
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X)
        home_p = y_proba[0, 1]
    else:
        home_p = float(model.predict(X, verbose=0).ravel()[0])
    times_sec.append(elapsed)
    home_wps.append(round(home_p * 100, 2))  
    prev_elapsed = elapsed

X_Y_Spline = make_interp_spline(times_sec, home_wps)
X_Spline = np.linspace(min(times_sec), max(times_sec), 500)
Y_Spline = X_Y_Spline(X_Spline)

fig, ax = plt.subplots()
ax.plot(X_Spline, Y_Spline, label="Home WP (%)", color="C0", linewidth=1.5)
ax.set_xlabel("Time (seconds from start)")
ax.set_ylabel("Win probability (%)")
ax.set_title("WP vs Time for Model: " + model_map[model_name])
ax.legend()
ax.set_xlim(0, max(times_sec))
ax.set_ylim(0, 100)
ax.set_yticks([0, 50, 100])
ax.axhline(50, color="gray", linestyle="--", alpha=0.5)

# Trace line: show y (win probability) when moving mouse over the plot
ann = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                  bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.9),
                  fontsize=9, verticalalignment="top")

def on_motion(event):
    if event.inaxes != ax or event.xdata is None:
        ann.set_visible(False)
        fig.canvas.draw_idle()
        return
    x = np.clip(event.xdata, X_Spline.min(), X_Spline.max())
    y = float(np.interp(x, X_Spline, Y_Spline))
    ann.xy = (x, y)
    ann.set_text(f"WP = {y:.1f}%")
    ann.set_visible(True)
    fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", on_motion)
plt.tight_layout()
plt.show()