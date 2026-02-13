# Win Probability Model

## Summary

Win probabilities are computed in `backend/util.py` and attached to each game record.

Output fields:
- `home_win_prob`
- `away_win_prob`

Current scale:
- Percentage scale from `0` to `100`.
- `away_win_prob = 100 - home_win_prob`.

## Runtime Behavior

### Final games
If status is `Final`:
- Home team gets `100` when `home_score >= away_score`, else `0`.
- Away team is the complement.

### In-progress games
If `ml/model.joblib` exists:
- Model features used:
  - `PERIOD`
  - `SECONDS_REMAINING`
  - `HOME_SCORE`
  - `AWAY_SCORE`
  - `POINT_DIFF`
- Probability comes from `predict_proba` and is converted to percent.

If model file is missing:
- Current fallback returns `0` for both teams on non-final games.

## Status Parsing

`parse_status(status: str)` maps status text to `(period, seconds_remaining)`.

Handled values include:
- `Pregame`, `Scheduled`
- `Q1 mm:ss`, `Q2 mm:ss`, `Q3 mm:ss`, `Q4 mm:ss`
- `Halftime`
- `Overtime`, `OT`, `2OT`, `3OT`, and optional OT clock values
- `Final`

Unknown formats currently return `(None, None)` and produce a `0,0` probability output in `calculate`.

## Contract Example

```json
{
  "home_win_prob": 63.2,
  "away_win_prob": 36.8
}
```

## Integration Notes

- Frontend should treat these values as percentages, not unit probabilities.
- During model-missing scenarios, non-final games can show both probabilities as `0`.
