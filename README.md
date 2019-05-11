# aw-exist-connector
Uses ActivityWatcher to update Exist.io

## Uses
### ActivityWatch
Works in the background and collects activity data.
https://github.com/ActivityWatch

### Exist.io
Aggregates and displays personal information. 

## Works
Assumes that the ActivityWatch is running on a host. Every-so-often (cron 1h) checks for updates,
maps to "productivity" categories based on regex and sends total time to the Exist.

## WIP
WIP so much.