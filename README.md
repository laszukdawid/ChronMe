# aw-exist-connector
Uses [ActivityWatcher](https://activitywatch.net/) to update [Exist.io](https://exist.io/?referred_by=dawid).

## Needed
### ActivityWatch
ActivityWatch is your friendly spy. It tracks what you do but it doesn't tell anyone. Well, except you. But if you want to share the data with the Exist (below) then we need some data manipulation and currently that's done in your AWS account.

Just to mention, the Activtity Watch is a great, open source project. Check it out on the GitHub: https://github.com/ActivityWatch.

### Exist.io
A service that tries to make sense of your personal data. People behind the service are good. They're seem to be transparent with their work and what they do. Check out their [privacy policy](https://exist.io/privacy/).
In either case, for purpose of this project, they only want to know your productivity/neutral/distraction time. Further we assume that you have an account with them already and you know your `EXIST_TOKEN`. For more information on how to find your token please take a look in the Exist' doc on [Authentication overview](http://developer.exist.io/#authentication-overview).

## Workflow
We assume that the ActivityWatch is installed on all the machines that you want to monitor.
As part of this project we will add a timed job (cron) that every hour will upload recent data to your S3 bucket. On the successful upload the AWS Lambda is triggered which processes your data with some predefined (by you) config rules and updates data in the Exist.

### Env Variables
Since we don't know anything about your side you need to fill these yourself.
```sh
export AWS_LAMBDA_NAME={FILL_ME}
export AW_BUCKET={FILL_ME}
export EXIST_TOKEN={FILL_ME}
```

I suggest that you add these to your environment setting so that they're always there and you don't have to check/update each time. In my case, since I run Ubuntu, I've added these to the end of `~/.bashrc` file.

## Installation
First of all, once you checked out this package, make sure that you have all the depenedncies installed. Go to the root

Given that we need to add some dependnecies to the Lambda we will have to install these locally and then zip them. You'll see that there will be `dependencies` directory. It's created by `scripts/lambda_deploy.sh`. Do not delete it.

Add the `aw-exist-sync.sh` to the cron. To do so I'd suggest opening cron editor with 
```sh
> crontab -e
```
and add
```
0 * * * * {path_to_root}/scripts/aw-exist-sync.sh
```
Obviously, please update the `path_to_root` accordingly to your directory root.


## Running locally
Make sure that you have correct environment variables set and that you have all necessary Python packages.

From the root execute
```
> python src/main.py
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

# Questions?
The best way to ask questions is through the github [issues](https://github.com/laszukdawid/ChronMe/issues). Second best is to send me an email with some chocolates attached at [chronme@dawid.lasz.uk](mailto:chronme@dawid.lasz.uk).
