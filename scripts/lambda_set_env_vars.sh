aws lambda update-function-configuration \
    --function-name ${AWS_LAMBDA_NAME} \
    --environment Variables="{EXIST_AW_TOKEN=${EXIST_AW_TOKEN},AW_BUCKET=${AW_BUCKET}}"
