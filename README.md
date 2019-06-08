# aw-exist-connector
Uses ActivityWatcher to update Exist.io

### WIP?
WIP! (Work In Progress)

## Uses
### ActivityWatch
Works in the background and collects activity data.
https://github.com/ActivityWatch

### Exist.io
Aggregates and displays personal information. 
Assumes that connection token is export to env shell under `EXIST_TOKEN`.

## Works
Assumes that the ActivityWatch is running on a host. Every-so-often (cron 1h) checks for updates,
maps to "productivity" categories based on regex and sends total time to the Exist.

## Env Variables
```sh
export AWS_LAMBDA_NAME=
export AW_BUCKET=
export EXIST_TOKEN=
```

## AWS preparation
### IAM role
Required permissions:
* S3 list objects
* S3 get object
* S3 put object
* Lambda function deploy

### Lambda
It's configured to be in the same region as the S3 bucket. Lambda also has a trigger on any changes in the `$AW_BUCKET/data` path.

## FAQ
### Why it doesn't work?
I think so. But cannot guarnatee.

### Who wrote such a mess?
The Universe. In the beginning, i.e. reversing the time arrow and fastforward to the beginning, the Universe was a hot mess. And look what we have right now! Just wait. Unless you fear of the Entropy in which case, well, concious mess requires order, so that's not that.
