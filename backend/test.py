from util import _load_wp_model, calculate
import joblib

model = joblib.load("../ml/xgboost.joblib")
# period, seconds_remaining, home_score, away_score, point_diff, home_wins, home_losses, away_wins, away_losses, home_l10_wins, away_l10_wins
period = 1
seconds_remaining = 2880
home_score = 0
away_score = 0
point_diff = 0
home_wins = 30
home_losses = 20
away_wins = 25
away_losses = 25
home_l10_wins = 6
away_l10_wins = 4
y_proba = model.predict_proba([[period, seconds_remaining, home_score, away_score, point_diff, home_wins, home_losses, away_wins, away_losses, home_l10_wins, away_l10_wins]])
print(f"Home WP: {round(y_proba[0, 1] * 100, 2)}")
print(f"Away WP: {round(y_proba[0, 0] * 100, 2)}")