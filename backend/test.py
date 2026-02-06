from util import _load_wp_model, calculate

model = _load_wp_model()
home_wp, away_wp = calculate(100, 95, "Q4 5:38")
print(f"Home WP: {round(home_wp, 2)}")
print(f"Away WP: {round(away_wp, 2)}")