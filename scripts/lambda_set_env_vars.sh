aws lambda update-function-configuration \
    --function-name ${AWS_LAMBDA_NAME} \
    --environment Variables="{EXIST_TOKEN=${EXIST_TOKEN},AW_BUCKET=${AW_BUCKET}}"
