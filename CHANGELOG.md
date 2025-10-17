# Changelog

 ## Version 1.0.1 and 1.0.2
- Created all objects for the wrapper
- Created all initial functions

## Version 1.0.3
- Added losses to standings
- Updated documentation

## Version 1.0.6
- Fixed scoreboards bug caused by sleeper api giving None as custom pts

## Version 1.0.7
- Fixed KeyError in the get_team_score() method.

## Version 1.0.8 
2025-10-17

### Changed
- Refactored `League.get_scoreboards`:
  - Removed unnecessary parameters `score_type` and `week`.
  - Simplified score calculation by using the `points` field from the Sleeper API directly.
  - This improves performance and aligns better with Sleeper's current matchup structure.
  - Old signature: `get_scoreboards(self, rosters, matchups, users, score_type, week)`
  - New signature: `get_scoreboards(self, rosters, matchups, users)`

### Why
- `get_team_score` calculation was redundant since the `matchups` endpoint already provides `points`.
- Simplifies the public API of the function and makes it easier to use in projects consuming live or completed matchups.

### Example
```python
# Before
scoreboards = league.get_scoreboards(rosters, matchups, users, score_type="pts_half_ppr", week=5)

# Now
scoreboards = league.get_scoreboards(rosters, matchups, users)
