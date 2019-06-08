AW_BUCKET=${AW_BUCKET}
aws s3 sync ../rules s3://$AW_BUCKET/rules --exclude "*" --include "*json"
