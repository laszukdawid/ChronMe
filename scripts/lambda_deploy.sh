AWS_LAMBDA_NAME=${AWS_LAMBDA_NAME}
AWS_PROFILE_NAME=${AWS_PROFILE_NAME}
zip_file=function_lambda.zip
cd ../dependencies
zip -r9 ../$zip_file .
cd ../src
zip -g ../$zip_file lambda_function.py chronme/*
cd ..
aws --profile $AWS_PROFILE_NAME lambda update-function-code \
    --function-name $AWS_LAMBDA_NAME \
    --zip-file fileb://./$zip_file

