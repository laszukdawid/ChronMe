AWS_LAMBDA_NAME=${AWS_LAMBDA_NAME}
zip_file=function_lambda.zip
cd ..
zip $zip_file lambda_function.py src/*
aws lambda update-function-code \
    --function-name $AWAWS_LAMBDA_NAME \
    --zip-file fileb://./$zip_file
