# aw-exist-connector
Uses ActivityWatcher to update Exist.io

## Uses
### ActivityWatch
Works in the background and collects activity data.
https://github.com/ActivityWatch

### Exist.io
Aggregates and displays personal information. 
Assumes that connection token is export to env shell under `EXIST_AW_TOKEN`.

## Works
Assumes that the ActivityWatch is running on a host. Every-so-often (cron 1h) checks for updates,
maps to "productivity" categories based on regex and sends total time to the Exist.

## WIP
WIP so much.